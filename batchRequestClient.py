#!/usr/bin/env python3

# A simple client application that does the following:
# - Loads a text file containing one variant per row
# - Performs a batch lookups to the Saphetor Variant API using n variants at a time. 
# - Saves the results in a new file.
#
# It uses the following module:
# variantapi.client
# https://github.com/saphetor/variant-api-client-python
# 
# Note:
# To sort output json file execute:
# jq -S '.' output.txt  > output_sorted.txt

import argparse
import json
import logging
import re
import sys
import operator
from sys import argv
from variantapi.client import VariantAPIClient

__author__ = 'stephanos-androutsellis'

def main(argv):
    infile = ''
    outfile = ''

    parser = argparse.ArgumentParser(
        description='Simple batch lookup Client application. '
        )
    parser.add_argument('-i',
        help='Input file',
        type=str,
        metavar='Input File',
        required=True
        )
    parser.add_argument('-o',
        help='Output file',
        type=str,
        metavar='Output File',
        required=True
        )
    parser.add_argument('-n',
        help="Number of variants per GET request",
        type=int,
        metavar='Batch size',
        required=False,
        default=10000
        )
    parser.add_argument('-k',
        help='Your key to the API',
        type=str,
        metavar='API Key',
        required=False
        )
    parser.add_argument('-g',
        help='Reference genome either hg19 (default) or hg38',
        type=str,
        metavar='Reference Genome',
        required=False,
        default='hg19'
        )
    parser.add_argument('-p',
        help='Request parameters '
            'e.g. add-all-data=1 expand-pubmed-articles=0',
        type=str,
        metavar='Request Params',
        required=False,
        nargs='+'
        )

    args = parser.parse_args()
    infile = args.i
    outfile = args.o
    batch_size = args.n
    api_key = args.k
    ref_genome = args.g
    request_parameters = None
    if args.p:
        request_parameters = {param[0]: param[1] for param in [
            param.split("=") for param in args.p
            ]
        }

    # Open and load input file into list
    print("Reading input file ", infile)
    with open(infile) as fi:
        variants = fi.readlines()
    variants = [v.strip('\n') for v in variants]

    # Initialize client connection to API
    api = VariantAPIClient(api_key, max_variants_per_batch=batch_size)
    if (api is None):
        print("Failed to connect to API")
        sys.exit()

    print("posting GET requests... ", end='')
    results = api.batch_lookup(
        variants,
        params=request_parameters,
        ref_genome=ref_genome
        )
    print("done")

    print("writing output file ", outfile)
    with open (outfile, 'w') as fo:
        fo.write(json.dumps(results, indent=4))

if __name__ == '__main__':
    main(argv)
