# VarSome API Client

## A basic API client implementation for [api.varsome.com](https://api.varsome.com)

This tool contains examples for the Varsome API usage. It can be used against the production server ([api.varsome.com](https://api.varsome.com)), the staging server ([staging-api.varsome.com](https://staging-api.varsome.com)) or the stable api server ([stable-api.varsome.com](https://stable-api.varsome.com))

### Staging-api environment

The staging-api.varsome.com environment is a free usage test environment for subscribers. It is the perfect environment for evaluating the performance of the API. It is updated on an adhoc basis at our discretion, either together with live or possibly ahead of live in order to test upcoming new features. 

It contains a substantial, but partial, data-set. Additionally it is throttled and is limited in the types of queries you can run. For example, it allows for only a limited number of samples and a limited size of data.

**Please note: For this reason API queries performed against the staging environment within the client may not always run correctly or may produce different results to the production environment.**

### Python versions

Requires at least Python 3.3, you can download the latest version from [www.python.org](http://www.python.org)

### Installation

We suggest that you create a python virtual environment instead of globally installing the library.

There are several ways to create a virtual environment, but you can refer to [pip installation](https://pip.pypa.io/en/stable/installing/) and
[virtualenv installation](https://virtualenv.pypa.io/en/stable/installation/) to first install these 2 tools if you don't
have them already installed via a package manager (Linux) or HomeBrew (MacOS), etc. 
Remember to use "sudo -H" when installing on Mac.

To create a virtual environment, you can follow the [user guide](https://virtualenv.pypa.io/en/stable/userguide/) or simply run:

    virtualenv -p path_to/python3 venv_dir_name

Activate the virtual environment:

    source venv_dir_name/bin/activate

Finally, to use the client, either download or clone the repository from github and place the `varsome_api` 
folder inside your project's directory, or run:

    pip install https://github.com/saphetor/varsome-api-client-python/archive/master.zip

The client will be installed within your virtual environment. Also, 2 scripts called `varsome_api_run.py` and 
`varsome_api_annotate_vcf.py` will be available within your virtual environment's `$PATH`.

### Using the scripts to directly annotate a list of variants or a VCF file

#### Annotating a variant or list of variants

Try the following query to annotate a single variant:

    varsome_api_run.py -g hg19 -k api_key -q 'chr7-140453136-A-T' -p add-all-data=1

The script should complete without errors and display aproximately 6,700 lines of data from `dann`, `dbnsfp`, `ensembl_transcripts`, `gerp`, `gnomad_exomes`, `gnomad_exomes_coverage`, `icgc_somatic`, `ncbi_clinvar2`, `pub_med_articles`, `refseq_transcripts`, `sanger_cosmic_public`, `uniprot_variants`, `wustl_civic` etc.
The script can also accept a text file with variants (one per line) and an optional output file to store the
annotations in. We suggest that you don't use this script for a large number of variants, but use
the client within your code instead.

    varsome_api_run.py -g hg19 -k api_key -i variants.txt -o annotations.txt -p add-all-data=1

The command above will read variants from `variants.txt` and dump the annotations to `annotations.txt`. 
For any number of variants you will need to [register](mailto:support@saphetor.com) for an API key. 

#### Annotating a VCF file

To annotate a VCF file, use: 

    varsome_api_annotate_vcf.py -g hg19 -k api_key -i input.vcf -o annotated_vcf.vcf -p add-all-data=1

Notice, however, that not all available annotations will be present in the `annotated_vcf.vcf` file. Only a subset
of the returned annotations will be available when running this script. See the "Using the client in your code" 
section below for how to annotate a VCF file with the annotations that are of interest to you. 

*Warning*: varsome_api_annotate_vcf.py can only deal with:

- SNPs
- small indels (up to 200bp)

If you want to use this script please remove any variant from your VCF that does not meet the above criteria.

### Using the client in your code

Using the API client is quite straightforward. Just install the API client package and use the following in your code:

```python
from varsome_api.client import VarSomeAPIClient
# API key is not required for single variant lookups
api_key = 'Your token'
api = VarSomeAPIClient(api_key, api_url="https://stable-api.varsome.com")
# fetch information about a variant into a dictionary
result = api.lookup('chr7-140453136-A-T', params={'add-source-databases': 'gnomad-exomes,refseq-transcripts'}, ref_genome='hg19')
# access results e.g. the transcripts of the variant
transcripts = result['refseq_transcripts']
# fetch information for multiple variants
variants = ['chr19:20082943:1:G','chr22:39777823::CAA']
# Results will be an array of dictionaries. An API key will be required for this request
results = api.batch_lookup(variants, params={'add-source-databases': 'gnomad-exomes,gnomad-genomes'}, ref_genome='hg19')
# look at the python doc for batch_lookup method for additional parameters
```

If errors occur while using the client, an exception will be thrown.
You may wish to catch this exception and proceed with your own code logic:

```python
from varsome_api.client import VarSomeAPIClient, VarSomeAPIException
api_key = 'Your token'
api = VarSomeAPIClient(api_key)
try:
   result = api.lookup('chr19:20082943:1:G', ref_genome='hg64')
except VarSomeAPIException as e:
    # proceed with your code flow e.g.
    print(e) # 404 (invalid reference genome)
```

To view available request parameters (used by the `params` method parameter), refer to an example at [api.varsome.com](https://api.varsome.com).

To understand how annotation properties are included in the JSON response, please refer to the relevant [schema](https://api.varsome.com/docs/variants/).

#### JSON response wrapper

If you don't want to read through each attribute in the JSON response, you can wrap the result into a Python
[JSON model](http://jsonmodels.readthedocs.io/en/latest/readme.html):

```python
from varsome_api.client import VarSomeAPIClient
from varsome_api.models.variant import AnnotatedVariant
# API key is not required for single variant lookups
api_key = 'Your token'
api = VarSomeAPIClient(api_key)
# fetch information about a variant into a dictionary
result = api.lookup('chr7-140453136-A-T', params={'add-source-databases': 'gnomad-exomes,refseq-transcripts'}, ref_genome='hg19')
annotated_variant = AnnotatedVariant(**result)
```

You now have access to a set of shortcut attributes (these will be updated over time in the code base):

```python
annotated_variant.chromosome
annotated_variant.alt
annotated_variant.genes # directly get the genes related to the variant
annotated_variant.gnomad_exomes_af # etc
```

Or you may access other inner properties of other available properties:

```python
# get gnomad exomes allele number
allele_number = [gnomad_exome.an for gnomad_exome in annotated_variant.gnomad_exomes]
```

JSON model-type objects that contain a `version` property, like `annotated_variant.gnomad_exomes`, are
always returned as lists of objects. This is because the API has the ability to return multiple versions of 
annotation databases (although this is not currently publicly available). For consistency, therefore,
these are always lists, though it is safe to assume that they will only include a single item. So it is safe
to rewrite as:

```python
try:
    allele_number = [gnomad_exome.an for gnomad_exome in annotated_variant.gnomad_exomes][0]
except IndexError:
    pass # no gnomad exomes annotation for the variant
```

#### Annotating a VCF using the client

To annotate a VCF you can base your code on the VCFAnnotator object. This provides a basic implementation that
will annotate a VCF file using a set of the available annotations. It uses [PyVCF](https://github.com/jamescasbon/PyVCF) to read and write to VCF files.

```python
from varsome_api.vcf import VCFAnnotator
api_key = 'Your token'
vcf_annotator = VCFAnnotator(api_key=api_key, ref_genome='hg19', get_parameters={'add-all-data': 1, 'expand-pubmed-articles': 0})
vcf_file = 'input.vcf'
output_vcf_file = 'annotated.vcf'
vcf_annotator.annotate(vcf_file, output_vcf_file)
```

To annotate the VCF file with the annotations that you are interested in, you need only override 2 methods
(`annotate_record` and `add_vcf_header_info`) in the VCFAnnotator class:

```python
from varsome_api.vcf import VCFAnnotator
from vcf.parser import _Info, _encode_type
class MyVCFAnnotator(VCFAnnotator):

    def annotate_record(self, record, variant_result, original_variant):
        """
        :param record: vcf record object
        :param variant_result: AnnotatedVariant object
        :param original_variant: The variant that was looked up
        :return: annotated record object
        """
        record.INFO['gnomad_exomes_AN'] = variant_result.gnomad_exomes_an
        # if you wish to also include the default annotations
        # return super().annotate_record(record, variant_result)
        return record


    def add_vcf_header_info(self, vcf_template):
        """
        Adds vcf INFO headers for the annotated values provided
        :param vcf_template: vcf reader object
        :return:
        """
        vcf_template.infos['gnomad_exomes_AN'] = _Info('gnomad_exomes_AN', 1, 'Integer',
                                                       'GnomAD exomes allele number value', 
                                                       None, None, _encode_type("Integer"),)
        # if you wish to also include the default headers
        # super().add_vcf_header_info(vcf_template)

api_key = 'Your token'
vcf_annotator = MyVCFAnnotator(api_key=api_key, ref_genome='hg19', get_parameters={'add-all-data': 1, 'expand-pubmed-articles': 0})
vcf_file = 'input.vcf'
output_vcf_file = 'annotated.vcf'
vcf_annotator.annotate(vcf_file, output_vcf_file)
```

### API Documentation

See [API documentation](https://api.varsome.com) for information on how to use the API and
what values the API provides as a response to lookup requests.

### How to get an API key

To obtain an API key please [contact us](mailto:support@saphetor.com).

### How to run the tests

Clone the repository, after creating a virtual environment, and run:

    pip install tox
    tox

To run the tests, set the `VARSOME_API_KEY` environment variable to your API token. Otherwise,
tests will fail because the API will return a 401 (not authenticated) error.
Be advised as well that running the tests will count towards your account request limit depending on the
API package you are subscribed to.
