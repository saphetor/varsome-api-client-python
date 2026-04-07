import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pysam
import pytest

from varsome_api.models.slim.annotation import AnnotatedVariant as SlimAnnotatedVariant
from varsome_api.models.variant import AnnotatedVariant
from varsome_api.vcf import AnnotationResult
from varsome_api.vcf import BatchResult as VcfBatchResult
from varsome_api.vcf import VCFAnnotator

FIXTURES_DIR = Path(__file__).parent / "fixtures"
VARIANTS_VCF = str(FIXTURES_DIR / "variants.vcf")


class TestAnnotationResult:
    """Verify the ``AnnotationResult`` dataclass."""

    def test_stores_all_fields(self) -> None:
        result = AnnotationResult(
            total_variants=5,
            filtered_out_variants=[("v1", {"filtered_out": "reason"})],
            variants_with_errors=[("v2", {"error": "bad"})],
        )
        assert result.total_variants == 5
        assert len(result.filtered_out_variants) == 1
        assert len(result.variants_with_errors) == 1


class TestReadHeaderFromVcf:
    """Verify that ``_read_header_from_vcf`` reads only the header."""

    def test_returns_header_object(self) -> None:
        header = VCFAnnotator._read_header_from_vcf(VARIANTS_VCF)
        assert isinstance(header, pysam.VariantHeader)

    def test_header_contains_contigs(self) -> None:
        header = VCFAnnotator._read_header_from_vcf(VARIANTS_VCF)
        contig_names = list(header.contigs)
        assert "chr1" in contig_names

    def test_header_contains_info_fields(self) -> None:
        header = VCFAnnotator._read_header_from_vcf(VARIANTS_VCF)
        assert "KM" in header.info


class TestReadVariantsFromVcf:
    """Verify that ``_read_variants_from_vcf`` yields the expected variant tuples."""

    async def test_yields_all_variants(self) -> None:
        """All variants with ALT alleles should be yielded."""
        annotator = VCFAnnotator(max_variants_per_batch=100, max_requests=1)
        header = VCFAnnotator._read_header_from_vcf(VARIANTS_VCF)

        items = [
            item
            async for item in annotator._read_variants_from_vcf(VARIANTS_VCF, header)
        ]
        # The test VCF has 20 variants with ALT alleles
        assert len(items) == 20

    async def test_yields_valid_variant_strings(self) -> None:
        """Each variant string should be a valid chrom:pos:ref:alt string."""
        annotator = VCFAnnotator(max_variants_per_batch=100, max_requests=1)
        header = VCFAnnotator._read_header_from_vcf(VARIANTS_VCF)

        variant_strings = [
            variant_str
            async for variant_str, _ in annotator._read_variants_from_vcf(
                VARIANTS_VCF, header
            )
        ]
        for variant_str in variant_strings:
            parts = variant_str.split(":")
            assert len(parts) == 4, f"Invalid variant string: {variant_str}"
            assert parts[0], "Contig is empty"
            assert parts[1].isdigit(), "Position is not numeric"

    async def test_yields_variant_records(self) -> None:
        """Each yielded record should be a pysam VariantRecord."""
        annotator = VCFAnnotator(max_variants_per_batch=100, max_requests=1)
        header = VCFAnnotator._read_header_from_vcf(VARIANTS_VCF)

        records = [
            record
            async for _, record in annotator._read_variants_from_vcf(
                VARIANTS_VCF, header
            )
        ]
        for record in records:
            assert isinstance(record, pysam.VariantRecord)

    async def test_empty_vcf_yields_nothing(self, tmp_path: Path) -> None:
        """A VCF with only a header and no records should yield nothing."""
        vcf_path = tmp_path / "empty.vcf"
        header = pysam.VariantHeader()
        header.add_sample("SAMPLE1")
        header.contigs.add("1")
        with pysam.VariantFile(str(vcf_path), "w", header=header):
            pass  # write only the header

        annotator = VCFAnnotator(max_variants_per_batch=10, max_requests=1)
        read_header = VCFAnnotator._read_header_from_vcf(str(vcf_path))

        items = [
            item
            async for item in annotator._read_variants_from_vcf(
                str(vcf_path), read_header
            )
        ]
        assert not items


