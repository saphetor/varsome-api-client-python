FROM continuumio/miniconda3@sha256:456e3196bf3ffb13fee7c9216db4b18b5e6f4d37090b31df3e0309926e98cfe2

LABEL description="Docker image containing all requirements for lifebit-ai/varsome-api-client-python"

RUN apt-get update -y  \ 
    && apt-get install -y wget zip procps libxt-dev p7zip-full \
    && rm -rf /var/lib/apt/lists/*

COPY environment.yml /
RUN conda env create -f /environment.yml && conda clean -a
ENV PATH /opt/conda/envs/varsome-api-client-python/bin:$PATH

RUN mkdir /opt/bin
COPY bin/* /opt/bin/

RUN find /opt/bin/ -type f -iname "*.py" -exec chmod +x {} \; && \
    find /opt/bin/ -type f -iname "*.R" -exec chmod +x {} \; && \
    find /opt/bin/ -type f -iname "*.sh" -exec chmod +x {} \; && \
    find /opt/bin/ -type f -iname "*.css" -exec chmod +x {} \; && \
    find /opt/bin/ -type f -iname "*.Rmd" -exec chmod +x {} \;

ENV PATH="$PATH:/opt/bin/"