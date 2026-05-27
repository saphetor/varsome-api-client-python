from typing import Any

import pyarrow as pa

from varsome_api.models.slim.annotation import AnnotatedVariant

PARQUET_SCHEMA: pa.Schema = pa.schema(
    [
        pa.field("original_variant", pa.string(), nullable=True),
        pa.field("chromosome", pa.string(), nullable=True),
        pa.field("pos", pa.int64(), nullable=True),
        pa.field("ref", pa.string(), nullable=True),
        pa.field("alt", pa.string(), nullable=True),
        pa.field("gnomad_exomes_af", pa.float64(), nullable=True),
        pa.field("gnomad_exomes_an", pa.int64(), nullable=True),
        pa.field("gnomad_genomes_af", pa.float64(), nullable=True),
        pa.field("gnomad_genomes_an", pa.int64(), nullable=True),
        pa.field("acmg_verdict", pa.string(), nullable=True),
        pa.field("acmg_rules", pa.list_(pa.string()), nullable=True),
        pa.field("genes", pa.list_(pa.string()), nullable=True),
        pa.field("rs_ids", pa.list_(pa.string()), nullable=True),
    ]
)


def _coerce_float(value: float | str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_parquet_row(variant: AnnotatedVariant) -> dict[str, Any]:
    clean_acmg_rules: list[str] = [
        r for r in (variant.acmg_rules or []) if r is not None
    ]

    return {
        "original_variant": variant.original_variant,
        "chromosome": variant.chromosome,
        "pos": variant.pos,
        "ref": variant.ref,
        "alt": variant.alt,
        "gnomad_exomes_af": _coerce_float(variant.gnomad_exomes_af),
        "gnomad_exomes_an": variant.gnomad_exomes_an,
        "gnomad_genomes_af": _coerce_float(variant.gnomad_genomes_af),
        "gnomad_genomes_an": variant.gnomad_genomes_an,
        "acmg_verdict": variant.acmg_verdict,
        "acmg_rules": clean_acmg_rules or None,
        "genes": variant.genes or None,
        "rs_ids": variant.rs_ids or None,
    }