class TestConstructVariantFromRecord:
    """Verify variant string construction from VCF records."""

    def test_returns_variant_strings_for_records_with_alt(self) -> None:
        with pysam.VariantFile(VARIANTS_VCF, "r") as reader:
            for record in reader:
                result = VCFAnnotator._construct_variant_from_record(record)
                if record.alleles and len(record.alleles) >= 2:
                    alt = record.alleles[1]
                    if alt not in (None, "."):
                        assert len(result) >= 1

    def test_returns_empty_for_no_alleles(self) -> None:
        """Records with fewer than 2 alleles return an empty list."""
        mock_record = MagicMock()
        mock_record.alleles = ("A",)
        result = VCFAnnotator._construct_variant_from_record(mock_record)
        assert result == []

    @pytest.mark.parametrize("ref_allele", [None, ".", ""])
    def test_does_not_return_empty_for_no_ref(self, ref_allele) -> None:
        """Records with no reference allele should not be filtered out."""
        mock_record = MagicMock()
        mock_record.alleles = (ref_allele, "T")
        mock_record.contig = "1"
        mock_record.pos = 100
        result = VCFAnnotator._construct_variant_from_record(mock_record)
        assert len(result) == 1
        assert result[0][0] == "1:100::T"

    @pytest.mark.parametrize("alt_allele", [None, ".", ""])
    def test_does_not_return_empty_for_no_alt(self, alt_allele) -> None:
        """Records with no ALT allele should not be filtered out."""
        mock_record = MagicMock()
        mock_record.alleles = ("A", alt_allele)
        mock_record.contig = "1"
        mock_record.pos = 100
        result = VCFAnnotator._construct_variant_from_record(mock_record)
        assert len(result) == 1
        assert result[0][0] == "1:100:A:"

    def test_returns_empty_for_none_alleles(self) -> None:
        mock_record = MagicMock()
        mock_record.alleles = None
        result = VCFAnnotator._construct_variant_from_record(mock_record)
        assert result == []


class TestProcessRequest:
    """Verify batch result processing."""

    def test_counts_annotated_variants(self) -> None:
        annotator = VCFAnnotator(max_variants_per_batch=10)
        mock_writer = MagicMock()

        mock_record = MagicMock(spec=pysam.VariantRecord)
        mock_record.info = {}

        batch_result = VcfBatchResult(
            queries=["1:100:A:T"],
            records=[mock_record],
            response=[
                {
                    "original_variant": "1:100:A:T",
                    "chromosome": "1",
                    "pos": 100,
                    "ref": "A",
                    "alt": "T",
                }
            ],
        )

        count, filtered, errors = annotator._process_request(batch_result, mock_writer)
        assert count == 1
        assert filtered == []
        assert errors == []
        mock_writer.write.assert_called_once()

    def test_tracks_filtered_variants(self) -> None:
        annotator = VCFAnnotator(max_variants_per_batch=10)
        mock_writer = MagicMock()

        batch_result = VcfBatchResult(
            queries=["1:100:A:T"],
            records=[MagicMock(spec=pysam.VariantRecord)],
            response=[{"filtered_out": "Frequency less than 0.01"}],
        )

        count, filtered, errors = annotator._process_request(batch_result, mock_writer)
        assert count == 0
        assert len(filtered) == 1
        assert filtered[0][0] == "1:100:A:T"
        assert "filtered_out" in filtered[0][1]

    def test_tracks_errored_variants(self) -> None:
        annotator = VCFAnnotator(max_variants_per_batch=10)
        mock_writer = MagicMock()

        batch_result = VcfBatchResult(
            queries=["1:100:A:T"],
            records=[MagicMock(spec=pysam.VariantRecord)],
            response=[{"error": "Invalid variant"}],
        )

        count, filtered, errors = annotator._process_request(batch_result, mock_writer)
        assert count == 0
        assert filtered == []
        assert len(errors) == 1
        assert errors[0][0] == "1:100:A:T"

    def test_mixed_results(self) -> None:
        """A batch with success, filtered, and error entries."""
        annotator = VCFAnnotator(max_variants_per_batch=10)
        mock_writer = MagicMock()

        mock_record = MagicMock(spec=pysam.VariantRecord)
        mock_record.info = {}

        batch_result = VcfBatchResult(
            queries=["1:100:A:T", "1:200:G:C", "1:300:A:G"],
            records=[
                mock_record,
                MagicMock(spec=pysam.VariantRecord),
                MagicMock(spec=pysam.VariantRecord),
            ],
            response=[
                {
                    "original_variant": "1:100:A:T",
                    "chromosome": "1",
                    "pos": 100,
                    "ref": "A",
                    "alt": "T",
                },
                {"filtered_out": "reason"},
                {"error": "bad"},
            ],
        )

        count, filtered, errors = annotator._process_request(batch_result, mock_writer)
        assert count == 1
        assert len(filtered) == 1
        assert len(errors) == 1


async def _async_gen_from_list(items: list[Any]) -> Any:
    """Yield items from a list as an async generator."""
    for item in items:
        yield item


