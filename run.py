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
    parser.add_argument('-g', help='Reference genome either 1019 or 1038', type=int, metavar='Reference Genome',
                        required=False, default=1019)
    parser.add_argument('-q',
                        help='Query to lookup in the API e.g. chr19:20082943:1:G or in case of batch request '
                             'e.g. chr19:20082943:1:G rs113488022',
                        type=str, metavar='Query', required=True, nargs='+')
    args = parser.parse_args()
    api_key = args.k
    query = args.q
    ref_genome = args.g
    api = VariantAPIClient(api_key)
    if len(query) == 1:
        result = api.lookup(query[0], ref_genome=ref_genome)
    else:
        if api_key is None:
            sys.exit("You need to pass an api key to perform batch requests")
        result = api.batch_lookup(query, ref_genome=ref_genome)
    sys.stdout.write(json.dumps(result, indent=4, sort_keys=True) if result else "No result")
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
