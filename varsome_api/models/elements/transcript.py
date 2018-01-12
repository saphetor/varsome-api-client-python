from jsonmodels import models, fields

__author__ = "ckopanos"


class TranscriptItem(models.Base):
    name = fields.StringField(help_text="Transcript")
    coding_impact = fields.StringField(help_text="Coding impact", required=False, nullable=True)
    function = fields.ListField(help_text="Function", items_types=(str,), required=False, nullable=True)
    hgvs = fields.StringField(required=False, help_text="HGVS cDNA level", nullable=True)
    hgvs_p1 = fields.StringField(required=False, nullable=True)
    hgvs_p3 = fields.StringField(required=False, nullable=True)
    hgvs_notation = fields.StringField(help_text="HGVS notation", required=False, nullable=True)
    location = fields.StringField(help_text="Location", required=False, nullable=True)
    coding_location = fields.StringField(help_text="Coding location", required=False, nullable=True)
    canonical = fields.BoolField(help_text="Canonical", required=False, nullable=True)
    gene_symbol = fields.StringField(help_text="Gene symbol", required=False, nullable=True)


class Transcript(models.Base):
    items = fields.ListField(help_text='Transcripts', items_types=(TranscriptItem,), required=False)
    version = fields.StringField(help_text="Version")
