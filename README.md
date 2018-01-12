# Variant API Client

## A basic api client implementation for [api.varsome.com](https://api.varsome.com)

This client is still in beta but it is a good start to start playing around with the API.

### Python versions
Python version 3 is supported.

### Installation
It is advised that you create a python virtual environment instead of globally installing the library

There several ways to create a virtual environment but you can refer to [pip installation](https://pip.pypa.io/en/stable/installing/) and
[virtualenv installation](https://virtualenv.pypa.io/en/stable/installation/) to first install these 2 tools if you don't
have them already installed via a package manager (Linux) or HomeBrew (MacOS), etc.

To create a virtual env you can follow the [user guide](https://virtualenv.pypa.io/en/stable/userguide/) or simply run

    virtualenv -p path_to/python3 venv_dir_name
    
Activate the virtual environment

    source venv_dir_name/bin/activate


Finally to use the client either download or clone the repository from github and place the variantapi package
within your code, or do

    pip install https://github.com/saphetor/variant-api-client-python/archive/master.zip

The client will be installed within your virtual environment. Also 2 scripts called variantapi_run.py and 
variantapi_annotate_vcf.py will be available within your virtual environment $PATH

### Using the scripts to directly annotate a list of variants or a vcf file

#### Annotating a variant or list of variants
Try the following query to annotate a single variant:

    variantapi_run.py -g hg19 -q 'chr7-140453136-A-T' -p add-all-data=1

The script should complete without errors and display aprox 6,700 lines of data from dann, dbnsfp, ensemble_transcripts, gerp, gnomad_exomes, gnomad_exomes_coverage, icgc_somatic, ncbi_clinvar2, pub_med_articles, refseq_transcripts, sanger_cosmic_public, uniprot_variants, wustl_civic etc.
The script may also accept a txt file with variants (one per line) and an optional output file to store the
annotations to. It is advised that you don't use this script with a large number of variants but directly use
the client within your code.

    variantapi_run.py -g hg19 -k api_key -i variants.txt -o annotations.txt -p add-all-data=1
    
Will read variants from variants.txt and dump the annotations to annotations.txt. If you don't use the -k
parameter the script will do as many requests as the variants within variants.txt file and you will probably
end up with HTTP status code 429 (Too many requests) error.

#### Annotating a vcf file
To annotate a vcf file use:

    variantapi_annotate_vcf.py -g hg19 -k api_key -i input.vcf -o annotated_vcf.vcf -p add-all-data=1
    
Notice however that not all available annotations will be present in the annotated_vcf file. Only a subset
of the returned annotations will be available, when running this script. Have a look at "Using the client in your code" 
section on how to annotate a vcf file with the annotations that are of interest to you. 

### Using the client in your code

Using the api client is quite straightforward. Just install the api client package and from within
your code use

    from variantapi.client import VariantAPIClient
    # api key is not required for single variant lookups
    api_key = 'Your token'
    api = VariantAPIClient(api_key)
    # if you don't have an api key use
    # api = VariantAPIClient()
    # fetch information about a variant into a dictionary
    result = api.lookup('chr7-140453136-A-T', params={'add-source-databases': 'gnomad-exomes,refseq-transcripts'}, ref_genome='hg19')
    # access results e.g. the transcripts of the variant
    transcripts = result['refseq_transcripts']
    # fetch information for multiple variants
    variants = ['chr19:20082943:1:G','chr22:39777823::CAA']
    # results will be an array of dictionaries an api key will be required for this request
    results = api.batch_lookup(variants, params={'add-source-databases': 'gnomad-exomes,gnomad-genomes'}, ref_genome='hg19')
    # look at the python doc for batch_lookup method for additional parameters

If errors occur while using the client an exception will be thrown.
You may wish to catch this exception and proceed with your own code logic

    from variantapi.client import VariantAPIClient, VariantApiException
    api = VariantAPIClient()
    try:
       result = api.lookup('chr19:20082943:1:G', ref_genome='hg64')
    except VariantApiException as e:
        # proceed with your code flow e.g.
        print(e) # 404 (invalid reference genome)

To view available request parameters (used in the params method parameter) refer to an example at [api.varsome.com](https://api.varsome.com)

To understand how annotation properties are included in the json response please refer to the relevant [schema](https://api.varsome.com/lookup/schema)

#### JSON response wrapper

If you don't want to read through each attribute in the json response you can wrap the result into a Python
[json model](http://jsonmodels.readthedocs.io/en/latest/readme.html).

    from variantapi.client import VariantAPIClient
    from variantapi.models.variant import AnnotatedVariant
    # api key is not required for single variant lookups
    api_key = 'Your token'
    api = VariantAPIClient(api_key)
    # fetch information about a variant into a dictionary
    result = api.lookup('chr7-140453136-A-T', params={'add-source-databases': 'gnomad-exomes,refseq-transcripts'}, ref_genome='hg19')
    annotated_variant = AnnotatedVariant(**result)

now you have access to a set of shortcut attributes (these will be updated over time in the code base)

    annotated_variant.chromosome
    annotated_variant.alt
    annotated_variant.genes # directly get the genes related to the variant
    annotated_variant.gnomad_exomes_af # etc

or you may access other inner properties of other available properties

    # get gnomad exomes allele number
    allele_number = [gnomad_exome.an for gnomad_exome in annotated_variant.gnomad_exomes]

annotated_variant.gnomad_exomes and also other json model type of objects that contain a version property, are
always returned as lists of objects. This is because of the ability of the API to return multiple versions of 
annotation databases (though this is not currently publicly available). For consistency reasons therefore
these are always lists, though it is safe to assume that they will only include a single item. So it is safe
to rewrite as:
     
    try:
        allele_number = [gnomad_exome.an for gnomad_exome in annotated_variant.gnomad_exomes][0]
    except IndexError:
        pass # no gnomad exomes annotation for the variant
           
#### Annotating a VCF using the client

To annotate a vcf you can base your code on the VCFAnnotator object. This provides a basic implementation that
will annotate a vcf file using a set of the available annotations. It uses [PyVCF](https://github.com/jamescasbon/PyVCF) to read and write to vcf files.

    from variantapi.vcf import VCFAnnotator
    api_key = 'Your token'
    vcf_annotator = VCFAnnotator(api_key=api_key, ref_genome='hg19', get_parameters={'add-all-data': 1, 'expand-pubmed-articles': 0})
    vcf_file = 'input.vcf'
    output_vcf_file = 'annotated.vcf'
    vcf_annotator.annotate(vcf_file, output_vcf_file)
        
To annotate the vcf file with the annotations that you are interested in you need only override 2 methods
in the VCFAnnotator class

    from variantapi.vcf import VCFAnnotator
    from vcf.parser import _Info
    class MyVCFAnnotator(VCFAnnotator):
    
        def annotate_record(self, record, variant_result):
            """
            :param record: vcf record object
            :param variant_result: AnnotatedVariant object
            :return: annotated record object
            """
            record.INFO['gnomad_exomes_AN'] = variant_result.gnomad_exomes_an
            return record
        
            
        def add_vcf_header_info(self, vcf_template):
            """
            Adds vcf INFO headers for the annotated values provided
            :param vcf_template: vcf reader object
            :return:
            """
            vcf_template.infos['gnomad_exomes_AN'] = _Info('gnomad_exomes_AN', '.', 'Integer',
                                                                 'GnomAD exomes allele number value', None, None)
                                                                 
    api_key = 'Your token'
    vcf_annotator = MyVCFAnnotator(api_key=api_key, ref_genome='hg19', get_parameters={'add-all-data': 1, 'expand-pubmed-articles': 0})
    vcf_file = 'input.vcf'
    output_vcf_file = 'annotated.vcf'
    vcf_annotator.annotate(vcf_file, output_vcf_file)
        
        
### API Documentation

Please visit the [api documentation](https://api.varsome.com) to find out how to use the api and
what values does the api provide as a response to lookup requests

### How to get an API key

You generally are not required to have an api key to use the api, though the number of requests you will be able
to issue will be throttled if they exceed a certain number.

An API key is required in order to batch requests or enable allele frequency filtering.

To obtain an API key please [contact us](mailto:support@saphetor.com)

### How to run the tests

Clone the repository after creating a virtual environment, and run

    python setup.py test
    
In order to run the tests it is advised that you set the VARIANT_API_KEY env var to your api token,
otherwise several tests will fail because the API will return a 429 (too many requests error).
Be advised as well that running the tests will count towards your account request limit depending on the
API package you are subscribed to.
 


