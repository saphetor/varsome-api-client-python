#!/usr/bin/env python
import argparse
import json
import logging
import sys

from variantapi.client import VariantAPIClient
from variantapi.vcf import VCFAnnotator

__author__ = 'ckopanos'
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s]	%(threadName)s	%(message)s',
                    )


def main(argv):
    parser = argparse.ArgumentParser(description='VCF Annotator command line')
    parser.add_argument('-k', help='Your key to the API', type=str, metavar='API Key', required=True)
    parser.add_argument('-g', help='Reference genome either hg19 or hg38', type=str, metavar='Reference Genome',
                        required=False, default='hg19')
    parser.add_argument('-f',
                        help='Path to vcf file',
                        type=str, metavar='VCF File', required=True)
    parser.add_argument('-p',
                        help='Request parameters e.g. add-all-data=1 expand-pubmed-articles=0',
                        type=str, metavar='Request Params', required=False, nargs='+')
    args = parser.parse_args()
    api_key = args.k
    vcf_file = args.f
    ref_genome = args.g
    request_parameters = None
    if args.p:
        request_parameters = {param[0]: param[1] for param in [param.split("=") for param in args.p]}
    vcf_annotator = VCFAnnotator(api_key=api_key, ref_genome=ref_genome, get_parametes=request_parameters)
    vcf_annotator.annotate(vcf_file)


if __name__ == "__main__":
    main(sys.argv[1:])
