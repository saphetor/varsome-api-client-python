#!/usr/bin/env python3

# Copyright 2018 Saphetor S.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import sys
import os

from varsome_api.client import VarSomeAPIClient

__author__ = 'ckopanos'


def annotate_variant():
    parser = argparse.ArgumentParser(description='Sample VarSome API calls')
    parser.add_argument('-k', help='Your key to the API', type=str, metavar='API Key', required=False)
    parser.add_argument('-g', help='Reference genome either hg19 or hg38', type=str, metavar='Reference Genome',
                        required=False, default='hg19')
    parser.add_argument('-q',
                        help='Query to lookup in the API e.g. chr19:20082943:1:G or in case of batch request '
                             'e.g. chr15-73027478-T-C rs113488022. Don\'t use it together with the -i option',
                        type=str, metavar='Query', required=False, nargs='+')
    parser.add_argument('-p',
                        help='Request parameters e.g. add-all-data=1 expand-pubmed-articles=0',
                        type=str, metavar='Request Params', required=False, nargs='+')
    parser.add_argument('-i',
                        help='Path to text file with variants. It should include one variant per line. Don\'t use it '
                             'together with the -q option',
                        type=str, metavar='Text/CSV File one line per variant', required=False)
    parser.add_argument('-o',
                        help='Path to output file to store variant annotations',
                        type=str, metavar='Output File with json entries', required=False)
    args = parser.parse_args()
    api_key = args.k
    query = args.q
    ref_genome = args.g
    input_file = args.i
    output_file = args.o
    if query and input_file:
        sys.stderr.write("Don't specify -i and -q options together. Use only one of them\n")
        sys.exit(1)
    if not query and not input_file:
        sys.stderr.write("Please either specify -i or -q options\n")
        sys.exit(1)
    if input_file and not os.path.exists(input_file):
        sys.stderr.write('File %s does not exist\n' % input_file)
        sys.exit(1)
    if output_file and os.path.exists(output_file):
        sys.stderr.write('File %s already exists\n' % output_file)
        sys.exit(1)
    request_parameters = None
    if args.p:
        request_parameters = {param[0]: param[1] for param in [param.split("=") for param in args.p]}
    api = VarSomeAPIClient(api_key)
    if query:
        if len(query) == 1:
            result = api.lookup(query[0], params=request_parameters, ref_genome=ref_genome)
        else:
            if api_key is None:
                sys.exit("You need to pass an api key to perform batch requests")
            result = api.batch_lookup(query, params=request_parameters, ref_genome=ref_genome)
        if output_file:
            write_f = open(output_file, 'w')
            json.dump(result, write_f, indent=4, sort_keys=True)
        else:
            sys.stdout.write(json.dumps(result, indent=4, sort_keys=True) if result else "No result")
            sys.stdout.write("\n")
        sys.exit(0)
    with open(input_file) as f:
        variants = f.read().splitlines()
    if variants:
        if len(variants) > 1000:
            sys.stdout.write('Too many variants.. Consider using annotate_vcf instead\n')
            sys.stdout.flush()
        write_f = None
        if output_file:
            write_f = open(output_file, 'w')
        try:
            if api_key is None:
                sys.stdout.write('Without an API key, variants will be annotated one a time, '
                                 'causing a 429 too many requests error after some time\n')
                sys.stdout.flush()
                results = []
                for variant in variants:
                    result = api.lookup(variant, params=request_parameters, ref_genome=ref_genome)
                    if not result:
                        result = {'error': 'Could not fetch annotations for %s' % variant}
                    results.append(result)
                if write_f is not None:
                    json.dump(results, write_f, indent=4, sort_keys=True)
                else:
                    sys.stdout.write(json.dumps(result, indent=4, sort_keys=True) if result else "No result")
                    sys.stdout.write("\n")
            else:
                result = api.batch_lookup(variants, params=request_parameters, ref_genome=ref_genome)
                if write_f is not None:
                    json.dump(result, write_f, indent=4, sort_keys=True)
                else:
                    sys.stdout.write(json.dumps(result, indent=4, sort_keys=True) if result else "No result")
                    sys.stdout.write("\n")
        except Exception as e:
            # several things might occur. This is to broad, but lets not keep open file handles
            sys.stderr.write(str(e))
            sys.stderr.write("\n")
            if write_f is not None:
                write_f.close()
            sys.exit(1)
    else:
        sys.stderr.write('No variants found in file %s\n' % input_file)
        sys.exit(1)


if __name__ == "__main__":
    annotate_variant()
