# Examples

This directory contains self-contained examples that demonstrate how the
`varsome_api` library can be used for custom annotation pipelines beyond
the built-in VCF workflow.

Each sub-directory is a standalone project with its own `requirements.txt`.

---

## Available examples

### [`parquet/`](parquet/)

**Annotate variants from a CSV file and write results to Parquet.**

This example shows how to:

- Read variant strings from a plain CSV file.
- Annotate them in batches using `VarSomeAPIClient`.
- Parse each API response with the lightweight **slim** Pydantic model
  (`varsome_api.models.slim.annotation.AnnotatedVariant`) — the same model
  used internally by `VCFAnnotator`.
- Flatten the nested annotation into a plain `dict` using `to_parquet_row()`.
- Write all rows to a [Parquet](https://parquet.apache.org/) file via
  [PyArrow](https://arrow.apache.org/docs/python/).

#### Quick start

```bash
# 1. Clone the repository and enter the example directory
git clone https://github.com/saphetor/varsome-api-client-python.git
cd varsome-api-client-python/examples/parquet

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies (varsome_api from the local clone + pyarrow)
pip install -r requirements.txt

# 4. Run the annotation script
#    Set VARSOME_API_KEY if you have one; batch lookups require one.
VARSOME_API_KEY=your_key_here python annotate_to_parquet.py

# Optional flags
python annotate_to_parquet.py \
    --api-key  your_key_here \
    --input    variants.csv \
    --output   annotated_variants.parquet \
    --genome   hg19

# 5. Inspect the output (pyarrow is already installed)
python - <<'EOF'
import pyarrow.parquet as pq
table = pq.read_table("annotated_variants.parquet")
print(table.schema)
print(table.slice(0, 5).to_pydict())
EOF
```

The script writes `annotated_variants.parquet` in the same directory.
Each row corresponds to one annotated variant and contains the following
columns:

| Column | Type | Description |
|--------|------|-------------|
| `original_variant` | `string` | Variant string as submitted to the API |
| `chromosome` | `string` | Chromosome identifier |
| `pos` | `int64` | Genomic position |
| `ref` | `string` | Reference allele |
| `alt` | `string` | Alternate allele |
| `gnomad_exomes_af` | `double` | gnomAD exomes allele frequency |
| `gnomad_exomes_an` | `int64` | gnomAD exomes allele number |
| `gnomad_genomes_af` | `double` | gnomAD genomes allele frequency |
| `gnomad_genomes_an` | `int64` | gnomAD genomes allele number |
| `acmg_verdict` | `string` | ACMG classification verdict |
| `acmg_rules` | `list<string>` | Active ACMG rule names |
| `genes` | `list<string>` | Deduplicated gene symbols |
| `rs_ids` | `list<string>` | dbSNP RS identifiers (`rs…`) |
