#!/usr/bin/env python
import argparse
import json
import logging
import sys

from variantapi.client import VariantAPIClient

__author__ = 'ckopanos'
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s]	%(threadName)s	%(message)s',
                    )


def main(argv):
    parser = argparse.ArgumentParser(description='Sample Variant API calls')
    parser.add_argument('-k', help='Your key to the API', type=str, metavar='API Key', required=False)
    parser.add_argument('-g', help='Reference genome either hg19 or hg38', type=str, metavar='Reference Genome',
                        required=False, default='hg19')
    parser.add_argument('-q',
                        help='Query to lookup in the API e.g. chr19:20082943:1:G or in case of batch request '
                             'e.g. chr19:20082943:1:G rs113488022',
                        type=str, metavar='Query', required=True, nargs='+')
    parser.add_argument('-p',
                        help='Request parameters e.g. add-all-data=1 expand-pubmed-articles=0',
                        type=str, metavar='Request Params', required=False, nargs='+')
    args = parser.parse_args()
    api_key = args.k
    query = args.q
    ref_genome = args.g
    request_parameters = None
    if args.p:
        request_parameters = {param[0]: param[1] for param in [param.split("=") for param in args.p]}
    api = VariantAPIClient(api_key)
    if len(query) == 1:
        result = api.lookup(query[0], params=request_parameters, ref_genome=ref_genome)
    else:
        if api_key is None:
            sys.exit("You need to pass an api key to perform batch requests")
        result = api.batch_lookup(query, params=request_parameters,  ref_genome=ref_genome)
    sys.stdout.write(json.dumps(result, indent=4, sort_keys=True) if result else "No result")
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