class TestAnnotateVariantsAndWriteToVcf:
    """Verify the annotation pipeline reads all variants then annotates."""

    async def test_read_variants_from_vcf_is_called(self, tmp_path: Path) -> None:
        """The pipeline should call _read_variants_from_vcf during annotation."""
        annotator = VCFAnnotator(
            api_key="test",
            max_variants_per_batch=2,
            max_requests=1,
        )
        output = str(tmp_path / "output.vcf")
        header = VCFAnnotator._read_header_from_vcf(VARIANTS_VCF)

        read_called = False
        original_method = annotator._read_variants_from_vcf

        def tracking_read(input_vcf_file: str, vcf_header: pysam.VariantHeader) -> Any:
            # Flag is set at call time (before iterating), not inside the body.
            nonlocal read_called
            read_called = True
            return original_method(input_vcf_file, vcf_header)

        with (
            patch.object(
                annotator,
                "_read_variants_from_vcf",
                tracking_read,
            ),
            patch.object(
                annotator,
                "abatch_lookup",
                return_value=_async_gen_from_list([]),
            ),
        ):
            await annotator._annotate_variants_and_write_to_vcf(
                VARIANTS_VCF, header, output
            )

        assert read_called

    async def test_returns_annotated_count(self, tmp_path: Path) -> None:
        """The method returns a 3-tuple of (annotated_count, filtered, errors)."""
        annotator = VCFAnnotator(
            api_key="test",
            max_variants_per_batch=100,
            max_requests=1,
        )
        output = str(tmp_path / "output.vcf")
        header = VCFAnnotator._read_header_from_vcf(VARIANTS_VCF)

        mock_batch_result = VcfBatchResult(queries=[], records=[], response=[])

        with patch.object(
            annotator,
            "abatch_lookup",
            return_value=_async_gen_from_list([mock_batch_result]),
        ):
            total_annotated, filtered, errors = (
                await annotator._annotate_variants_and_write_to_vcf(
                    VARIANTS_VCF, header, output
                )
            )

        assert total_annotated == 0  # mock returns empty batches
        assert filtered == []
        assert errors == []

    async def test_default_output_file_name(self, tmp_path: Path) -> None:
        """When output_vcf_file is None, it defaults to input + .annotated.vcf."""
        # Create a simple VCF in tmp_path so the annotated output goes there too
        vcf_path = tmp_path / "test.vcf"
        header = pysam.VariantHeader()
        header.add_sample("S1")
        header.contigs.add("1")
        with pysam.VariantFile(str(vcf_path), "w", header=header):
            pass

        annotator = VCFAnnotator(
            api_key="test",
            max_variants_per_batch=100,
            max_requests=1,
        )
        read_header = VCFAnnotator._read_header_from_vcf(str(vcf_path))

        with patch.object(
            annotator,
            "abatch_lookup",
            return_value=_async_gen_from_list([]),
        ):
            await annotator._annotate_variants_and_write_to_vcf(
                str(vcf_path), read_header, None
            )

        expected_output = f"{str(vcf_path)}.annotated.vcf"
        assert os.path.isfile(expected_output)

    async def test_passes_all_variant_keys_to_batch_lookup(
        self, tmp_path: Path
    ) -> None:
        """All variant keys from _read_variants_from_vcf are sent to abatch_lookup."""
        annotator = VCFAnnotator(
            api_key="test",
            max_variants_per_batch=2,
            max_requests=1,
        )
        output = str(tmp_path / "output.vcf")
        header = VCFAnnotator._read_header_from_vcf(VARIANTS_VCF)

        captured_variants: list[str] = []

        async def mock_abatch_lookup(variants: Any, **kwargs: Any) -> Any:
            # Consume the async generator to capture the variant strings
            async for variant_str, _record in variants:
                captured_variants.append(variant_str)
            if False:
                yield  # make this an async generator

        with patch.object(annotator, "abatch_lookup", mock_abatch_lookup):
            await annotator._annotate_variants_and_write_to_vcf(
                VARIANTS_VCF, header, output
            )

        # All 20 variants should have been passed through the generator
        assert len(captured_variants) == 20


