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
import sys
import re
from sys import argv
from variantapi.client import VariantAPIClient
from vcf.parser import _Info as VcfInfo, field_counts as vcf_field_counts

# Open and load vcf file into vfc reader
script, infile, outfile = argv
vcf_reader = vcf.Reader(filename=infile, encoding='utf8')

# Add a new GENE info field in the metadata description, so that we may store such data for each record
vcf_reader.infos['GENE'] = VcfInfo( 'GENE', ".", 'String', 'Concatenated list of GENE sumbols',"","")

# Prepare output for writing.
vcf_writer = vcf.Writer(open(outfile, 'w'), vcf_reader, lineterminator='\n')

# Declare reference genome
ref_genome = 1019

# For record (i.e. non-metadata row) in the input vcf file:
for record in vcf_reader:

    # Prepare a variant description string for lookup
    v = record.CHROM + ":" + str(record.POS) + ":" +  record.REF + ":"
    for elem in record.ALT:
       v = v + str(elem)

    # Prepare and execute a lookup call to the Variant API and obtain the response in json format
    api = VariantAPIClient()
    result = api.lookup(v, ref_genome=ref_genome)

    # XXX SHOULD BE THIS:
    data = json.load(result)
    # TEMPORARILY TEST WITH THIS:
    with open('j.json') as data_file:    
       data = json.load(data_file)

    # Check whether there is a field containing gene information in the response.
    if (data['genes'] is not None):
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
