from jsonmodels import models, fields

__author__ = "ckopanos"


class UniprotVariantsDetails(models.Base):
    annotation_id = fields.StringField(help_text="Annotation ID", required=False, nullable=True)
    protein_id = fields.StringField(help_text="Protein ID", required=False, nullable=True)
    bed_comments = fields.ListField(help_text="Comments", items_types=(str, ), required=False, nullable=True)
    gene = fields.StringField(help_text="Gene", required=False, nullable=True)
    variant_type = fields.StringField(help_text="Variant type", required=False, nullable=True)
    transcripts = fields.ListField(help_text="Transcripts", items_types=(str,), required=False, nullable=True)
    pub_med_references = fields.ListField(help_text="PubMed References", items_types=(int,), required=False, nullable=True)
    disease = fields.StringField(help_text="Disease", required=False, nullable=True)
    disease_symbol = fields.StringField(help_text="Disease symbol", required=False, nullable=True)
    disease_alt_symbol = fields.StringField(help_text="Disease alt symbol", required=False, nullable=True)


class UniprotVariants(models.Base):
    version = fields.StringField(help_text="Version")
    items = fields.ListField(help_text='Details', items_types=(UniprotVariantsDetails,))
