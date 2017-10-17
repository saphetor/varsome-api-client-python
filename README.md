# Variant API Client

## A basic api client implementation for [api.varsome.com](https://api.varsome.com)

This client is still in beta but it is a good start to start playing around with the API.

### Installation

Either download clone the repository from github and place the variantapi package
within your code, or do

    pip install https://github.com/saphetor/variant-api-client-python/archive/master.zip

### API Documentation

Please visit the [api documentation](http://docs.varsome.apiary.io) to find out how to use the api and
what values does the api provide as a response to lookup requests

### How to get an API key

You generally are not required to have an api key to use the api, though the number of requests you will be able
to issue will be throttled if they exceed a certain number.

Without an API key you will not be able to perform batch requests as well.

To obtain an API key please [contact us](mailto:support@saphetor.com)

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
    result = api.lookup('chr19:20082943:1:G', params={'add-source-databases': 'gnomad-exomes,refseq-transcripts'}, ref_genome='hg19')
    # access results e.g. the transcripts of the variant
    transcripts = result['refseq_transcripts']
    # fetch information for multiple variants
    variants = ['chr19:20082943:1:G','chr22:39777823::CAA']
    # results will be an array of dictionaries an api key will be required for this request
    results = api.batch_lookup(variants, params={'add-source-databases': 'gnomad-exomes,gnomad-genomes'}, ref_genome='hg19')

If errors occur while using the client an exception will be thrown.
You may wish to catch this exception and proceed with your own code logic

    from variantapi.client import VariantAPIClient, VariantApiException
    api = VariantAPIClient()
    try:
       result = api.lookup('chr19:20082943:1:G', ref_genome='hg64')
    except VariantApiException as e:
        # proceed with your code flow e.g.
        print(e) # 404 (invalid reference genome)

### Example Usage


You may download and run the run.py python file after installation of the package
to test the api client directly e.g.

    ./run.py -g hg19 -q 'chr19:20082943:1:G' -p add-all-data=1

You may pass more than one values after the -q argument that will make a batch request
to the API but you will need a token to do that e.g.

    ./run.py -k 'your token' -g hg19 -q 'rs113488022' 'chr19:20082943:1:G' -p add-source-databases=gnomad-exomes,gnomad-genomes

Run

    ./run.py -h

for a list of available options

To view available request parameters (used in the params method parameter) refer to an example at [api.varsome.com](https://api.varsome.com) or
the [api documentation](http://docs.varsome.apiary.io).

To understand how annotation properties are included in the json response please refer to the relevant [schema](https://api.varsome.com/lookup/schema)

