# Copyright [2018] [Saphetor S.A.]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os

import unittest
from tempfile import NamedTemporaryFile
try:
    unittest.TestCase.subTest
except AttributeError:
    import unittest2 as unittest

import vcf
from vcf.parser import _Info
from varsome_api.client import VarSomeAPIClient, VarSomeAPIException
from varsome_api.models.variant import AnnotatedVariant
from varsome_api.vcf import VCFAnnotator

__author__ = "ckopanos"


API_KEY = os.getenv('VARSOME_API_KEY', None)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARIANTS_CSV_FILE = os.path.join(BASE_DIR, 'tests', 'variants.csv')
VARIANTS_VCF_FILE = os.path.join(BASE_DIR, 'tests', 'variants.vcf')



class TestApiClient(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.client = VarSomeAPIClient(API_KEY)
        with open(VARIANTS_CSV_FILE) as f:
            self.variants_to_lookup = f.read().splitlines()
        if API_KEY is None:
            # just get 5 variants without an API key tests might fail with 429
            self.variants_to_lookup = self.variants_to_lookup[:5]
        else:
            self.variants_to_lookup = self.variants_to_lookup[:50]

    def test_schema(self):
        """Check we receive the response schema back"""
        self.assertIsNotNone(self.client.schema())
        self.client.session.close()

    def test_404(self):
        """Check we can raise VarSomeAPIException"""
        with self.assertRaises(VarSomeAPIException) as ve:
            self.client.lookup('chrM:410:A:T', ref_genome='hg64')
        test_exception = ve.exception
        self.assertEqual(test_exception.status, 404)
        self.client.session.close()

    def test_get_lookup_hg19(self):
        """Check we can do plain get requests"""
        for i, variant in enumerate(self.variants_to_lookup):
            with self.subTest(i=i):
                result = self.client.lookup(variant, ref_genome='hg19', params={'add-all-data': 1,
                                                                                'expand-pubmed-articles': 0})
                self.assertIsNotNone(result)
                self.assertTrue('variant_id' in result)
                self.client.session.close()

    def test_batch_lookup_hg19(self):
        """Check we can do batch requests"""
        results = self.client.batch_lookup(self.variants_to_lookup, ref_genome='hg19',
                                           params={'add-all-data': 1, 'expand-pubmed-articles': 0},
                                           raise_exceptions=True)
        self.assertEqual(len(results), len(self.variants_to_lookup))
        self.client.session.close()


class TestApiResponse(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        client = VarSomeAPIClient(API_KEY, max_variants_per_batch=1000)
        with open(VARIANTS_CSV_FILE) as f:
            self.variants_to_lookup = f.read().splitlines()
        self.results = client.batch_lookup(self.variants_to_lookup, ref_genome='hg19',
                                           params={'add-all-data': 1, 'expand-pubmed-articles': 0},
                                           raise_exceptions=True)
        client.session.close()

    def test_result_is_not_none(self):
        """Check result is not None"""
        for i, result in enumerate(self.results):
            with self.subTest(i=i):
                self.assertIsNotNone(result)

    def test_result_has_variant_id(self):
        """Check result includes variant_id"""
        for i, result in enumerate(self.results):
            with self.subTest(i=i):
                self.assertTrue('variant_id' in result)

    def test_variant_chromosome_result_chromosome(self):
        """Check that the requested chromosome is the same as the one returned"""
        for i, result in enumerate(self.results):
            with self.subTest(i=i):
                chromosome = self.variants_to_lookup[i].split(":")[0]
                self.assertEqual(result['chromosome'], chromosome)

    def test_result_wrapper(self):
        """Check that we can wrap the result in a json model"""
        for i, result in enumerate(self.results):
            with self.subTest(i=i):
                annotated_variant = AnnotatedVariant(**result)
                self.assertEqual(annotated_variant.chromosome, result['chromosome'])
                self.assertIsNotNone(annotated_variant.pos)
                self.assertEqual(result['pos'], annotated_variant.pos)


class TestVCFAnnotator(VCFAnnotator):

    def annotate_record(self, record, variant_result):
        record.INFO['gnomad_genomes_AN'] = variant_result.gnomad_genomes_an
        return record

    def add_vcf_header_info(self, vcf_template):
        vcf_template.infos['gnomad_genomes_AN'] = _Info('gnomad_genomes_AN', '.', 'Integer',
                                                        'GnomAD genomes allele number value', None, None)

class TestVcfAnnotator(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.annotator = TestVCFAnnotator(API_KEY)

    def test_annotate_vcf(self):
        """Check that we can annotate a vcf file"""
        output_vcf_file = NamedTemporaryFile(delete=False)
        output_vcf_file.close()
        self.annotator.annotate(VARIANTS_VCF_FILE, output_vcf_file.name)
        vcf_reader = vcf.Reader(filename=output_vcf_file.name, strict_whitespace=True)
        self.assertTrue('gnomad_genomes_AN' in vcf_reader.infos)
        for i, record in enumerate(vcf_reader):
            with self.subTest(i=i):
                self.assertTrue('gnomad_genomes_AN' in record.INFO)
        vcf_reader._reader.close()
        self.annotator.session.close()

