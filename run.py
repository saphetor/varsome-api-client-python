#!/usr/bin/env python
import argparse
import json
import sys
import os

from variantapi.client import VariantAPIClient

__author__ = 'ckopanos'


def annotate_variant(argv):
    parser = argparse.ArgumentParser(description='Sample Variant API calls')
    parser.add_argument('-k', help='Your key to the API', type=str, metavar='API Key', required=False)
    parser.add_argument('-g', help='Reference genome either hg19 or hg38', type=str, metavar='Reference Genome',
                        required=False, default='hg19')
    parser.add_argument('-q',
                        help='Query to lookup in the API e.g. chr19:20082943:1:G or in case of batch request '
                             'e.g. chr19:20082943:1:G rs113488022. Don\'t use it together with the -i option',
                        type=str, metavar='Query', required=False, nargs='+')
    parser.add_argument('-p',
                        help='Request parameters e.g. add-all-data=1 expand-pubmed-articles=0',
                        type=str, metavar='Request Params', required=False, nargs='+')
    parser.add_argument('-i',
                        help='Path to csv file with variants. It should include one variant per line. Don\'t use it '
                             'together with the -q option',
                        type=str, metavar='CSV File', required=False)
    parser.add_argument('-o',
                        help='Path to output file to store variant annotations',
                        type=str, metavar='CSV File', required=False)
    args = parser.parse_args()
    api_key = args.k
    query = args.q
    ref_genome = args.g
    input_file = args.i
    output_file = args.o
    if query and input_file:
        sys.stderr.write("Don't specify -i and -q options together. Use only one of them")
        sys.exit(1)
    if not query and not input_file:
        sys.stderr.write("Please either specify -i or -q options")
        sys.exit(1)
    if input_file and not os.path.exists(input_file):
        sys.stderr.write('File %s does not exist' % input_file)
        sys.exit(1)
    if output_file and not os.path.exists(output_file):
        sys.stderr.write('File %s already exists' % input_file)
        sys.exit(1)
    request_parameters = None
    if args.p:
        request_parameters = {param[0]: param[1] for param in [param.split("=") for param in args.p]}
    api = VariantAPIClient(api_key)

    if len(query) == 1:
        result = api.lookup(query[0], params=request_parameters, ref_genome=ref_genome)
    else:
        if api_key is None:
            sys.exit("You need to pass an api key to perform batch requests")
        result = api.batch_lookup(query, params=request_parameters, ref_genome=ref_genome)
    sys.stdout.write(json.dumps(result, indent=4, sort_keys=True) if result else "No result")
    sys.stdout.write("\n")


if __name__ == "__main__":
    annotate_variant(sys.argv[1:])
