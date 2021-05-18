################## BASE IMAGE ######################
FROM continuumio/miniconda3@sha256:456e3196bf3ffb13fee7c9216db4b18b5e6f4d37090b31df3e0309926e98cfe2 

################## METADATA ######################
LABEL software="" \
      version="" \
      software.version="" \
      about.home="" \
      maintainer="Vladyslav Dembrovskyi <vlad@lifebit.ai>"

################## INSTALLATION ######################
USER root

ENV PATH /opt/conda/bin:$PATH

ARG ENV_NAME="base"

RUN apt-get update -y \
  && apt-get install procps -y \
  && rm -rf /var/lib/apt/lists/*

COPY environment.yml /
RUN conda env update -n ${ENV_NAME} -f environment.yml && conda clean -a

# Add conda installation dir to PATH (instead of doing 'conda activate')
ENV PATH /opt/conda/envs/${ENV_NAME}/bin:$PATH

# Dump the details of the installed packages to a file for posterity
RUN conda env export --name ${ENV_NAME} > ${ENV_NAME}_exported.yml

# Initialise bash for conda
RUN conda init bash

WORKDIR /data/

CMD ["bash"]
