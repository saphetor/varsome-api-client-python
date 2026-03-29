# Docker Guide

This guide covers running the VarSome API CLI tools via Docker — either using the
pre-built image from the GitHub Container Registry (GHCR) or building your own image
from source.

For CLI flag reference see the [root README](../README.md).
For using the library in Python code see the [Developer Guide](developer-guide.md).

---

## Pre-built image from GHCR

Images are built automatically on every release and pushed to the GitHub Container
Registry at:

```
ghcr.io/saphetor/varsome-api-client-python
```

### Available tags

| Tag | Description |
|-----|-------------|
| `1` | Latest `1.x` release (major) |
| `1.3` | Latest `1.3.x` patch (major.minor) |
| `1.3.0` | Exact release version |

Replace the version number with the release you want. See the
[GitHub releases page](https://github.com/saphetor/varsome-api-client-python/releases)
for all available versions.

### Pull the image

```bash
docker pull ghcr.io/saphetor/varsome-api-client-python:1
```

---

## Running `varsome_api_run` via Docker

### Annotate a single variant

```bash
docker run --rm \
  ghcr.io/saphetor/varsome-api-client-python:1 \
  varsome_api_run \
    -k YOUR_API_KEY \
    -g hg19 \
    -q 'chr7-140453136-A-T' \
    -p add-all-data=1
```

### Annotate multiple variants

```bash
docker run --rm \
  ghcr.io/saphetor/varsome-api-client-python:1 \
  varsome_api_run \
    -k YOUR_API_KEY \
    -g hg19 \
    -q 'chr7-140453136-A-T' 'chr19:20082943:1:G' \
    -p add-source-databases=gnomad-exomes,refseq-transcripts
```

### Read variants from a file, write output to a file

Mount the directory containing your input file and write output to the same mount:

```bash
docker run --rm \
  -v /path/to/your/data:/data \
  ghcr.io/saphetor/varsome-api-client-python:1 \
  varsome_api_run \
    -k YOUR_API_KEY \
    -g hg19 \
    -i /data/variants.txt \
    -o /data/annotations.json \
    -p add-all-data=1
```

Replace `/path/to/your/data` with the absolute path to the directory on your host
that contains `variants.txt`. The output file `annotations.json` will be written
to the same directory.

---

## Running `varsome_api_annotate_vcf` via Docker

Mount the directory containing your VCF and write the annotated output to the same
mount:

```bash
docker run --rm \
  -v /path/to/your/data:/data \
  ghcr.io/saphetor/varsome-api-client-python:1 \
  varsome_api_annotate_vcf \
    -k YOUR_API_KEY \
    -g hg19 \
    -i /data/input.vcf \
    -o /data/annotated.vcf \
    -p add-all-data=1
```

> **VCF limitation:** Only SNPs and small indels (≤ 200 bp) are supported.
> Remove other variant types from your VCF before running.

### Tune concurrency and batch size

Use `-t` to control how many API requests run in parallel and `-m` to set the
number of variants per batch:

```bash
docker run --rm \
  -v /path/to/your/data:/data \
  ghcr.io/saphetor/varsome-api-client-python:1 \
  varsome_api_annotate_vcf \
    -k YOUR_API_KEY \
    -g hg19 \
    -i /data/input.vcf \
    -o /data/annotated.vcf \
    -t 10 \
    -m 100 \
    -p add-source-databases=gnomad-exomes,refseq-transcripts
```

### Use the stable API server

Pass `-u` to target a different API server:

```bash
docker run --rm \
  -v /path/to/your/data:/data \
  ghcr.io/saphetor/varsome-api-client-python:1 \
  varsome_api_annotate_vcf \
    -k YOUR_API_KEY \
    -g hg19 \
    -u https://stable-api.varsome.com \
    -i /data/input.vcf \
    -o /data/annotated.vcf \
    -p add-all-data=1
```

---

## Building the image from source

Clone the repository and build locally:

```bash
git clone https://github.com/saphetor/varsome-api-client-python.git
cd varsome-api-client-python
docker build -t varsome-api-client-python .
```

Run using your locally built image — the usage is identical to the GHCR image:

```bash
docker run --rm \
  -v /path/to/your/data:/data \
  varsome-api-client-python \
  varsome_api_run \
    -k YOUR_API_KEY \
    -g hg19 \
    -q 'chr7-140453136-A-T' \
    -p add-all-data=1
```

### Multi-platform build (amd64 + arm64)

The official release workflow builds for both `linux/amd64` and `linux/arm64`.
To replicate this locally with Docker Buildx:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t varsome-api-client-python:local \
  --load \
  .
```

> **Note:** `--load` only works for single-platform builds. For multi-platform,
> use `--push` to push to a registry instead.

---

## Container notes

- The container runs as a non-root user (`appuser`) for security.
- The working directory inside the container is `/app`.
- The default command (`CMD`) is `varsome_api_run --help`, so running the image
  without arguments prints the help text.
- Input and output files must be mounted via `-v` — the container has no access
  to your host filesystem by default.
- The image is built with the `[vcf]` extra, so **pysam and its htslib runtime
  libraries are pre-installed**. No local build toolchain or system libraries
  are required on the host — this is why Docker is the recommended way for end
  users to run `varsome_api_annotate_vcf`.
