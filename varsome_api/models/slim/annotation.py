from pydantic import BaseModel, ConfigDict, Field

from varsome_api.models.variant import AnnotatedVariantPropertiesMixin


class _SlimBase(BaseModel):
    """Common base for all slim models.

    ``extra="ignore"`` silently drops any key that is not declared
    as a field.
    """

    model_config = ConfigDict(extra="ignore")


class GnomadFrequency(_SlimBase):
    """Allele frequency and allele number from gnomAD (exomes or genomes)."""

    af: float | None = None
    an: int | None = None


class AcmgRules(_SlimBase):
    """ACMG rules verdict (innermost level)."""

    verdict: str | None = None


class AcmgVerdict(_SlimBase):
    """ACMG verdict containing the rules object and classification list."""

    acmg_rules: AcmgRules | None = Field(None, alias="ACMG_rules")
    classifications: list[str | None] | None = None


class AcmgAnnotation(_SlimBase):
    """Top-level ACMG annotation — only the verdict sub-tree."""

    verdict: AcmgVerdict | None = None


class TranscriptItem(_SlimBase):
    """Single transcript item — only the gene symbol is retained."""

    gene_symbol: str | None = None


class Transcript(_SlimBase):
    """Transcript list wrapper (shared by RefSeq and Ensembl)."""

    items: list[TranscriptItem] | None = None


class DbsnpItem(_SlimBase):
    """dbSNP entry — only the RS-ID list."""

    rsid: list[int | None] | None = None


class AnnotatedVariant(_SlimBase, AnnotatedVariantPropertiesMixin):
    """Lightweight variant model for VCF annotation pipelines."""

    original_variant: str | None = None
    chromosome: str | None = None
    pos: int | None = None
    ref: str | None = None
    alt: str | None = None
    gnomad_exomes: list[GnomadFrequency] | None = None
    gnomad_genomes: list[GnomadFrequency] | None = None
    acmg_annotation: AcmgAnnotation | None = None
    refseq_transcripts: list[Transcript] | None = None
    ensembl_transcripts: list[Transcript] | None = None
    ncbi_dbsnp: list[DbsnpItem] | None = None
