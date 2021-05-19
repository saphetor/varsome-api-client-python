#!/usr/bin/python3

# This python script extracts variants from VarSome Clinical API results .josn and transforms into csv


import pandas as pd
import argparse
import json


### Input arguments

parser = argparse.ArgumentParser(description='This script is used to run convert json file to csv table.')

# Input file
parser.add_argument("-i", "--input", help="Input json file to convert, required.", required=True)

# Output file
parser.add_argument("-o", "--output", default="", help="Output file. Default: <basename>_main_table.csv .")

args = parser.parse_args()
input_file     = args.input
output_file    = args.output
if (output_file == ""):
    output_file = input_file.rsplit(".",1)[0] + "_main_table.csv"


### Extract variants

with open(input_file, 'r') as json_file:
    data = json.load(json_file)



# Convert json (array) to df with unnesting all nested annotations into separate columns of data frame
#NOTE: this fully doesn't unnest items that have arrays in them, e.g. gnamad_genomes, ensembl_transcripts, etc.
df = pd.json_normalize(data)

# Write entire annotaion data frame to csv file
#df.to_csv(output_file, index = False, header=True)


### Save only data needed for first iteration report table

def shorten_indel(indel):
    if len(indel) >= 5:
        return f'{indel[:2]}..{indel[-2:]} ({len(indel)})'
    else:
        return indel

def label_variant(row):
    if not row['ref'] : #insertion
        return f'{row["chromosome"]}:{row["pos"]-1}_{row["pos"] % 10} ins{shorten_indel(row["alt"])}'
    elif not row['alt'] : #deletion
        return f'{row["chromosome"]}:{row["pos"]} del{shorten_indel(row["ref"])}'
    else: #SNP
        return f'{row["chromosome"]}:{row["pos"]} {row["ref"]}⇒{row["alt"]}'

# Creating missing cols

df['variant_label'] = df.apply (lambda row:  label_variant(row), axis=1)
df['hgvs_full'] = df.apply (lambda row:  row['acmg_annotation.transcript'] + ":" + str(row['refseq_transcripts'][0]['items'][0]['hgvs']), axis=1)
df['tr_position'] = df.apply (lambda row:  str(row['refseq_transcripts'][0]['items'][0]['location']), axis=1)

main_table_cols = {
    'variant_label':'Variant',
    'variant_type':'Variant type',
    'acmg_annotation.coding_impact':'Coding impact',
    'acmg_annotation.gene_symbol':'Gene Symbol',
    'acmg_annotation.verdict.ACMG_rules.verdict':'ACMG Class',
    'acmg_annotation.verdict.classifications':'ACMG Rules',
    'hgvs_full':'HGVS',
    'tr_position':'Transcript position',
#    'overlapping_genes':'Overlapping Genes',
#    'cgd_inheritance':'Inheritance',
#    'variant_function':'Variant function',
#    'zygosity':'Zygosity',
#    'frequency':'Frequency',
#    'allelic_balance':'Allelic balance',
#    'coverage':'Coverage'
}

# Select and rename columns
df = df[list(main_table_cols.keys())]
df = df.rename(columns=main_table_cols)

# Reformatting existing columns
## Unlist ACMG rules list to print without quotes and commas to the table
df.loc[:,'ACMG Rules'] = df.apply (lambda row: " ".join(row['ACMG Rules']), axis=1)
## Make VarSome zygosity codes match logic: 2 for homozygous, 1 heterozygous
#df2['Zygosity'] = df2.apply (lambda row:  row['Zygosity'] - 1, axis=1)

df.to_csv(output_file, index = False, header=True)

