import json
from pathlib import Path
from typing import Any

import pytest

from varsome_api.models.slim.annotation import AnnotatedVariant as SlimAnnotatedVariant
from varsome_api.models.variant import AnnotatedVariant

BASE_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = BASE_DIR / "fixtures"
GERMLINE_FIXTURE = FIXTURES_DIR / "example_response_germline.json"
AMP_FIXTURE = FIXTURES_DIR / "example_response_amp.json"


@pytest.fixture(scope="module")
def germline_data() -> dict[str, Any]:
    """Load the germline example response as a raw dict."""
    with GERMLINE_FIXTURE.open() as f:
        return json.load(f)


@pytest.fixture(scope="module")
def amp_data() -> dict[str, Any]:
    """Load the AMP example response as a raw dict."""
    with AMP_FIXTURE.open() as f:
        return json.load(f)


@pytest.fixture(scope="module")
def germline_variant(germline_data: dict[str, Any]) -> AnnotatedVariant:
    """Deserialize the germline fixture into an AnnotatedVariant."""
    return AnnotatedVariant(**germline_data)


@pytest.fixture(scope="module")
def amp_variant(amp_data: dict[str, Any]) -> AnnotatedVariant:
    """Deserialize the AMP fixture into an AnnotatedVariant."""
    return AnnotatedVariant(**amp_data)


class TestDeserialization:
    """Verify that example responses can be completely deserialized."""

    def test_germline_response_deserializes(
        self, germline_variant: AnnotatedVariant
    ) -> None:
        assert germline_variant is not None

    def test_amp_response_deserializes(self, amp_variant: AnnotatedVariant) -> None:
        assert amp_variant is not None

    def test_empty_dict_produces_default_variant(self) -> None:
        """An empty dict should produce a valid instance with all None fields."""
        v = AnnotatedVariant()
        assert v.chromosome is None
        assert v.pos is None

    def test_extra_fields_accepted(self) -> None:
        """Unknown keys must not cause a validation error."""
        v = AnnotatedVariant(
            chromosome="chr1",
            some_future_database=[{"version": "1.0", "score": 42}],
        )
        assert v.chromosome == "chr1"
        assert v.some_future_database == [{"version": "1.0", "score": 42}]


class TestCoreFields:
    """Check that core fields are parsed from both fixtures."""

    @pytest.mark.parametrize("fixture", ["germline_variant", "amp_variant"])
    def test_chromosome(self, fixture: str, request: pytest.FixtureRequest) -> None:
        v: AnnotatedVariant = request.getfixturevalue(fixture)
        assert v.chromosome == "chr7"

    @pytest.mark.parametrize("fixture", ["germline_variant", "amp_variant"])
    def test_pos(self, fixture: str, request: pytest.FixtureRequest) -> None:
        v: AnnotatedVariant = request.getfixturevalue(fixture)
        assert v.pos == 140453136

    @pytest.mark.parametrize("fixture", ["germline_variant", "amp_variant"])
    def test_ref_alt(self, fixture: str, request: pytest.FixtureRequest) -> None:
        v: AnnotatedVariant = request.getfixturevalue(fixture)
        assert v.ref == "A"
        assert v.alt == "T"

    @pytest.mark.parametrize("fixture", ["germline_variant", "amp_variant"])
    def test_variant_type(self, fixture: str, request: pytest.FixtureRequest) -> None:
        v: AnnotatedVariant = request.getfixturevalue(fixture)
        assert v.variant_type == "SNV"

    @pytest.mark.parametrize("fixture", ["germline_variant", "amp_variant"])
    def test_cytobands(self, fixture: str, request: pytest.FixtureRequest) -> None:
        v: AnnotatedVariant = request.getfixturevalue(fixture)
        assert v.cytobands == "7q34"


