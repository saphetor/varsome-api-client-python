from varsome_api.models.annotation import VariantVariantApi


class AnnotatedVariantPropertiesMixin:
    """Mixin providing convenience properties for variant annotation results.

    Expects the consuming class to declare the following attributes
    (all ``None``-able):

    - ``refseq_transcripts`` / ``ensembl_transcripts`` — iterables whose
      items expose ``.items`` containing objects with a ``.gene_symbol``.
    - ``ncbi_dbsnp`` — iterable whose items expose ``.rsid`` (list of ints).
    - ``gnomad_exomes`` / ``gnomad_genomes`` — iterables whose items
      expose ``.af`` and ``.an``.
    - ``acmg_annotation`` — object with ``.verdict.acmg_rules.verdict``
      and ``.verdict.classifications``.
    """

    @property
    def genes(self) -> list[str]:
        """Return the deduplicated union of RefSeq and Ensembl gene symbols."""
        genes: list[str] = []
        genes.extend(self.refseq_genes)
        genes.extend(self.ensembl_genes)
        return list(set(genes))

    @property
    def refseq_genes(self) -> list[str]:
        """Return gene symbols extracted from RefSeq transcripts."""
        genes: list[str] = []
        if self.refseq_transcripts:
            for transcript in self.refseq_transcripts:
                if transcript.items:
                    genes.extend(
                        item.gene_symbol
                        for item in transcript.items
                        if item.gene_symbol
                    )
        return genes

    @property
    def ensembl_genes(self) -> list[str]:
        """Return gene symbols extracted from Ensembl transcripts."""
        genes: list[str] = []
        if self.ensembl_transcripts:
            for transcript in self.ensembl_transcripts:
                if transcript.items:
                    genes.extend(
                        item.gene_symbol
                        for item in transcript.items
                        if item.gene_symbol
                    )
        return genes

    @property
    def rs_ids(self) -> list[str]:
        """Return dbSNP RS identifiers prefixed with ``rs``."""
        rs_ids: list[int] = []
        if self.ncbi_dbsnp:
            for dbsnp_entry in self.ncbi_dbsnp:
                rs_ids.extend(dbsnp_entry.rsid)
        return [f"rs{rs_id}" for rs_id in rs_ids]

    @property
    def gnomad_exomes_af(self) -> float | str | None:
        """Return the gnomAD exomes allele frequency, or None if unavailable."""
        if self.gnomad_exomes:
            af = [entry.af for entry in self.gnomad_exomes if entry.af is not None]
            return af[0] if af else None
        return None

    @property
    def gnomad_genomes_af(self) -> float | str | None:
        """Return the gnomAD genomes allele frequency, or None if unavailable."""
        if self.gnomad_genomes:
            af = [entry.af for entry in self.gnomad_genomes if entry.af is not None]
            return af[0] if af else None
        return None

    @property
    def gnomad_exomes_an(self) -> int | None:
        """Return the gnomAD exomes allele number, or None if unavailable."""
        if self.gnomad_exomes:
            an = [entry.an for entry in self.gnomad_exomes if entry.an is not None]
            return an[0] if an else None
        return None

    @property
    def gnomad_genomes_an(self) -> int | None:
        """Return the gnomAD genomes allele number, or None if unavailable."""
        if self.gnomad_genomes:
            an = [entry.an for entry in self.gnomad_genomes if entry.an is not None]
            return an[0] if an else None
        return None

    @property
    def acmg_verdict(self) -> str | None:
        """Return the ACMG classification verdict string, or None."""
        if (
            self.acmg_annotation is not None
            and self.acmg_annotation.verdict is not None
            and self.acmg_annotation.verdict.acmg_rules is not None
        ):
            return self.acmg_annotation.verdict.acmg_rules.verdict
        return None

    @property
    def acmg_rules(self) -> list[str]:
        """Return the list of ACMG classification rule names, or an empty list."""
        if (
            self.acmg_annotation is not None
            and self.acmg_annotation.verdict is not None
        ):
            return self.acmg_annotation.verdict.classifications
        return []


class AnnotatedVariant(VariantVariantApi, AnnotatedVariantPropertiesMixin):
    """Variant annotation result with convenience accessors.

    All fields from the OpenAPI ``variant_VariantApi`` schema are
    available as typed attributes.  The computed ``@property`` methods
    (provided by :class:`AnnotatedVariantPropertiesMixin`) offer
    shortcuts for the most commonly needed derived values.

    This model validates **every** field the API returns (via
    ``extra="allow"`` on the base).  For performance-sensitive
    pipelines, consider :class:`~varsome_api.models.slim.annotation.AnnotatedVariant`
    which validates only the fields needed by the default
    ``VCFAnnotator.annotate_record``, or use your own Pydantic model
    """

    pass
