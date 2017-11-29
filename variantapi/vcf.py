from collections import OrderedDict

from variantapi.client import VariantAPIClient, VariantApiException
import os, vcf

from variantapi.models.variant import AnnotatedVariant

__author__ = "ckopanos"


class VCFAnnotator(VariantAPIClient):
    """
    VCFAnnotator will take an input vcf file parse it and produce an annotated vcf file
    """

    def __init__(self, api_key=None,
                 max_variants_per_batch=200, ref_genome='hg19', get_parametes=None):
        super().__init__(api_key, max_variants_per_batch)
        self.ref_genome = ref_genome
        self.get_parameters = get_parametes

    def annotate(self, input_vcf_file, output_vcf_file=None):
        if not os.path.isfile(input_vcf_file):
            raise FileNotFoundError('%s does not exist' % input_vcf_file)
        if output_vcf_file is None:
            output_vcf_file = "%s.annotated.vcf" % input_vcf_file
        vcf_reader = vcf.Reader(filename=input_vcf_file)
        vcf_writer = vcf.Writer(open(output_vcf_file, 'w'), vcf_reader)
        input_batch = OrderedDict()
        for record in vcf_reader:
            for alt_seq in record.ALT:
                requested_variant = "%s:%s:%s:%s" % (record.CHROM, record.POS, record.REF or "", alt_seq or "")
                input_batch[requested_variant] = record
            if len(input_batch) < self.max_variants_per_batch:
                continue
            api_results = self.batch_lookup(list(input_batch.keys()), params=self.get_parameters, ref_genome=self.ref_genome)
            for i, requested_variant in enumerate(input_batch.keys()):
                try:
                    variant_result = AnnotatedVariant(**api_results[i])
                    record = input_batch[requested_variant]
                    record.INFO['VARIANT_ID'] = variant_result.variant_id
                    record.INFO['GENE'] = ",".join(variant_result.genes)
                except Exception as e:
                    print(api_results[i]['variant_id'], e)
                    pass
                vcf_writer.write_record(record)


            # reset input batch
            input_batch = OrderedDict()


