#!/usr/bin/env python3

# A simple client application that does the following:
# - Loads a VCF file,
# - For each entry in the file, performs a lookup to the Saphetor Variant API. 
#   The call can be either in batch mode (the default and more efficient way, 
#   sending a number of variants at a time), or one by one. 
# - Extends the VCF description to include gene information for each entry that
#   is retreived from the response received from the API.
# - Saves the result, including the gene information (a comma-separated list of 
#   gene symbols for each variant) in a new file in the VCF format.
#   Note that if a row in the input VCF file contains more than one ALT field 
#   entries, i.e. corresponds to more than one variants, we'll be storing one
#   row per variant in the output VCF file.
#
# It uses the following modules:
# pyVCF (http://pyvcf.readthedocs.io/en/latest/) 
# variantapi.client (https://github.com/saphetor/variant-api-client-python)

import argparse
import json
import logging
import vcf
import re
import sys
from sys import argv
from variantapi.client import VariantAPIClient
from vcf.parser import _Info as VcfInfo, field_counts as vcf_field_counts

__author__ = 'stephanos-androutsellis'

# Declare reference genome as a global variable
_ref_genome = 1019

# Declare the limit of variants we want to lookup in each batch request
_batch_limit = 3 


# A class to store variant lookup data:
# - The record from the input VCF file
# - The variant string
# - The corresponding ALT value (convenient for multi-variant records)
class Variant_lookup_data(object):
    vcf_record = None
    variant_string = ""
    alt_value = ""

    # The class constructor/initializer 
    def __init__(self,vcf_record,variant_string,alt_value):
        self.vcf_record=vcf_record
        self.variant_string=variant_string
        self.alt_value=alt_value


def main(argv):
	# Read and parse arguments
	infile = ''
	outfile = ''
	do_batch_lookups = True
	input_error = False

	parser = argparse.ArgumentParser(description='Simple VCF Client application')
	parser.add_argument('-i', help='Input VCF file', type=str, metavar='Input File', required=True)
	parser.add_argument('-o', help='Output VCF file', type=str, metavar='Output File', required=True)
	parser.add_argument('-k', help='Your key to the API', type=str, metavar='API Key', required=False)
	parser.add_argument('-g', help='Reference genome either 1019 (default) or 1038', type=int, 
		metavar='Reference Genome', required=False, default=1019)
	parser.add_argument('-nb', help="Do not do batch requests", action='store_true')

	args = parser.parse_args()
	infile = args.i
	outfile = args.o
	api_key = args.k
	ref_genome = args.g if args.g is not None else _ref_genome
	do_batch_lookups = not args.nb

	# Open and load vcf file into vfc reader object
	print ("Reading input file ", infile)
	vcf_reader = vcf.Reader(filename=infile, encoding='utf8')

	# Add a new GENE info field in the metadata description, so that we may store such data for each record
	vcf_reader.infos['GENE'] = VcfInfo( 'GENE', ".", 'String', 'Concatenated list of GENE sumbols',"","")
	
	# Prepare output for writing.
	print ("Opening output file ", outfile)
	vcf_writer = vcf.Writer(open(outfile, 'w'), vcf_reader, lineterminator='\n')

	# Declare an array of Variant_lookup_data objects to hold data for executing the
	# lookups and process its outcome.
	variant_lookup_data_array = []

	# A counter for the total number of rows processed thus far
	total_counter = 0

	# Initialize client connection to API
	api = VariantAPIClient(api_key)
	if (api is None):
		print("Failed to connect to API")
		sys.exit()

	print("Start parsing input file")

	# Iterate throught all the records read from the input VCF file
	while True:
		try: 
			# Get next record (corresponds to a data row in the file)
			vcf_record = next(vcf_reader)

			# A vcf_record (i.e. row in the VCF file) may correspond to more than one variants, if it contains 
			# more than one ALT values. We generate a Variant_lookup_data record for each variant,
			# and add them to the variant_lookup_data_array. 
			# Note: A reference to the same "vcf_record" object will be stored in each Variant_lookup_data record,
			#       however the "alt" field will contain a different ALT value.
			variant_lookup_data_from_vcf_record(vcf_record, variant_lookup_data_array)

		except StopIteration as e:
			# Reached end of input VCF file, no new vcf_record was read
			vcf_record = None

		# If we are performing batch lookups...
		if (do_batch_lookups):
			# Check if we have reached (or slightly crossed) the limit of variants we want for the batch request, or the end of the input file.
			# Note: In this implementation we may cross the limit if the last vcf_record read contained more than one variants. This is OK.
			if (len(variant_lookup_data_array) >= _batch_limit or vcf_record is None):
				# Extract variant strings from array.
				variant_string_array = [vld.variant_string for vld in variant_lookup_data_array]

				# Execute batch lookup request
				batch_data = api.batch_lookup(variant_string_array, ref_genome=ref_genome, params={ 'add-all-data': 1 })
		
				# Process response, variant by variant
				batch_counter = 0
				for data in batch_data:
					process_single_variant_response_data(variant_lookup_data_array[batch_counter], data, vcf_writer)
					batch_counter += 1
		
				# Clear array
				del variant_lookup_data_array[:]

				if (vcf_record is None):
					# Reached the end of the file, finish
					break

		# If we are performing individual lookups for each variant (which is not recommended for performance issues), 
		# execute the lookup and process the outcome
		else: 
			if (vcf_record is not None):
				# Execute lookup requests for each element in the array
				for vld in variant_lookup_data_array:
					data = api.lookup(vld.variant_string, ref_genome=ref_genome)
					process_single_variant_response_data(vld, data, vcf_writer)

				# Clear array
				del variant_lookup_data_array[:]
			else:
				# Reached the end of the file, finish
				break

		total_counter += 1 
		if (total_counter % 1000 == 0):
			print ("Read ", total_counter, " rows")

	print ("Finished reading ", total_counter, " rows, exiting")



