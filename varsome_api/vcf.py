from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any, AsyncGenerator

import aiohttp
from pydantic import BaseModel

from varsome_api._sync import sync_wrapper
from varsome_api.client import BatchResult as _BaseBatchResult
from varsome_api.client import VarSomeAPIClient
from varsome_api.constants import DEFAULT_REF_GENOME, RefGenome
from varsome_api.exceptions import VarSomeAPIException
from varsome_api.models.slim.annotation import AnnotatedVariant as SlimAnnotatedVariant
from varsome_api.models.variant import AnnotatedVariant

try:
    import pysam

    _PYSAM_AVAILABLE = True
except ImportError:
    pysam = None  # type: ignore[assignment]
    _PYSAM_AVAILABLE = False


def _require_pysam() -> None:
    """Raise ImportError with installation instructions if pysam is not installed.

    Raises:
        ImportError: When pysam is not present in the current environment,
            with instructions for installing the ``vcf`` extra.
    """
    if not _PYSAM_AVAILABLE:
        raise ImportError(
            "pysam is required for VCF support but is not installed.\n"
            "Install it with: pip install 'varsome_api[vcf]'\n\n"
            "See the developer guide."
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class AnnotationResult:
    """Summary statistics returned after a VCF annotation run.

    Attributes:
        total_variants: Number of variants successfully annotated and
            written to the output VCF.
        filtered_out_variants: Pairs of ``(variant_string, response_dict)``
            for variants filtered out by the API.  Each response dict
            contains at least a ``"filtered_out"`` key with a reason string.
        variants_with_errors: Pairs of ``(variant_string, response_dict)``
            for variants that encountered annotation errors.  Each response
            dict contains at least an ``"error"`` key.
    """

    total_variants: int
    filtered_out_variants: list[tuple[str, dict[str, Any]]]
    variants_with_errors: list[tuple[str, dict[str, Any]]]


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchResult(_BaseBatchResult):
    """Extends :class:`~varsome_api.client.BatchResult` with VCF records.

    Attributes:
        records: The ``pysam.VariantRecord`` objects corresponding to each
            query, aligned by index with *queries* and *response*.
    """

    records: list[pysam.VariantRecord]


class VCFAnnotator(VarSomeAPIClient):
    """Annotate a VCF file using the VarSome API.

    Reads an input VCF, sends variants in batches to the API, and writes
    an annotated VCF with the results.

    Three class-level extension points control the annotation pipeline:

    ``variant_model``
        The Pydantic model used to deserialise each API response dict.
        Defaults to
        :class:`~varsome_api.models.slim.annotation.AnnotatedVariant`,
        which declares only the fields consumed by the default
        ``annotate_record`` implementation.  Swap in the full
        :class:`~varsome_api.models.variant.AnnotatedVariant` if you
        need access to the complete API response, or use your own
        Pydantic model for a custom field selection.

    ``annotate_record``
        Called once per variant to write INFO fields into the
        ``pysam.VariantRecord``.  The base implementation writes a
        default set of annotations.  Override this to customize which
        fields appear in the output VCF.

    ``add_vcf_header_info``
        Called once before annotation begins to register INFO header
        lines.  Must declare every INFO key that ``annotate_record``
        writes.

    .. note::

       If you override ``annotate_record`` to read additional API
       fields that are **not** present on the default slim
       ``AnnotatedVariant``, you must also set ``variant_model``
       to a model that includes those fields — either the full
       ``AnnotatedVariant`` or a custom slim model of your own.
    """

    variant_model: type[BaseModel] = SlimAnnotatedVariant

    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
        max_variants_per_batch: int = 100,
        ref_genome: RefGenome = DEFAULT_REF_GENOME,
        request_parameters: dict[str, Any] | None = None,
        max_requests: int = 1,
    ):
        """Initialise the VCF annotator.

        Args:
            api_key: Optional API authentication token.
            api_url: Optional custom API base URL.
            max_variants_per_batch: Number of variants per batch request.
            ref_genome: Reference genome, either ``"hg19"`` or ``"hg38"``.
            request_parameters: Optional dict of additional API query
                parameters (e.g. ``{"add-all-data": "1"}``).
            max_requests: Maximum number of concurrent API requests.
        """
        super().__init__(api_key, api_url, max_variants_per_batch)
        _require_pysam()
        self.ref_genome = ref_genome
        self.request_parameters = request_parameters
        self.max_requests = max_requests or 1

    def _process_request(
        self,
        batch_result: BatchResult,
        writer: pysam.VariantFile,
    ) -> tuple[int, list[tuple[str, dict[str, Any]]], list[tuple[str, dict[str, Any]]]]:
        """Process a batch result and write annotated records to the output VCF.

        Iterates over each query in *batch_result* by index, skips
        filtered-out or errored responses, deserialises valid responses via
        ``self.variant_model``, and delegates to ``annotate_record`` before
        writing the record.

        Args:
            batch_result: A ``BatchResult`` whose ``queries``, ``records``,
                and ``response`` lists are aligned by index.
            writer: An open ``pysam.VariantFile`` in write mode.

        Returns:
            A 3-tuple ``(annotated_count, filtered_variants, errored_variants)``
            where *filtered_variants* and *errored_variants* are lists of
            ``(variant_string, response_dict)`` tuples for this batch.
        """
        annotated_count = 0
        filtered_variants: list[tuple[str, dict[str, Any]]] = []
        errored_variants: list[tuple[str, dict[str, Any]]] = []
        for idx, variant in enumerate(batch_result.queries):
            annotated_variant = batch_result.response[idx]
            vcf_record = batch_result.records[idx]
            if "filtered_out" in annotated_variant:
                filtered_variants.append((variant, annotated_variant))
                continue
            if "error" in annotated_variant:
                errored_variants.append((variant, annotated_variant))
                continue
            variant_result = self.variant_model(**annotated_variant)
            self.annotate_record(
                vcf_record, variant_result, variant_result.original_variant
            )
            writer.write(vcf_record)
            annotated_count += 1
        return annotated_count, filtered_variants, errored_variants

    def annotate_record(
        self,
        record: pysam.VariantRecord,
        variant_result: AnnotatedVariant,
        original_variant: str,
    ) -> None:
        """Annotate a VCF record with API result data.

        This base implementation adds a default set of annotations
        (genes, gnomAD frequencies, ACMG verdict/rules).
        Override this method to customize which fields appear in your
        output VCF.

        Values that are ``None`` are omitted from the INFO field to avoid
        writing invalid VCF entries.  ``ref``, ``alts``, and ``pos`` are
        only updated when the API returns non-None values.

        Args:
            record: The ``pysam.VariantRecord`` to annotate in-place.
            variant_result: A variant model instance (``SlimAnnotatedVariant``
                by default).
            original_variant: The variant string as sent in the request.
        """
        scalar_info: dict[str, Any] = {
            "gnomad_exomes_AF": variant_result.gnomad_exomes_af,
            "gnomad_genomes_AF": variant_result.gnomad_genomes_af,
            "acmg_verdict": variant_result.acmg_verdict,
            "acmg_rules": variant_result.acmg_rules,
            "genes": variant_result.genes,
            "original_variant": original_variant,
        }
        for key, value in scalar_info.items():
            if value is not None:
                record.info[key] = value
        record.pos = variant_result.pos
        ref_allele = variant_result.ref or "."
        alt_allele = variant_result.alt or "."
        record.alleles = (ref_allele, alt_allele) if alt_allele else (ref_allele,)
        record.id = ";".join(variant_result.rs_ids) if variant_result.rs_ids else None

    def add_vcf_header_info(self, header: pysam.VariantHeader) -> None:
        """Add INFO header lines for the annotated fields.

        This base implementation adds headers for the default annotations
        written by ``annotate_record``. Override this method to match your
        custom ``annotate_record`` implementation.

        Args:
            header: The ``pysam.VariantHeader`` to add INFO lines to.
        """
        header.info.add("genes", ".", "String", "Genes related to this variant")
        header.info.add(
            "gnomad_exomes_AF",
            "1",
            "Float",
            "GnomAD exomes allele frequency value",
        )
        header.info.add(
            "gnomad_genomes_AF",
            "1",
            "Float",
            "GnomAD genomes allele frequency value",
        )
        header.info.add("acmg_verdict", "1", "String", "ACMG Classification Verdict")
        header.info.add("acmg_rules", ".", "String", "ACMG Classifications")
        header.info.add(
            "original_variant",
            "1",
            "String",
            "Variant as present in the request",
        )

    @staticmethod
    def _construct_variant_from_record(
        record: pysam.VariantRecord,
    ) -> list[tuple[str, pysam.VariantRecord]]:
        """Construct variant strings from a VCF record.

        For multi-allelic records, returns one ``(variant_string, record)``
        pair per supported ALT allele.

        Args:
            record: A ``pysam.VariantRecord`` object.

        Returns:
            A list of ``(variant_string, record)`` tuples for every
            supported ALT allele, or an empty list when none are present.
        """
        alleles = record.alleles
        if alleles is None or len(alleles) < 2:
            return []

        ref = alleles[0] if alleles[0] not in (None, ".") else ""

        results: list[tuple[str, pysam.VariantRecord]] = []
        for alt in alleles[1:]:
            alt_value = alt if alt not in (None, ".") else ""
            results.append(
                (
                    f"{record.contig}:{record.pos}:{ref}:{alt_value}",
                    record.copy(),
                )
            )
        return results

    @staticmethod
    def _read_header_from_vcf(
        input_vcf_file: str,
    ) -> pysam.VariantHeader:
        """Read only the header from a VCF file without loading records.

        Args:
            input_vcf_file: Path to the input VCF file.

        Returns:
            A copy of the VCF header.
        """
        with pysam.VariantFile(input_vcf_file, "r") as reader:
            return reader.header.copy()

    async def _read_variants_from_vcf(
        self,
        input_vcf_file: str,
        vcf_header: pysam.VariantHeader,
    ) -> AsyncGenerator[tuple[str, pysam.VariantRecord], Any]:
        with pysam.VariantFile(input_vcf_file, "r") as reader:
            for record in reader:
                record.translate(vcf_header)
                for variant_str, rec in self._construct_variant_from_record(record):
                    yield variant_str, rec

    async def _batch_producer(
        self,
        variants: AsyncGenerator[tuple[str, pysam.VariantRecord], Any],
        queue: asyncio.Queue,
    ) -> None:
        batch = []
        async for variant_str, record in variants:
            batch.append((variant_str, record))
            if len(batch) >= self.max_variants_per_batch:
                await queue.put(batch)
                batch = []
        if batch:
            await queue.put(batch)
        await queue.put(None)

    async def _batch_worker(
        self,
        session: aiohttp.ClientSession,
        request_queue: asyncio.Queue,
        result_queue: asyncio.Queue,
        url: str,
        params: dict[str, Any] | None,
        batch_key: str,
    ) -> None:
        """Consume batches of variants from the request
        queue and send them to the API."""
        while True:
            batch = await request_queue.get()
            if batch is None:
                request_queue.task_done()
                break
            variant_reprs, records = zip(*batch)
            try:
                response = await self._make_request(
                    session,
                    path=url,
                    method="POST",
                    params=params,
                    json={batch_key: variant_reprs},
                    headers={"Content-Type": "application/json"},
                )
                await result_queue.put(
                    BatchResult(
                        queries=variant_reprs, records=records, response=response
                    )
                )
            except VarSomeAPIException as e:
                await result_queue.put(e)
            finally:
                request_queue.task_done()

    async def _annotate_variants_and_write_to_vcf(
        self,
        input_vcf_file: str,
        vcf_header: pysam.VariantHeader,
        output_vcf_file: str | None = None,
    ) -> tuple[int, list[tuple[str, dict[str, Any]]], list[tuple[str, dict[str, Any]]]]:
        """Read all variants, annotate them via the API, and write a VCF.

        Args:
            input_vcf_file: Path to the input VCF file.
            vcf_header: The VCF header to use for the output file.
            output_vcf_file: Optional explicit output file path.  When
                *None*, defaults to ``{input_vcf_file}.annotated.vcf``.

        Returns:
            A 3-tuple ``(total_annotated, filtered_variants, errored_variants)``
            where *filtered_variants* and *errored_variants* are accumulated
            lists of ``(variant_string, response_dict)`` tuples across all
            batches.
        """
        self.add_vcf_header_info(vcf_header)
        if output_vcf_file is None:
            output_vcf_file = f"{input_vcf_file}.annotated.vcf"

        total_annotated = 0
        all_filtered: list[tuple[str, dict[str, Any]]] = []
        all_errors: list[tuple[str, dict[str, Any]]] = []

        with pysam.VariantFile(output_vcf_file, "w", header=vcf_header) as writer:
            async for batch_result in self.abatch_lookup(
                self._read_variants_from_vcf(input_vcf_file, vcf_header),
                params=self.request_parameters,
                ref_genome=self.ref_genome,
                max_requests=self.max_requests,
            ):
                annotated, filtered, errors = self._process_request(
                    batch_result,
                    writer,
                )
                total_annotated += annotated
                all_filtered.extend(filtered)
                all_errors.extend(errors)

        return total_annotated, all_filtered, all_errors

    async def aannotate(
        self,
        input_vcf_file: str,
        output_vcf_file: str | None = None,
    ) -> AnnotationResult:
        """Asynchronously annotate a VCF file and write the results.

        Variants are streamed from the input VCF and sent to the API in
        concurrent batches.

        Args:
            input_vcf_file: Path to the input VCF file.
            output_vcf_file: Path to the output VCF file. Defaults to
                ``{input_vcf_file}.annotated.vcf``.

        Returns:
            An ``AnnotationResult`` with counts of annotated, filtered-out,
            and errored variants.

        Raises:
            FileNotFoundError: If *input_vcf_file* does not exist.
        """
        if not os.path.isfile(input_vcf_file):
            raise FileNotFoundError(f"{input_vcf_file} does not exist")
        header = self._read_header_from_vcf(input_vcf_file)
        total_annotated, filtered_variants, errored_variants = (
            await self._annotate_variants_and_write_to_vcf(
                input_vcf_file, header, output_vcf_file
            )
        )
        return AnnotationResult(
            total_variants=total_annotated,
            filtered_out_variants=filtered_variants,
            variants_with_errors=errored_variants,
        )

    annotate = sync_wrapper(aannotate)