class TestAannotate:
    """Verify the public async annotation entry point."""

    async def test_raises_for_missing_file(self) -> None:
        annotator = VCFAnnotator(api_key="test")
        with pytest.raises(FileNotFoundError):
            await annotator.aannotate("/nonexistent/file.vcf")

    async def test_returns_annotation_result(self, tmp_path: Path) -> None:
        """End-to-end: reads file, calls API, returns AnnotationResult."""
        annotator = VCFAnnotator(
            api_key="test",
            max_variants_per_batch=100,
            max_requests=1,
        )
        output = str(tmp_path / "annotated.vcf")

        mock_batch_result = VcfBatchResult(queries=[], records=[], response=[])

        with patch.object(
            annotator,
            "abatch_lookup",
            return_value=_async_gen_from_list([mock_batch_result]),
        ):
            result = await annotator.aannotate(VARIANTS_VCF, output)

        assert isinstance(result, AnnotationResult)
        assert result.total_variants == 0
        assert result.filtered_out_variants == []
        assert result.variants_with_errors == []

    async def test_all_variants_passed_to_batch_lookup(self, tmp_path) -> None:
        """Verify all variants from the VCF are processed through abatch_lookup."""
        annotator = VCFAnnotator(
            api_key="test",
            max_variants_per_batch=3,
            max_requests=2,
        )

        captured_variants: list[str] = []
        output = str(tmp_path / "annotated.vcf")

        async def mock_abatch_lookup(variants: Any, **kwargs: Any) -> Any:
            async for variant_str, _record in variants:
                captured_variants.append(variant_str)
            if False:
                yield  # make this an async generator

        with patch.object(annotator, "abatch_lookup", mock_abatch_lookup):
            await annotator.aannotate(VARIANTS_VCF, output)

        # All 20 variants should have been passed through the generator
        assert len(captured_variants) == 20


class TestAnnotateSync:
    """Verify the synchronous ``annotate`` wrapper."""

    def test_sync_wrapper_exists(self) -> None:
        """The sync wrapper should be a callable attribute."""
        assert callable(VCFAnnotator.annotate)

    def test_sync_raises_for_missing_file(self) -> None:
        annotator = VCFAnnotator(api_key="test")
        with pytest.raises(FileNotFoundError):
            annotator.annotate("/nonexistent/file.vcf")


class TestAddVcfHeaderInfo:
    """Verify that ``add_vcf_header_info`` adds expected INFO fields."""

    def test_adds_required_info_fields(self) -> None:
        annotator = VCFAnnotator(max_variants_per_batch=10)
        header = pysam.VariantHeader()
        annotator.add_vcf_header_info(header)
        expected_fields = [
            "genes",
            "gnomad_exomes_AF",
            "gnomad_genomes_AF",
            "acmg_verdict",
            "acmg_rules",
            "original_variant",
        ]
        for field in expected_fields:
            assert field in header.info, f"Missing INFO field: {field}"


class TestVariantModel:
    """Verify the ``variant_model`` class attribute extension point."""

    def test_default_variant_model_is_slim(self) -> None:
        assert VCFAnnotator.variant_model is SlimAnnotatedVariant

    def test_can_override_to_full_annotated_variant(self) -> None:
        """Subclass can switch back to the full model for more fields."""

        class FullAnnotator(VCFAnnotator):
            variant_model = AnnotatedVariant

        assert FullAnnotator.variant_model is AnnotatedVariant

    def test_custom_variant_model_is_used_for_deserialization(self) -> None:
        """A subclass can set variant_model to a slim Pydantic model."""
        from pydantic import BaseModel, ConfigDict

        class SlimVariant(BaseModel):
            model_config = ConfigDict(extra="ignore")
            original_variant: str | None = None
            custom_score: float | None = None
            chromosome: str | None = None
            pos: int | None = None
            ref: str | None = None
            alt: str | None = None

        class SlimAnnotator(VCFAnnotator):
            variant_model = SlimVariant

            def annotate_record(self, record, variant_result, original_variant):
                if variant_result.custom_score is not None:
                    record.info["custom_score"] = variant_result.custom_score

            def add_vcf_header_info(self, header):
                header.info.add("custom_score", "1", "Float", "Custom score")

        annotator = SlimAnnotator(max_variants_per_batch=10)
        mock_writer = MagicMock()
        mock_record = MagicMock(spec=pysam.VariantRecord)
        mock_record.info = {}

        batch_result = VcfBatchResult(
            queries=["1:100:A:T"],
            records=[mock_record],
            response=[
                {
                    "custom_score": 0.95,
                    "original_variant": "1:100:A:T",
                    "chromosome": "1",
                    "pos": 100,
                    "ref": "A",
                    "alt": "T",
                    "gnomad_exomes": [{"version": "4.1", "af": 0.001}],
                    "dbnsfp": [{"version": "4.9a"}],
                }
            ],
        )

        count, filtered, errors = annotator._process_request(batch_result, mock_writer)
        assert count == 1
        mock_writer.write.assert_called_once()
        # Verify the slim model was used (extra fields were ignored).
        assert not hasattr(
            SlimVariant(
                original_variant="x",
                gnomad_exomes=[{"version": "4.1"}],  # type: ignore[call-arg]
            ),
            "gnomad_exomes",
        )
