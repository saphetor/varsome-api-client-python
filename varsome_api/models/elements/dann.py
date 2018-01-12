from jsonmodels import models, fields

__author__ = "ckopanos"


class DannSNVs(models.Base):
    version = fields.StringField(help_text="Version")
    dann_score = fields.FloatField(help_text="DANN Score", required=False, nullable=True)
