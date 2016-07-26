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
ref_genome = 1019

# Declare the limit of variants to lookup in each batch
batch_limit = 3 

def main(argv):
	# Read script arguments
	infile = ''
	outfile = ''
	do_batch = True
	input_error = False

	help_string = "Usage is:\n   simpleVCFClient.py <input VCF file name> <output VCF file name> [-nobatch]\n   where -nobatch instructs the script to execute single variant queries instead of batching them in groups, which is the default and more efficient way\n"
	if (len(sys.argv) == 3):
		infile = sys.argv[1]
		outfile = sys.argv[2]
	elif (len(sys.argv) == 4):
		infile = sys.argv[1]
		outfile = sys.argv[2]
		if (sys.argv[3] == "-nobatch"):
			do_batch = False
		else:
			input_error = True
	else:
		input_error = True
	
	if (input_error):
		print(help_string);
		sys.exit()

	print("Input VCF file:", infile)
	print("Output VCF file:", outfile)
	print("Do batch:", do_batch)
	
	# Open and load vcf file into vfc reader
	vcf_reader = vcf.Reader(filename=infile, encoding='utf8')

	# Add a new GENE info field in the metadata description, so that we may store such data for each record
	vcf_reader.infos['GENE'] = VcfInfo( 'GENE', ".", 'String', 'Concatenated list of GENE sumbols',"","")
	
	# Prepare output for writing.
	vcf_writer = vcf.Writer(open(outfile, 'w'), vcf_reader, lineterminator='\n')
	
	# Initialize a counter for the number of rows in each batch lookup.
	batch_counter = 0;

	# A string to hold the entire array of variant descriptions for the batch lookup.
	batch_variant_string = ""
	
        # An array to hold all the records that will be used for each batch lookup
	batch_records = []

	total_counter = 0
	# Iterate throught all the records read from the input vcf file:
	while True:
		try: 
			record = next(vcf_reader)
		except StopIteration as e:
			record = None


		if (record is not None):
			print ("Records read: ",total_counter)
			print ("Batch counter: ",batch_counter)
			total_counter += 1
			# Prepare a variant description string for lookup
			variant_string = record.CHROM + ":" + str(record.POS) + ":"
			if (record.REF is not None):
				variant_string += str(record.REF)
			variant_string += ":"
			if (record.ALT is not None):
				print (str(record.ALT[0]))
				variant_string += str(record.ALT[0])
                	# XXX Note that here we assume a single variant per row, i.e. the ALT value will be an array with just one element. Must make this more generic to allow
			# XXX multiple values per row, in whcih case ALT would be an array with more elements, e.g. ALT=["A", "CCT", "C"]
			# XXX Such a row would give rise to more than one rows in the output VCF file produced.

	
		# If we are performing individual lookups for each variant (which is not recommended for performance issues), execute the lookup now and process the outcome
		if (not do_batch and record is not None):
			print("Continuing non-batch execution")
			# Perform a single variant, process the output, and write the resulting record in the ouput VCF file.
			api = VariantAPIClient()
			data = api.lookup(variant_string, ref_genome=ref_genome)
			process_single_variant_response_data(record, data, vcf_writer)

		elif (not do_batch and record is None):
			print("Finished non-batch execution, exiting")
			break

		elif (record is None or batch_counter == batch_limit):
			print("Finished batch execution step")
			# We have reached the limit of variants to batch in the request, or the end of the input file
			# Execute request, process the output and write resulting records in the output VCF file
			api = VariantAPIClient()
			print (batch_variant_string)
			batch_data = api.batch_lookup(batch_variant_string, ref_genome=ref_genome)
			print(json.dumps(result, indent=4, sort_keys=True) if result else "No result")
	
			# Process response, variant by variant
			counter = 0
			for data in batch_data:
				process_single_variant_response_data(batch_records[counter], data, vcf_writer)
				counter += 1
	
			# Reset counter
			batch_counter = 0
			batch_records = []
		else:
			# Continue building the string for the batch lookup
			if (batch_counter > 0):
				batch_variant_string += " "
			batch_variant_string += variant_string
			batch_counter += 1
			batch_records.append(record)
			print("Continuing batch execution preparation with string:", batch_variant_string)

		# If we reached the end of the file, finish
		if (record is None):
			break


def process_single_variant_response_data(record, data, vcf_writer):
	
	# Check whether there is a field containing gene information in the response.
	if ('genes' in data.keys()):
		# Concatenate all gene symbols into a comma-separated string
		gene_str = ""
		for g in data['genes'][:-1]:
			gene_str = gene_str + g['symbol'] + ","
		gene_str = gene_str + data['genes'][-1]['symbol']
		print(gene_str)
		# Add gene entry in the INFO field, containing the string.
		record.INFO['GENE'] = gene_str
			
	# Write the record in the output vcf file.
	vcf_writer.write_record(record)


if __name__ == '__main__':
    main(argv)
