from jsonmodels import models, fields

__author__ = "ckopanos"


class Gerp(models.Base):
    version = fields.StringField(help_text="Version")
    gerp_nr = fields.ListField(items_types=(float, type(None)), required=False, help_text="GERP NR", nullable=True)
    gerp_rs = fields.ListField(items_types=(float, type(None)), required=False, help_text="GERP RS", nullable=True)