# Processes a vcf_record from the input VCF file, creates Variant_lookup_data objects for the variants
# in the vcf_record, and appends them to the array variant_lookup_data_array that keeps such objects
# for the current lookup. 
# Input:
#    vcf_record: The record read from the input VCF file
#    variant_lookup_data_array: An array of Variant_lookup_data objects for the current lookup.
# Output:
#    None as such, but new elements are appended to the input array variant_lookup_data_array
def variant_lookup_data_from_vcf_record(vcf_record, variant_lookup_data_array):
	# Concatenate chromosome, position and reference, separated by ":" characters
	variant_chromposref = vcf_record.CHROM + ":" + str(vcf_record.POS) + ":"
	if (vcf_record.REF is not None):
		variant_chromposref += str(vcf_record.REF)
	variant_chromposref += ":"
	
	# For each ALT element, generate a new string and append to the array
	if (vcf_record.ALT is not None):
		for alt in vcf_record.ALT:
			variant_string = variant_chromposref + str(alt)
			variant_lookup_data = Variant_lookup_data(vcf_record,variant_string,alt)
			variant_lookup_data_array.append(variant_lookup_data)
	else:
		variant_lookup_data = Variant_lookup_data(vcf_record,variant_chromposref,vcf_record.ALT)
		variant_lookup_data_array.append(variant_lookup_data)


# Processes a single variant description vcf_record and writes the resulting new record in the output VCF file
# Input:
#  variant_lookup_data: A Variant_lookup_data object corresponding to the variant being queried.
#  response_data: The data received from the variant API for this specific record. Note that if the record contained more than one
#        elements in the ALT field, and thus corresponded to more than one variants, we query the variant API once for each 
#        variant. 
#  vcf_writer: The output VCF file handler object
# Output:
#    None
def process_single_variant_response_data(variant_lookup_data, response_data, vcf_writer):
	# Try to extract the gene_data information from the response
	gene_symbols = set()
	if 'refseq_transcripts' in response_data.keys() and response_data['refseq_transcripts']:
		for t in response_data['refseq_transcripts'][0]['items']:
			if 'gene_symbol' in t and t['gene_symbol']:
				gene_symbols.add(t['gene_symbol'])
	if 'ensembl_transcripts' in response_data.keys() and response_data['ensembl_transcripts']:
		for t in response_data['ensembl_transcripts'][0]['items']:
			if 'gene_symbol' in t and t['gene_symbol']:
				gene_symbols.add(t['gene_symbol'])

	if gene_symbols:
		# Concatenate all gene symbols into a comma-separated string
		gene_str = ','.join(gene_symbols)

		# Add gene entry in the INFO field, containing the string.
		variant_lookup_data.vcf_record.INFO['GENE'] = gene_str

	# Assign the correct ALT value to the vcf_record for this variant.
	variant_lookup_data.vcf_record.ALT = [variant_lookup_data.alt_value]

	# Write the record in the output vcf file.
	vcf_writer.write_record(variant_lookup_data.vcf_record)


if __name__ == '__main__':
    main(argv)
