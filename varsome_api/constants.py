from typing import Literal, get_args

RefGenome = Literal["hg19", "hg38"]
DEFAULT_REF_GENOME = "hg19"
REFERENCE_GENOMES = get_args(RefGenome)

QueryType = Literal["variants", "genes", "cnvs"]
DEFAULT_QUERY_TYPE = "variants"
QUERY_TYPES = get_args(QueryType)
