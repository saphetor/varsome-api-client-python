#!/bin/bash

# This script exctract individual variants from vcf file
# in a list of fromat chr-pos-ref-alt.

# Script is aware of heterozygous vcf mutation sites,
# where there are two different alt alleles present.

input_file=$1

grep --invert-match '#' $input_file | \
awk '
BEGIN { FS = "\t" }
{
    chr=$1;
    pos=$2;
    ref=$4;
    alt=$5;

    #If there are two alt alleles (separated by comma),
    #split them in two variant recors, avoid "*" alleles.
    if (alt ~ /,/) {
        split(alt, alt_alleles, ",");
        if (alt_alleles[1]!="*")
            print chr"-"pos"-"ref"-"alt_alleles[1];
        if (alt_alleles[2]!="*")
            print chr"-"pos"-"ref"-"alt_alleles[2];
    }
    else {
        print chr"-"pos"-"ref"-"alt;
    }
}'