#!/usr/bin/env python3

# A simple client application that does the following:
# - Loads a text file containing one variant per row
# - Performs a batch lookups to the Saphetor Variant API using N variants at a time. 
# - Saves the results in a new file.
#
# It uses the following module:
# variantapi.client (https://github.com/saphetor/variant-api-client-python)
#
# Note: To sort output json file execute:
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

# Declare reference genome as a global variable
_ref_genome = 1019


def main(argv):
	# Read and parse arguments
	infile = ''
	outfile = ''
	batch_size = 5000

	parser = argparse.ArgumentParser(description='Simple batch lookup Client application')
	parser.add_argument('-i', help='Input file', type=str, metavar='Input File', required=True)
	parser.add_argument('-o', help='Output file', type=str, metavar='Output File', required=True)
	parser.add_argument('-n', help="Number of variants to batch", type=int, metavar='Batch size', required=True,default=5000)
	parser.add_argument('-k', help='Your key to the API', type=str, metavar='API Key', required=False)
	parser.add_argument('-g', help='Reference genome either 1019 (default) or 1038', type=int, 
		metavar='Reference Genome', required=False, default=1019)

	args = parser.parse_args()
	infile = args.i
	outfile = args.o
	batch_size = args.n if args.n is not None else batch_size
	api_key = args.k
	ref_genome = args.g if args.g is not None else _ref_genome

	# Open and load input file into list
	print("Reading input file ", infile)
	with open(infile) as fi:
		variants = fi.readlines()
	variants = [v.strip('\n') for v in variants]

	# Prepare output for writing.
	print("Opening output file ", outfile)
	fo = open(outfile,'w')

	# Initialize client connection to API
	api = VariantAPIClient(api_key)
	if (api is None):
		print("Failed to connect to API")
		sys.exit()

	batch_counter = 0
	finished = False
	while not finished:
		start_index = batch_counter*batch_size
		end_index = (batch_counter+1)*batch_size
		if (end_index > len(variants)):
			end_index = len(variants)
			finished = True
		print(start_index, ":", end_index-1)
		batch_variants = variants[start_index:end_index]
		print("Lookup for: ", batch_variants, "with ref_genome= ", ref_genome)
		batch_data = api.batch_lookup(batch_variants, ref_genome=ref_genome)

		fo.write(json.dumps(batch_data, indent=2))
		batch_counter += 1

	print ("Finished ", batch_counter, " batch lookups")

if __name__ == '__main__':
    main(argv)
