FROM python:3.14.3-slim-trixie AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libdeflate-dev \
 && rm -rf /var/lib/apt/lists/*


COPY . .
RUN pip install --no-cache-dir ".[vcf]"

FROM python:3.14.3-slim-trixie AS final

RUN apt-get update && apt-get install -y --no-install-recommends \
    libbz2-1.0 \
    liblzma5 \
    zlib1g \
    libcurl4 \
    libdeflate0 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=base /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p /app && chown appuser:appuser /app

WORKDIR /app
USER appuser


CMD ["varsome_api_run", "--help"]
