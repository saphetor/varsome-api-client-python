from .fields import DictField
from .elements import *

__author__ = "ckopanos"

class AnnotatedVariant(models.Base):
    """
    Base variant result definition model
    Most fields are defined as list fields, even though they contain a single list item
    This is due to the fact that VarSome API can return both current and old versions of databases
    """

    chromosome = fields.StringField(help_text="Chromosome")
    alt = fields.StringField(help_text="ALT Sequence", required=False, nullable=True)
    ref = fields.StringField(help_text="REF Sequence", required=False, nullable=True)
    pos = fields.IntField(help_text="Position")
    variant_id = fields.StringField(help_text='Variant Id')
    refseq_transcripts = fields.ListField(required=False, items_types=(Transcript, ), help_text="RefSeq Transcripts")
    ensembl_transcripts = fields.ListField(required=False, items_types=(Transcript,), help_text="Ensembl Transcripts")
    broad_exac = fields.ListField(required=False, items_types=(ExAC,), help_text="ExAC")
    gnomad_exomes = fields.ListField(required=False, items_types=(GnomAD, ), help_text="gnomAD Exomes (ExAC)")
    gnomad_exomes_coverage = fields.ListField(required=False, items_types=(GnomADCoverage, ), help_text="gnomAD exomes coverage")
    gnomad_genomes = fields.ListField(required=False, items_types=(GnomAD,), help_text="gnomAD Genomes")
    gnomad_genomes_coverage = fields.ListField(required=False, items_types=(GnomADCoverage,), help_text="gnomAD genomes coverage")
    thousand_genomes = fields.ListField(required=False, items_types=(ThousandGenomes, ), help_text="1000 Genomes")
    gerp = fields.ListField(required=False, items_types=(Gerp,), help_text="GERP")
    isb_kaviar3 = fields.ListField(required=False, items_types=(Kaviar3, ), help_text='ISB Kaviar3')
    dbnsfp = fields.ListField(required=False, items_types=(DbNSFP, ), help_text="dbNSFP")
    dann_snvs = fields.ListField(required=False, items_types=(DannSNVs, ), help_text="DANN score")
    dbnsfp_dbscsnv = fields.ListField(required=False, items_types=(DBscSNV, ), help_text='dbNSFP dbscSNV')
    ncbi_dbsnp = fields.ListField(required=False, items_types=(DbSNP, ), help_text="dbSNP")
    sanger_cosmic = fields.ListField(required=False, items_types=(Cosmic, ), help_text="Sanger Cosmic")
    sanger_cosmic_public = fields.ListField(required=False, items_types=(CosmicPublic, ), help_text="Cosmic")
    sanger_cosmic_licensed = fields.ListField(required=False, items_types=(CosmicLicensed, ), help_text="Cosmic")
    ncbi_clinvar = fields.ListField(required=False, items_types=(ClinVar, ), help_text="ClinVar")
    ncbi_clinvar2 = fields.ListField(required=False, items_types=(ClinVar2, ), help_text="ClinVar2")
    icgc_somatic = fields.ListField(required=False, items_types=(Somatic, ), help_text="ICGC Somatic")
    iarc_tp53_germline = fields.ListField(required=False, items_types=(TP53Germline, ), help_text="IARC TP53 Germline")
    iarc_tp53_somatic = fields.ListField(required=False, items_types=(TP53Somatic, ), help_text="IARC TP53 Somatic")
    pub_med_articles = DictField(required=False, help_text="PUBMED Articles")
    uniprot_variants = fields.ListField(required=False, items_types=(UniprotVariants, ), help_text="UniProt variants")
    wustl_civic = fields.ListField(required=False, items_types=(Civic, ), help_text="CIViC")
    gwas = fields.ListField(required=False, items_types=(GWAS, ), help_text="GWAS")


    @property
    def genes(self):
        genes = []
        genes.extend(self.refseq_genes)
        genes.extend(self.ensembl_genes)
        return list(set(genes))

    @property
    def refseq_genes(self):
        genes = []
        for transcript in self.refseq_transcripts:
            genes.extend([item.gene_symbol for item in transcript.items if item.gene_symbol])
        return genes

    @property
    def ensembl_genes(self):
        genes = []
        for transcript in self.ensembl_transcripts:
            genes.extend([item.gene_symbol for item in transcript.items if item.gene_symbol])
        return genes

    @property
    def rs_ids(self):
        rs_ids = []
        for dbnsp_entry in self.ncbi_dbsnp:
            rs_ids.extend(dbnsp_entry.rsid)
        return ["rs%s" % rs_id for rs_id in rs_ids]

    @property
    def gnomad_exomes_af(self):
        """
        Returns the gnomad exomes af value.
        :return:
        """
        af = [gnomad_exomes.af for gnomad_exomes in self.gnomad_exomes]
        return af[0] if af else None

    @property
    def gnomad_genomes_af(self):
        af = [gnomad_genomes.af for gnomad_genomes in self.gnomad_genomes]
        return af[0] if af else None


