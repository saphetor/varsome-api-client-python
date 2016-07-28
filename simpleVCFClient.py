#!/usr/bin/env python3

# A simple client application that load the following:
# - Loads a VCF file,
# - For each entry in the file, performs a call to the Saphetor Variant API
# - Extends the VCF description to include gene information for each entry
# - Saves the result, including the gene information (a comma-separated list of gene symbols for each variant) in a new file in the VCF format.
#
# It uses the following modules:
# pyVCF (http://pyvcf.readthedocs.io/en/latest/) 
# variantapi.client (https://github.com/saphetor/variant-api-client-python)

import argparse
import json
import logging
import vcf
import sys, getopt
import re
from sys import argv
from variantapi.client import VariantAPIClient
from vcf.parser import _Info as VcfInfo, field_counts as vcf_field_counts

# Declare reference genome as a global variable
_ref_genome = 1019

# Declare the limit of variants to lookup in each batch
_batch_limit = 3 

def main(argv):
	# Read script arguments
	infile = ''
	outfile = ''
	no_batch = False
	input_error = False

	parser = argparse.ArgumentParser(description='Simple VCF Client application')
	parser.add_argument('-i', help='Input VCF file', type=str, metavar='Input File', required=True)
	parser.add_argument('-o', help='Output VCF file', type=str, metavar='Output File', required=True)
	parser.add_argument('-k', help='Your key to the API', type=str, metavar='API Key', required=False)
	parser.add_argument('-g', help='Reference genome either 1019 (default) or 1038', type=int, metavar='Reference Genome',
                        	required=False, default=1019)
	parser.add_argument('-nb', help="Do not do batch requests", action='store_true')

	args = parser.parse_args()
	infile = args.i
	outfile = args.o
	api_key = args.k
	ref_genome = args.g if args.g is not None else _ref_genome
	no_batch = args.nb

	# Open and load vcf file into vfc reader
	print ("Reading input file ", infile)
	vcf_reader = vcf.Reader(filename=infile, encoding='utf8')

	# Add a new GENE info field in the metadata description, so that we may store such data for each record
	vcf_reader.infos['GENE'] = VcfInfo( 'GENE', ".", 'String', 'Concatenated list of GENE sumbols',"","")
	
	# Prepare output for writing.
	print ("Opening output file ", outfile)
	vcf_writer = vcf.Writer(open(outfile, 'w'), vcf_reader, lineterminator='\n')
	
	# An array to hold the variant descriptions for the batch lookup.
	batch_variant_array = []
	
        # An array to hold all the records that will be used for each batch lookup
	batch_records = []

	# Count rows processed
	counter = 0

	print("Start parsing input file")
	# Iterate throught all the records read from the input vcf file
	while True:
		try: 
			record = next(vcf_reader)

			# Prepare a variant description string for this record
			variant_string = record.CHROM + ":" + str(record.POS) + ":"
			if (record.REF is not None):
				variant_string += str(record.REF)
			variant_string += ":"
			if (record.ALT is not None):
				variant_string += str(record.ALT[0])
                	# XXX Note that here we assume a single variant per row, i.e. the ALT value will be an array with just one element. Must make this more generic to allow
			# XXX multiple values per row, in whcih case ALT would be an array with more elements, e.g. ALT=["A", "CCT", "C"]
			# XXX Such a row would give rise to more than one rows in the output VCF file produced.

		except StopIteration as e:
			# Reached end of input VCF file, no new record was read
			record = None

		# If we are performing batch lookups...
		if (not no_batch):
			# Add new record (if it exists) and resulting variant description to batch arrays:
			if (record is not None):
				batch_records.append(record)
				batch_variant_array.append(variant_string)

			# Check if we  have reached the limit of variants for the batch request, or the end of the input file.
			if (len(batch_variant_array) == _batch_limit or record is None):
				# Execute request, process the output and write resulting records in the output VCF file.
				api = VariantAPIClient(api_key)
				batch_data = api.batch_lookup(batch_variant_array, ref_genome=ref_genome)
		
				# Process response, variant by variant
				batch_counter = 0
				for data in batch_data:
					process_single_variant_response_data(batch_records[batch_counter], data, vcf_writer)
					batch_counter += 1
		
				if (record is not None):
					# Reset arrays
					batch_records = []
					batch_variant_array = []
				else:
					# Reached the end of the file, finish
					break

		# If we are performing individual lookups for each variant (which is not recommended for performance issues), execute the lookup now and process the outcome
		else: 
			if (record is not None):
				# Perform a single variant, process the output, and write the resulting record in the ouput VCF file.
				api = VariantAPIClient(api_key)
				data = api.lookup(variant_string, ref_genome=ref_genome)
				process_single_variant_response_data(record, data, vcf_writer)
			else:
				# Reached the end of the file, finish
				break

		counter += 1 
		if (counter % 1000 == 0):
			print ("Read ", counter, " rows")

	print ("Finished reading ", counter, " rows, exiting")
	
def process_single_variant_response_data(record, data, vcf_writer):
	
	# Check whether there is a field containing gene information in the response.
	if ('genes' in data.keys()):
		# Concatenate all gene symbols into a comma-separated string
		gene_str = ""
		for g in data['genes'][:-1]:
			gene_str = gene_str + g['symbol'] + ","
		gene_str = gene_str + data['genes'][-1]['symbol']
		# Add gene entry in the INFO field, containing the string.
		record.INFO['GENE'] = gene_str
			
	# Write the record in the output vcf file.
	vcf_writer.write_record(record)


if __name__ == '__main__':
    main(argv)
