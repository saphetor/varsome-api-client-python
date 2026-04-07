# VarSome API Client

A Python client for the [VarSome API](https://api.varsome.com) — annotate genetic variants
against gnomAD, ClinVar, and many other databases via a simple
command-line interface or a Python library.

---

## ⚠️ Legacy version notice

This is a **new major version** (`1.x`) that requires **Python ≥ 3.11**.

If you need compatibility with Python 3.10 or earlier, use the previous release:

> **[v0.0.3 — Python ≤ 3.10 compatible](https://github.com/saphetor/varsome-api-client-python/tree/v0.0.3)**

---

## What this library provides

- **`varsome_api_run`** — look up one or more variants, genes, or CNVs and receive
  the full JSON annotation response.
- **`varsome_api_annotate_vcf`** — read a VCF file, annotate every variant via the
  VarSome API, and write an annotated output VCF.
- **`VarSomeAPIClient`** — a Python class for integrating variant, gene, and CNV
  annotation directly into your own code (synchronous and async interfaces).
- **`VCFAnnotator`** — a customisable VCF annotation pipeline class for use in
  your own Python projects.

---

## Installation

### End users — CLI tools

If you only want to run `varsome_api_run` or `varsome_api_annotate_vcf`,
**the Docker image is the recommended approach** — it ships with all system
dependencies pre-installed and requires no local build toolchain:

```bash
docker pull ghcr.io/saphetor/varsome-api-client-python:1
```

See the [Docker Guide](docs/docker.md) for full usage instructions.

---

### Python install — core library (no VCF support)

If you only need `VarSomeAPIClient` for variant lookup in your own code and
**do not** require VCF reading/writing, install without extras:

```bash
pip install git+https://github.com/saphetor/varsome-api-client-python.git
```

Or with [Poetry](https://python-poetry.org/):

```bash
poetry add git+https://github.com/saphetor/varsome-api-client-python.git
```

---

### Python install — with VCF support (`[vcf]` extra)

`varsome_api_annotate_vcf` and `VCFAnnotator` depend on
[pysam](https://pysam.readthedocs.io/), which requires several C build
libraries. Install the `vcf` extra to include pysam:

```bash
pip install "varsome_api[vcf] @ git+https://github.com/saphetor/varsome-api-client-python.git"
```

Or with Poetry:

```bash
poetry add "git+https://github.com/saphetor/varsome-api-client-python.git[vcf]"
```

> **Build requirements for pysam** — the following system libraries must be
> present before `pip` can compile pysam:
>
> | Library | Ubuntu/Debian | macOS (Homebrew) |
> |---------|---------------|-----------------|
> | zlib | `zlib1g-dev` | `zlib` |
> | bzip2 | `libbz2-dev` | `bzip2` |
> | lzma | `liblzma-dev` | `xz` |
> | libcurl | `libcurl4-openssl-dev` | `curl` |
> | OpenSSL | `libssl-dev` | `openssl` |
> | libdeflate | `libdeflate-dev` | `libdeflate` |
> | build tools | `build-essential` | Xcode CLT |
>
> If installing these is inconvenient, **use the Docker image instead** —
> it handles all of this for you.

After installation, the `varsome_api_run` and `varsome_api_annotate_vcf` commands
will be available in your `PATH`.

Requires **Python ≥ 3.11, < 3.15**.

---

## API servers

| Server  | URL | Notes                                        |
|---------|-----|----------------------------------------------|
| Live    | `https://api.varsome.com` | Default                                      |
| Stable  | `https://stable-api.varsome.com` | Kept frozen according to schedule            |
| Staging | `https://staging-api.varsome.com` | Test environment, throttled |

For more information on the different servers, [read here](https://docs.varsome.com/en/varsome-api-environments).

Use the `-u` flag to select a non-default server.

> **Note:** The staging environment is intended for evaluation only. It may contain a
> partial dataset, is throttled, and may produce different results from production.

---

## Quick-start: command-line tools

### Annotate a single variant

```bash
varsome_api_run -g hg19 -k YOUR_API_KEY -q 'chr7-140453136-A-T' -p add-all-data=1
```

### Annotate multiple variants in one call

```bash
varsome_api_run -g hg19 -k YOUR_API_KEY \
  -q 'chr7-140453136-A-T' 'chr19:20082943:1:G' \
  -p add-source-databases=gnomad-exomes,refseq-transcripts
```

### Annotate variants from a text file (one variant per line)

```bash
varsome_api_run -g hg19 -k YOUR_API_KEY -i variants.txt -o annotations.json -p add-all-data=1
```

### Look up gene information

```bash
varsome_api_run -y genes -g hg19 -k YOUR_API_KEY -q BRCA1 TP53
```

```bash
varsome_api_run -y genes -g hg19 -k YOUR_API_KEY -i genes.txt -o gene_annotations.json
```

### Look up CNV information

```bash
varsome_api_run -y cnvs -g hg19 -k YOUR_API_KEY -q 'chr1:122:5235:DEL' 'chr1:100:L1254:DUP'
```

```bash
varsome_api_run -y cnvs -g hg19 -k YOUR_API_KEY -i cnvs.txt -o cnv_annotations.json
```


Output defaults to stdout. Use `-o` to write to a file.
The output is always written in [JSON Lines](https://jsonlines.org) format —
one JSON object per line — regardless of whether you write to a file or stdout.
See [Output format: JSON Lines](#output-format-json-lines-breaking-change-from-v0x)
for details and migration guidance.

### Annotate a VCF file

```bash
varsome_api_annotate_vcf -g hg19 -k YOUR_API_KEY -i input.vcf -o annotated.vcf -p add-all-data=1
```

> **VCF annotation limitation:** `varsome_api_annotate_vcf` supports SNPs and small
> indels (up to 200 bp). Remove any variants outside these criteria before running.

### Common CLI flags

| Flag | Description | Default |
|------|-------------|---------|
| `-k` | API key (required) | — |
| `-g` | Reference genome: `hg19` or `hg38` | `hg19` |
| `-y` | Query type: `variants`, `genes`, or `cnvs` | `variants` |
| `-p` | Request parameters as `key=value` pairs | `add-ACMG-annotation=1` |
| `-u` | API server URL | `https://api.varsome.com` |
| `-t` | Max concurrent requests (1–20) | `5` |
| `-m` | Max items per batch request | `100` |
| `-v` / `--verbose` | Enable debug-level logging | off |

> **Batch limits:** The `-m` parameter specifies the maximum number of items
> (variants or genes) per batch request. The API enforces per-environment limits:
> - **Live / Stable**: Variants: 200, Genes: 100
> - **Staging**: Variants: 50, Genes: 10
>
> If you exceed the environment's limit, the API will return an error. Adjust `-m`
> accordingly. CNV queries do not support batching and are always sent individually.

Run any tool with `--help` for the full option reference.

---

## Output format: JSON Lines (breaking change from v0.x)

`varsome_api_run` v1.x writes all output — to a file or to stdout — in
**[JSON Lines](https://jsonlines.org)** (JSONL) format: one self-contained JSON
object per line, with no surrounding array wrapper.

This is a **breaking change** from v0.x, which wrote the output file as a single
JSON array.

### v0.x — old format (JSON array)

The old output file looked like this:

```json
[
  {"chromosome": "7", "pos": 140453136, "ref": "A", "alt": "T", ...},
  {"chromosome": "19", "pos": 20082943, "ref": "1", "alt": "G", ...}
]
```

Users would load the entire file at once and iterate the resulting list:

```python
# v0.x — old approach
import json

with open("annotations.json") as f:
    annotations = json.load(f)  # parses the whole file as a JSON array

for annotation in annotations:
    print(annotation["chromosome"], annotation["pos"])
```

### v1.x — new format (JSON Lines)

The new output file looks like this:

```jsonl
{"alt": "T", "chromosome": "7", "pos": 140453136, "ref": "A", ...}
{"alt": "G", "chromosome": "19", "pos": 20082943, "ref": "1", ...}
```

Each line is an independent, complete JSON object. Read the file **line by line**
and parse each line separately:

```python
# v1.x — new approach
import json

with open("annotations.jsonl") as f:
    for line in f:
        annotation = json.loads(line)  # parse one object at a time
        print(annotation["chromosome"], annotation["pos"])
```

> ⚠️ **`json.load(f)` will fail** on a JSONL file because the file as a whole is
> not valid JSON. Always use `json.loads(line)` inside a loop.

### Why the change?

The JSONL format allows results to be streamed and written **as they arrive** from
the API, keeping memory usage constant regardless of how many variants are
annotated. The old array format required buffering all results in memory before
writing, which was impractical for large variant sets.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Developer Guide](docs/developer-guide.md) | Using `VarSomeAPIClient` and `VCFAnnotator` in your Python code |
| [Docker Guide](docs/docker.md) | Running the tools via the pre-built Docker image or building your own |

---

## How to get an API key

[Contact support](mailto:support@saphetor.com) to register for an API key.

An API key is required for all CLI operations and for batch lookups.
Single-variant lookups via `VarSomeAPIClient` do not require a key, but will be throttled.

---

## API documentation

See [api.varsome.com](https://api.varsome.com) for available request parameters and
the full response schema. The OpenAPI specification is available at
`https://api.varsome.com/openapi/variants/`.

---

## Contributing & running the tests

See the [Developer Guide](docs/developer-guide.md) for instructions on cloning
the repository, setting up a development environment, and running the test suite.
