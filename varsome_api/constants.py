from typing import Literal, get_args

RefGenome = Literal["hg19", "hg38"]
DEFAULT_REF_GENOME = "hg19"
REFERENCE_GENOMES = get_args(RefGenome)