class TestConvenienceProperties:
    """Verify the computed helper properties on AnnotatedVariant."""

    def test_genes(self, germline_variant: AnnotatedVariant) -> None:
        assert sorted(germline_variant.genes) == ["BRAF"]

    def test_refseq_genes_not_empty(self, germline_variant: AnnotatedVariant) -> None:
        assert len(germline_variant.refseq_genes) > 0
        assert all(g == "BRAF" for g in germline_variant.refseq_genes)

    def test_ensembl_genes_not_empty(self, germline_variant: AnnotatedVariant) -> None:
        assert len(germline_variant.ensembl_genes) > 0
        assert all(g == "BRAF" for g in germline_variant.ensembl_genes)

    def test_rs_ids(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.rs_ids == ["rs113488022"]

    def test_gnomad_exomes_af(self, germline_variant: AnnotatedVariant) -> None:
        af = germline_variant.gnomad_exomes_af
        assert af is not None
        assert af > 0

    def test_gnomad_exomes_an(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.gnomad_exomes_an == 251260

    def test_gnomad_genomes_af_none_when_absent(
        self, germline_variant: AnnotatedVariant
    ) -> None:
        assert germline_variant.gnomad_genomes_af is None

    def test_gnomad_genomes_an_none_when_absent(
        self, germline_variant: AnnotatedVariant
    ) -> None:
        assert germline_variant.gnomad_genomes_an is None

    def test_acmg_verdict(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.acmg_verdict == "Pathogenic"

    def test_acmg_rules(self, germline_variant: AnnotatedVariant) -> None:
        rules = germline_variant.acmg_rules
        assert rules is not None
        assert "PS3" in rules
        assert "PM1" in rules


class TestGermlineDataSources:
    """Verify presence and basic structure of data sources in the germline fixture."""

    def test_regions_present(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.regions is not None

    def test_refseq_transcripts(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.refseq_transcripts is not None
        assert len(germline_variant.refseq_transcripts) == 1

    def test_ensembl_transcripts(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.ensembl_transcripts is not None
        assert len(germline_variant.ensembl_transcripts) == 1

    def test_gnomad_exomes(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.gnomad_exomes is not None
        assert len(germline_variant.gnomad_exomes) == 1

    def test_ncbi_dbsnp(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.ncbi_dbsnp is not None
        assert len(germline_variant.ncbi_dbsnp) > 0

    def test_ncbi_clinvar2(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.ncbi_clinvar2 is not None
        assert len(germline_variant.ncbi_clinvar2) > 0

    def test_dbnsfp(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.dbnsfp is not None
        assert len(germline_variant.dbnsfp) > 0

    def test_acmg_annotation(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.acmg_annotation is not None
        assert germline_variant.acmg_annotation.verdict is not None

    def test_alpha_missense(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.alpha_missense is not None
        assert len(germline_variant.alpha_missense) > 0

    def test_cadd(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.cadd is not None
        assert len(germline_variant.cadd) > 0

    def test_pharmgkb(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.pharmgkb is not None
        assert len(germline_variant.pharmgkb) > 0

    def test_publications(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.publications is not None

    def test_saphetor_known_pathogenicity(
        self, germline_variant: AnnotatedVariant
    ) -> None:
        assert germline_variant.saphetor_known_pathogenicity is not None
        assert len(germline_variant.saphetor_known_pathogenicity) > 0

    def test_cancer_hotspots(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.cancer_hotspots is not None
        assert len(germline_variant.cancer_hotspots) > 0

    def test_cbio_portal(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.cbio_portal is not None
        assert len(germline_variant.cbio_portal) > 0

    def test_jax_ckb(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.jax_ckb is not None
        assert len(germline_variant.jax_ckb) > 0

    def test_lumc_lovd(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.lumc_lovd is not None
        assert len(germline_variant.lumc_lovd) > 0

    def test_wustl_civic(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.wustl_civic is not None
        assert len(germline_variant.wustl_civic) > 0

    def test_sanger_cosmic_licensed(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.sanger_cosmic_licensed is not None
        assert len(germline_variant.sanger_cosmic_licensed) > 0


class TestAmpDataSources:
    """Verify AMP-specific sources that are absent from the germline fixture."""

    def test_amp_annotation_present(self, amp_variant: AnnotatedVariant) -> None:
        assert amp_variant.amp_annotation is not None

    def test_oncokb_present(self, amp_variant: AnnotatedVariant) -> None:
        assert amp_variant.oncokb is not None
        assert len(amp_variant.oncokb) > 0

    def test_germline_lacks_amp_annotation(
        self, germline_variant: AnnotatedVariant
    ) -> None:
        assert germline_variant.amp_annotation is None

    def test_germline_lacks_oncokb(self, germline_variant: AnnotatedVariant) -> None:
        assert germline_variant.oncokb is None


class TestConveniencePropertiesEdgeCases:
    """Verify convenience properties handle empty / missing data gracefully."""

    def test_genes_empty_when_no_transcripts(self) -> None:
        v = AnnotatedVariant()
        assert v.genes == []

    def test_refseq_genes_empty_when_no_transcripts(self) -> None:
        v = AnnotatedVariant()
        assert v.refseq_genes == []

    def test_ensembl_genes_empty_when_no_transcripts(self) -> None:
        v = AnnotatedVariant()
        assert v.ensembl_genes == []

    def test_rs_ids_empty_when_no_dbsnp(self) -> None:
        v = AnnotatedVariant()
        assert v.rs_ids == []

    def test_gnomad_exomes_af_none_when_empty(self) -> None:
        v = AnnotatedVariant()
        assert v.gnomad_exomes_af is None

    def test_gnomad_genomes_af_none_when_empty(self) -> None:
        v = AnnotatedVariant()
        assert v.gnomad_genomes_af is None

    def test_gnomad_exomes_an_none_when_empty(self) -> None:
        v = AnnotatedVariant()
        assert v.gnomad_exomes_an is None

    def test_gnomad_genomes_an_none_when_empty(self) -> None:
        v = AnnotatedVariant()
        assert v.gnomad_genomes_an is None

    def test_acmg_verdict_none_when_no_annotation(self) -> None:
        v = AnnotatedVariant()
        assert v.acmg_verdict is None

    def test_acmg_rules_empty_when_no_annotation(self) -> None:
        v = AnnotatedVariant()
        assert v.acmg_rules == []


@pytest.fixture(scope="module")
def slim_germline_variant(germline_data: dict[str, Any]) -> SlimAnnotatedVariant:
    """Deserialize the germline fixture into a SlimAnnotatedVariant."""
    return SlimAnnotatedVariant(**germline_data)


@pytest.fixture(scope="module")
def slim_amp_variant(amp_data: dict[str, Any]) -> SlimAnnotatedVariant:
    """Deserialize the AMP fixture into a SlimAnnotatedVariant."""
    return SlimAnnotatedVariant(**amp_data)


class TestSlimDeserialization:
    """Verify that SlimAnnotatedVariant deserializes fixtures without errors."""

    def test_germline_deserializes(
        self, slim_germline_variant: SlimAnnotatedVariant
    ) -> None:
        assert slim_germline_variant is not None

    def test_amp_deserializes(self, slim_amp_variant: SlimAnnotatedVariant) -> None:
        assert slim_amp_variant is not None

    def test_empty_dict_produces_default(self) -> None:
        v = SlimAnnotatedVariant()
        assert v.chromosome is None
        assert v.pos is None

    def test_extra_fields_are_discarded(self) -> None:
        """Undeclared keys must be silently ignored (not stored)."""
        v = SlimAnnotatedVariant(
            chromosome="chr1",
            dbnsfp=[{"version": "4.9a"}],
            sanger_cosmic=[{"version": "100"}],
        )
        assert v.chromosome == "chr1"
        assert not hasattr(v, "dbnsfp")
        assert not hasattr(v, "sanger_cosmic")


class TestSlimCoreFields:
    """Verify core fields on the slim model match the full model."""

    @pytest.mark.parametrize("fixture", ["slim_germline_variant", "slim_amp_variant"])
    def test_chromosome(self, fixture: str, request: pytest.FixtureRequest) -> None:
        v: SlimAnnotatedVariant = request.getfixturevalue(fixture)
        assert v.chromosome == "chr7"

    @pytest.mark.parametrize("fixture", ["slim_germline_variant", "slim_amp_variant"])
    def test_pos(self, fixture: str, request: pytest.FixtureRequest) -> None:
        v: SlimAnnotatedVariant = request.getfixturevalue(fixture)
        assert v.pos == 140453136

    @pytest.mark.parametrize("fixture", ["slim_germline_variant", "slim_amp_variant"])
    def test_ref_alt(self, fixture: str, request: pytest.FixtureRequest) -> None:
        v: SlimAnnotatedVariant = request.getfixturevalue(fixture)
        assert v.ref == "A"
        assert v.alt == "T"


class TestSlimConvenienceProperties:
    """Convenience properties from the mixin must work on the slim model."""

    def test_genes(self, slim_germline_variant: SlimAnnotatedVariant) -> None:
        assert sorted(slim_germline_variant.genes) == ["BRAF"]

    def test_refseq_genes_not_empty(
        self, slim_germline_variant: SlimAnnotatedVariant
    ) -> None:
        assert len(slim_germline_variant.refseq_genes) > 0
        assert all(g == "BRAF" for g in slim_germline_variant.refseq_genes)

    def test_ensembl_genes_not_empty(
        self, slim_germline_variant: SlimAnnotatedVariant
    ) -> None:
        assert len(slim_germline_variant.ensembl_genes) > 0
        assert all(g == "BRAF" for g in slim_germline_variant.ensembl_genes)

    def test_rs_ids(self, slim_germline_variant: SlimAnnotatedVariant) -> None:
        assert slim_germline_variant.rs_ids == ["rs113488022"]

    def test_gnomad_exomes_af(
        self, slim_germline_variant: SlimAnnotatedVariant
    ) -> None:
        af = slim_germline_variant.gnomad_exomes_af
        assert af is not None
        assert float(af) > 0

    def test_gnomad_exomes_an(
        self, slim_germline_variant: SlimAnnotatedVariant
    ) -> None:
        assert slim_germline_variant.gnomad_exomes_an == 251260

    def test_acmg_verdict(self, slim_germline_variant: SlimAnnotatedVariant) -> None:
        assert slim_germline_variant.acmg_verdict == "Pathogenic"

    def test_acmg_rules(self, slim_germline_variant: SlimAnnotatedVariant) -> None:
        rules = slim_germline_variant.acmg_rules
        assert rules is not None
        assert "PS3" in rules
        assert "PM1" in rules


class TestSlimMatchesFullModel:
    """Verify that convenience properties return identical values on both models."""

    def test_genes_match(
        self,
        germline_variant: AnnotatedVariant,
        slim_germline_variant: SlimAnnotatedVariant,
    ) -> None:
        assert sorted(germline_variant.genes) == sorted(slim_germline_variant.genes)

    def test_rs_ids_match(
        self,
        germline_variant: AnnotatedVariant,
        slim_germline_variant: SlimAnnotatedVariant,
    ) -> None:
        assert germline_variant.rs_ids == slim_germline_variant.rs_ids

    def test_gnomad_exomes_af_match(
        self,
        germline_variant: AnnotatedVariant,
        slim_germline_variant: SlimAnnotatedVariant,
    ) -> None:
        assert (
            germline_variant.gnomad_exomes_af == slim_germline_variant.gnomad_exomes_af
        )

    def test_gnomad_exomes_an_match(
        self,
        germline_variant: AnnotatedVariant,
        slim_germline_variant: SlimAnnotatedVariant,
    ) -> None:
        assert (
            germline_variant.gnomad_exomes_an == slim_germline_variant.gnomad_exomes_an
        )

    def test_gnomad_genomes_af_match(
        self,
        germline_variant: AnnotatedVariant,
        slim_germline_variant: SlimAnnotatedVariant,
    ) -> None:
        assert (
            germline_variant.gnomad_genomes_af
            == slim_germline_variant.gnomad_genomes_af
        )

    def test_acmg_verdict_match(
        self,
        germline_variant: AnnotatedVariant,
        slim_germline_variant: SlimAnnotatedVariant,
    ) -> None:
        assert germline_variant.acmg_verdict == slim_germline_variant.acmg_verdict

    def test_acmg_rules_match(
        self,
        germline_variant: AnnotatedVariant,
        slim_germline_variant: SlimAnnotatedVariant,
    ) -> None:
        assert germline_variant.acmg_rules == slim_germline_variant.acmg_rules


class TestSlimEdgeCases:
    """Verify slim model handles empty / missing data gracefully."""

    def test_genes_empty_when_no_transcripts(self) -> None:
        v = SlimAnnotatedVariant()
        assert v.genes == []

    def test_rs_ids_empty_when_no_dbsnp(self) -> None:
        v = SlimAnnotatedVariant()
        assert v.rs_ids == []

    def test_gnomad_exomes_af_none_when_empty(self) -> None:
        v = SlimAnnotatedVariant()
        assert v.gnomad_exomes_af is None

    def test_gnomad_genomes_af_none_when_empty(self) -> None:
        v = SlimAnnotatedVariant()
        assert v.gnomad_genomes_af is None

    def test_gnomad_exomes_an_none_when_empty(self) -> None:
        v = SlimAnnotatedVariant()
        assert v.gnomad_exomes_an is None

    def test_gnomad_genomes_an_none_when_empty(self) -> None:
        v = SlimAnnotatedVariant()
        assert v.gnomad_genomes_an is None

    def test_acmg_verdict_none_when_no_annotation(self) -> None:
        v = SlimAnnotatedVariant()
        assert v.acmg_verdict is None

    def test_acmg_rules_empty_when_no_annotation(self) -> None:
        v = SlimAnnotatedVariant()
        assert v.acmg_rules == []
