# Developer Guide

This guide covers using `VarSomeAPIClient` and `VCFAnnotator` inside your own Python code.

For CLI usage see the [root README](../README.md).
For Docker usage see [docker.md](docker.md).

---

## Installation

### Core library (no VCF support)

If you only need `VarSomeAPIClient` for programmatic variant lookup and **do not**
require `VCFAnnotator`, install without extras — no C compiler or system libraries
are needed:

```bash
pip install git+https://github.com/saphetor/varsome-api-client-python.git
```

With [Poetry](https://python-poetry.org/):

```bash
poetry add git+https://github.com/saphetor/varsome-api-client-python.git
```

### With VCF support (`[vcf]` extra)

`VCFAnnotator` and `varsome_api_annotate_vcf` depend on
[pysam](https://pysam.readthedocs.io/), a C extension that wraps htslib.
Install the `vcf` extra to include it:

```bash
pip install "varsome_api[vcf] @ git+https://github.com/saphetor/varsome-api-client-python.git"
```

With Poetry:

```bash
poetry add "git+https://github.com/saphetor/varsome-api-client-python.git[vcf]"
```

#### Build dependencies for pysam

pysam requires the following system libraries to compile. Install them before
running `pip install`:

**Ubuntu / Debian**

```bash
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libdeflate-dev
```

**macOS (Homebrew)**

```bash
brew install bzip2 xz curl openssl libdeflate
```

> **Tip:** If managing these libraries is inconvenient, use the pre-built
> Docker image instead — it ships with all dependencies pre-compiled.
> See [docker.md](docker.md) for details.

### Cloning the repository (development)

Clone the repository and install all dependencies, including dev tooling:

```bash
git clone https://github.com/saphetor/varsome-api-client-python.git
cd varsome-api-client-python
poetry install --all-extras
```

`--all-extras` ensures pysam is installed alongside the regular dev dependencies.
Without it, tests that import `pysam` will fail with an `ImportError`.

---

## Running the tests

The test suite uses [pytest](https://docs.pytest.org/) with
[pytest-asyncio](https://pytest-asyncio.readthedocs.io/) and
[pytest-cov](https://pytest-cov.readthedocs.io/).

### Run the full suite

```bash
poetry run pytest
```

Coverage is measured automatically. The suite must reach **80 % total coverage**
or pytest exits with a non-zero status.

### Run a specific test file

```bash
poetry run pytest tests/test_vcf.py
```

### Run a specific test class or function

```bash
poetry run pytest tests/test_vcf.py::TestReadHeaderFromVcf
poetry run pytest tests/test_vcf.py::TestReadHeaderFromVcf::test_returns_header_object
```

### Run with verbose output

```bash
poetry run pytest -v
```

---
Requires **Python ≥ 3.11, < 3.15**.

---

## VarSomeAPIClient

### Single lookup (synchronous)

`lookup` is a synchronous convenience wrapper around the underlying async method.
It returns a plain `dict` containing the full API JSON response.

The `query_type` parameter controls what type of lookup is performed:
- `"variants"` (default): variant lookup
- `"genes"`: gene symbol lookup
- `"cnvs"`: CNV query lookup

#### Variant lookup

```python
from varsome_api.client import VarSomeAPIClient

api = VarSomeAPIClient(api_key="YOUR_API_KEY")

result = api.lookup(
    "chr7-140453136-A-T",
    params={"add-source-databases": "gnomad-exomes,refseq-transcripts"},
    ref_genome="hg19",
)

# Access any field from the raw JSON response
print(result["chromosome"])
print(result["gnomad_exomes"])
```

#### Gene lookup

```python
from varsome_api.client import VarSomeAPIClient

api = VarSomeAPIClient(api_key="YOUR_API_KEY")

result = api.lookup(
    "BRCA1",
    query_type="genes",
    ref_genome="hg19",
)

print(result)
```

#### CNV lookup

```python
from varsome_api.client import VarSomeAPIClient

api = VarSomeAPIClient(api_key="YOUR_API_KEY")

result = api.lookup(
    "chr1:122:5235:DEL",
    query_type="cnvs",
    ref_genome="hg19",
)

print(result)
```

> **Note:** CNV queries do not support batch mode. Each CNV must be looked up
> individually via `lookup(..., query_type="cnvs")`.

`api_key` is optional for single-item lookups against public data. It is
required for batch lookups.

To target a specific API server, pass `api_url`:

```python
api = VarSomeAPIClient(
    api_key="YOUR_API_KEY",
    api_url="https://stable-api.varsome.com",
)
```

### Batch lookup (synchronous)

`batch_lookup` sends items (variants, genes, etc.) in batches and returns a
`list[BatchResult]`. Each `BatchResult` pairs the submitted query strings with
the corresponding API response list, aligned by index.

The `query_type` parameter controls what type of batch lookup is performed:
- `"variants"` (default): variant batch lookup
- `"genes"`: gene symbol batch lookup
- `"cnvs"`: not supported for batch (CNVs must be queried individually)

#### Batch variant lookup

```python
from varsome_api.client import VarSomeAPIClient

api = VarSomeAPIClient(api_key="YOUR_API_KEY")

variants = ["chr7-140453136-A-T", "chr19:20082943:1:G", "chr22:39777823::CAA"]

batch_results = api.batch_lookup(
    variants,
    params={"add-source-databases": "gnomad-exomes,gnomad-genomes"},
    ref_genome="hg19",
)

for batch in batch_results:
    for i, query_string in enumerate(batch.queries):
        annotation = batch.response[i]
        if "error" in annotation:
            print(f"{query_string}: error — {annotation['error']}")
        elif "filtered_out" in annotation:
            print(f"{query_string}: filtered out — {annotation['filtered_out']}")
        else:
            print(f"{query_string}: gnomad_exomes = {annotation.get('gnomad_exomes')}")
```

#### Batch gene lookup

```python
from varsome_api.client import VarSomeAPIClient

api = VarSomeAPIClient(api_key="YOUR_API_KEY")

genes = ["BRCA1", "TP53", "EGFR"]

batch_results = api.batch_lookup(
    genes,
    query_type="genes",
    params={"add-source-databases": "cgd"},
    ref_genome="hg19",
)

for batch in batch_results:
    for i, gene_symbol in enumerate(batch.queries):
        annotation = batch.response[i]
        if "error" in annotation:
            print(f"{gene_symbol}: error — {annotation['error']}")
        else:
            print(f"{gene_symbol}: {annotation}")
```

> **Batch limits:** The API enforces different limits per environment:
> - **Live / Stable**: Variants: 200, Genes: 100
> - **Staging**: Variants: 50, Genes: 10

`max_variants_per_batch` (default `200`) controls how many items are sent per
POST request. `max_requests` (default `5`) controls the maximum number of
concurrent HTTP requests:

```python
api = VarSomeAPIClient(api_key="YOUR_API_KEY", max_variants_per_batch=50)
results = api.batch_lookup(variants, max_requests=10, ref_genome="hg38")
```

### Exception handling

All API errors raise `VarSomeAPIException`:

```python
from varsome_api.client import VarSomeAPIClient
from varsome_api.exceptions import VarSomeAPIException

api = VarSomeAPIClient(api_key="YOUR_API_KEY")

try:
    result = api.lookup("chr19:20082943:1:G", ref_genome="hg64")
except VarSomeAPIException as e:
    print(e)  # e.g. "404 — invalid reference genome"
```

---

## Async interface

The client is async-native. The synchronous `lookup` / `batch_lookup` methods
are thin wrappers. Use the async interface directly for better performance in
async code.

### Single item lookup

```python
import asyncio
from varsome_api.client import VarSomeAPIClient

async def main():
    async with VarSomeAPIClient(api_key="YOUR_API_KEY") as api:
        # Variant lookup
        result = await api.alookup(
            "chr7-140453136-A-T",
            params={"add-source-databases": "gnomad-exomes"},
            ref_genome="hg19",
        )
        print(result["chromosome"])

        # Gene lookup
        result = await api.alookup(
            "BRCA1",
            query_type="genes",
            ref_genome="hg19",
        )
        print(result)

        # CNV lookup
        result = await api.alookup(
            "chr1:100:L1254:DUP",
            query_type="cnvs",
            ref_genome="hg19",
        )
        print(result)

asyncio.run(main())
```

Using `async with` keeps a single HTTP session alive for all requests inside the
block, avoiding per-request connection overhead. Without the context manager, each
call creates and closes its own session automatically.

### Batch lookup (async generator)

`abatch_lookup` is an async generator that yields `BatchResult` objects as each
batch completes. The `query_type` parameter controls whether variants, genes, or
other query types are batch-processed.

#### Batch variant lookup

```python
import asyncio
from varsome_api.client import VarSomeAPIClient

async def main():
    variants = ["chr7-140453136-A-T", "chr19:20082943:1:G", "chr22:39777823::CAA"]

    async with VarSomeAPIClient(api_key="YOUR_API_KEY") as api:
        async for batch in api.abatch_lookup(
            variants,
            params={"add-source-databases": "gnomad-exomes,gnomad-genomes"},
            ref_genome="hg19",
            max_requests=5,
        ):
            for i, query_string in enumerate(batch.queries):
                annotation = batch.response[i]
                print(query_string, annotation.get("gnomad_exomes"))

asyncio.run(main())
```

#### Batch gene lookup

```python
import asyncio
from varsome_api.client import VarSomeAPIClient

async def main():
    genes = ["BRCA1", "TP53", "EGFR"]

    async with VarSomeAPIClient(api_key="YOUR_API_KEY") as api:
        async for batch in api.abatch_lookup(
            genes,
            query_type="genes",
            ref_genome="hg19",
            max_requests=5,
        ):
            for i, gene_symbol in enumerate(batch.queries):
                annotation = batch.response[i]
                print(gene_symbol, annotation)


asyncio.run(main())
```

---

## Working with response models

The raw API response is a `dict`. You can wrap it in `AnnotatedVariant` for typed
attribute access and convenience properties.

### Full model

```python
from varsome_api.client import VarSomeAPIClient
from varsome_api.models.variant import AnnotatedVariant

api = VarSomeAPIClient(api_key="YOUR_API_KEY")

result = api.lookup(
    "chr7-140453136-A-T",
    params={"add-source-databases": "gnomad-exomes,refseq-transcripts"},
    ref_genome="hg19",
)

variant = AnnotatedVariant(**result)

print(variant.chromosome)          # e.g. "7"
print(variant.pos)                 # e.g. 140453136
print(variant.ref)                 # e.g. "A"
print(variant.alt)                 # e.g. "T"
print(variant.genes)               # deduplicated list of gene symbols
print(variant.gnomad_exomes_af)    # allele frequency float or None
print(variant.gnomad_genomes_af)   # allele frequency float or None
print(variant.acmg_verdict)        # e.g. "Pathogenic" or None
print(variant.acmg_rules)          # list of ACMG rule names
print(variant.rs_ids)              # e.g. ["rs113488022"]
```

`AnnotatedVariant` (from `varsome_api.models.variant`) validates **every** field
the API returns. For performance-sensitive pipelines processing many variants, see
the slim model section below.

### Accessing versioned database entries

Some annotation databases (e.g. gnomAD) are returned as lists because the API may in the future
return multiple database versions. Each list item is a typed object:

```python
try:
    allele_number = [entry.an for entry in variant.gnomad_exomes][0]
except IndexError:
    allele_number = None  # no gnomAD exomes annotation for this variant
```

It is safe to assume only one item is present currently.

### Somatic and germline annotation modes

Pass annotation-mode parameters via the `params` argument:

```python
from varsome_api.client import VarSomeAPIClient
from varsome_api.models.variant import AnnotatedVariant
from varsome_api.exceptions import VarSomeAPIException

api = VarSomeAPIClient(api_key="YOUR_API_KEY", api_url="https://stable-api.varsome.com")

try:
    result = api.lookup(
        "chr22-29091857-G-",
        params={
            "add-source-databases": "gnomad-exomes,refseq-transcripts",
            "annotation-mode": "somatic",
            "cancer-type": "Prostate Adenocarcinoma",
            "tissue-type": "Prostate",
        },
        ref_genome="hg19",
    )
except VarSomeAPIException as e:
    print(e)
else:
    variant = AnnotatedVariant(**result)
    print(variant.chromosome, variant.gnomad_exomes_af, variant.amp_annotation)
```

```python
try:
    result = api.lookup(
        "15:68500735:C:T",
        params={
            "add-source-databases": "gnomad-exomes,refseq-transcripts",
            "annotation-mode": "germline", # default
            "patient-phenotypes": "Progressive Visual Loss",
        },
        ref_genome="hg19",
    )
except VarSomeAPIException as e:
    print(e)
else:
    variant = AnnotatedVariant(**result)
    print(variant.chromosome, variant.alt, variant.gnomad_exomes_af)
```

---

## VCF annotation

### Basic usage

`VCFAnnotator` reads an input VCF, sends variants in batches to the API, and
writes an annotated output VCF. It subclasses `VarSomeAPIClient` so all client
parameters apply.

```python
from varsome_api.vcf import VCFAnnotator

annotator = VCFAnnotator(
    api_key="YOUR_API_KEY",
    ref_genome="hg19",
    request_parameters={"add-ACMG-annotation": "1"},
)
annotator.annotate("input.vcf", "annotated.vcf")
```

The default annotator writes the following INFO fields to the output VCF:
`gnomad_exomes_AF`, `gnomad_genomes_AF`, `acmg_verdict`, `acmg_rules`, `genes`,
`original_variant`.

> **Limitation:** VCF annotation supports SNPs and small indels (up to 200 bp) only.

### Async annotation

`VCFAnnotator` also exposes an async method and supports `async with`:

```python
import asyncio
from varsome_api.vcf import VCFAnnotator

async def main():
    annotator = VCFAnnotator(
        api_key="YOUR_API_KEY",
        ref_genome="hg19",
        request_parameters={"add-all-data": "1"},
        max_requests=5,
    )
    async with annotator:
        result = await annotator.aannotate("input.vcf", "annotated.vcf")

    print(f"Annotated {result.total_variants} variant(s)")
    for variant, info in result.filtered_out_variants:
        print(f"Filtered: {variant} — {info.get('filtered_out')}")
    for variant, info in result.variants_with_errors:
        print(f"Error: {variant} — {info.get('error')}")

asyncio.run(main())
```

### Customising what gets written to the VCF

Override `annotate_record` and `add_vcf_header_info` to control which fields
appear in the output VCF:

```python
import pysam
from varsome_api.vcf import VCFAnnotator
from varsome_api.models.variant import AnnotatedVariant


class MyVCFAnnotator(VCFAnnotator):
    # Switch to the full model to access gnomad_exomes_an,
    # which is not present on the default slim model.
    variant_model = AnnotatedVariant

    def annotate_record(self, record, variant_result, original_variant):
        an = variant_result.gnomad_exomes_an
        if an is not None:
            record.info["gnomad_exomes_AN"] = an
        # Optionally include the default annotations too:
        # super().annotate_record(record, variant_result, original_variant)

    def add_vcf_header_info(self, header):
        header.info.add(
            "gnomad_exomes_AN", "1", "Integer",
            "gnomAD exomes allele number",
        )
        # super().add_vcf_header_info(header)


annotator = MyVCFAnnotator(
    api_key="YOUR_API_KEY",
    ref_genome="hg38",
    request_parameters={
        "add-source-databases": "gnomad-exomes,refseq-transcripts",
        "annotation-mode": "somatic",
        "cancer-type": "Prostate Adenocarcinoma",
        "tissue-type": "Prostate",
    },
)
annotator.annotate("input.vcf", "annotated.vcf")
```

---

## Slim vs full `AnnotatedVariant`

| Model | Location | Fields validated | Use when |
|-------|----------|-----------------|----------|
| Slim (default) | `varsome_api.models.slim.annotation` | ~12 fields used by `annotate_record` | VCF annotation pipelines where you only need the defaults |
| Full | `varsome_api.models.variant` | Every field the API returns | You need access to any field beyond the slim defaults |

The slim model uses `extra="ignore"` so unknown fields are silently discarded
before Pydantic validates — significantly faster for large VCFs.

### Custom slim model

If you need a handful of fields beyond the defaults without the overhead of
the full model, define your own:

```python
from pydantic import BaseModel, ConfigDict
from varsome_api.models.annotation import AcmgAnnotation, GnomadExome, DbnsfpItem
from varsome_api.models.variant import AnnotatedVariantPropertiesMixin
from varsome_api.vcf import VCFAnnotator


class MySlimVariant(BaseModel, AnnotatedVariantPropertiesMixin):
    """Slim model with dbnsfp added on top of the basics."""

    model_config = ConfigDict(extra="ignore")

    original_variant: str | None = None
    chromosome: str | None = None
    pos: int | None = None
    ref: str | None = None
    alt: str | None = None
    gnomad_exomes: list[GnomadExome] | None = None
    acmg_annotation: AcmgAnnotation | None = None
    dbnsfp: list[DbnsfpItem] | None = None


class MyAnnotator(VCFAnnotator):
    variant_model = MySlimVariant

    def annotate_record(self, record, variant_result, original_variant):
        if variant_result.dbnsfp:
            sift_values = variant_result.dbnsfp[0].sift_pred
            if sift_values:
                record.info["sift_pred"] = ",".join(s for s in sift_values if s)
        record.info["original_variant"] = original_variant

    def add_vcf_header_info(self, header):
        header.info.add("sift_pred", ".", "String", "SIFT predictions")
        header.info.add("original_variant", "1", "String", "Original variant string")
```

> **Tip:** `AnnotatedVariantPropertiesMixin` provides the convenience properties
> (`genes`, `gnomad_exomes_af`, `acmg_verdict`, etc.) on any model that declares
> the expected attribute names. Mix-and-match slim and full nested types freely.

---

## Model generation

`varsome_api/models/annotation.py` was **code-generated** from the OpenAPI schema
published at [`https://api.varsome.com/openapi/variants/`](https://api.varsome.com/openapi/variants/)
using [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator):

```bash
pip install datamodel-code-generator

datamodel-codegen \
    --url https://api.varsome.com/openapi/variants/ \
    --output varsome_api/models/annotation.py \
    --output-model-type pydantic_v2.BaseModel \
    --target-python-version 3.11 \
    --use-standard-collections \
    --use-union-operator
```

The raw output was then customised in two ways:

1. **Shared base class.** A `_GeneratedBase` class was introduced at the top of
   `annotation.py`.  Every generated model was rebased onto it (replacing
   `BaseModel`) so that configuration changes — currently `extra="allow"` to
   absorb undocumented fields — apply uniformly:

   ```python
   class _GeneratedBase(BaseModel):
       model_config = ConfigDict(extra="allow")

   class UniprotRegionItem(_GeneratedBase):   # was: BaseModel
       ...
   ```

2. **Readability pass.** Field names, ordering, and minor type annotations were
   adjusted to match the rest of the codebase style; no semantic changes were
   made.

### Regenerating after an API schema change

1. Re-run `datamodel-codegen` with the command above to produce a fresh
   `annotation.py`.
2. Restore the `_GeneratedBase` class at the top of the file and rebase all
   generated models onto it (search-replace `(BaseModel)` → `(_GeneratedBase)`).
3. Re-apply any readability edits that are worth keeping.
4. Run the test suite — `poetry run pytest` — to catch any field renames or
   structural changes introduced by the updated schema.

---

## Using the library for custom output formats

`VarSomeAPIClient` and the Pydantic annotation models are not tied to VCF.
Any Python project can use the batch API, parse responses with the slim (or full)
`AnnotatedVariant` model, and write the results in whatever format is most
appropriate for the downstream workflow — Parquet, CSV, JSON-lines, a database,
a message queue, etc.

The general pattern is always the same:

```python
from varsome_api.client import VarSomeAPIClient
from varsome_api.models.slim.annotation import AnnotatedVariant

api = VarSomeAPIClient(api_key="YOUR_API_KEY")

for batch in api.batch_lookup(my_variants, params={...}, ref_genome="hg19"):
    for i, query_string in enumerate(batch.queries):
        raw = batch.response[i]
        if "error" not in raw and "filtered_out" not in raw:
            variant = AnnotatedVariant(**raw)
            # … transform `variant` and write to your target format
```

### Working example — CSV → Parquet

See [`examples/README.md`](../examples/README.md) for a
self-contained, runnable example that demonstrates this pattern end-to-end.

---

## Available request parameters

Refer to [api.varsome.com](https://api.varsome.com) and the
[API documentation](https://api.varsome.com/docs/variants/) for the full list of
query parameters and response fields.
