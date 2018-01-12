#!/usr/bin/env python3
import argparse
import sys

from varsome_api.vcf import VCFAnnotator

__author__ = 'ckopanos'


def annotate_vcf(argv):
    parser = argparse.ArgumentParser(description='VCF Annotator command line')
    parser.add_argument('-k', help='Your key to the API', type=str, metavar='API Key', required=True)
    parser.add_argument('-g', help='Reference genome either hg19 or hg38', type=str, metavar='Reference Genome',
                        required=False, default='hg19')
    parser.add_argument('-i',
                        help='Path to vcf file',
                        type=str, metavar='Input VCF File', required=True)
    parser.add_argument('-o',
                        help='Path to output vcf file',
                        type=str, metavar='Output VCF File', required=False)
    parser.add_argument('-p',
                        help='Request parameters e.g. add-all-data=1 expand-pubmed-articles=0',
                        type=str, metavar='Request Params', required=False, nargs='+')
    parser.add_argument('-t', help='Run vcf annotator using x threads', type=int, default=3, required=False,
                        metavar='Number of threads')
    args = parser.parse_args()
    api_key = args.k
    vcf_file = args.i
    output_vcf_file = args.o
    ref_genome = args.g
    num_threads = args.t
    request_parameters = None
    if args.p:
        request_parameters = {param[0]: param[1] for param in [param.split("=") for param in args.p]}
    vcf_annotator = VCFAnnotator(api_key=api_key, ref_genome=ref_genome, get_parameters=request_parameters,
                                 max_threads=num_threads)
    vcf_annotator.annotate(vcf_file, output_vcf_file)


if __name__ == "__main__":
    annotate_vcf(sys.argv[1:])
