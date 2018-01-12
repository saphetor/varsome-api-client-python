from jsonmodels import models, fields

__author__ = "ckopanos"


class Kaviar3(models.Base):
    version = fields.StringField(help_text="Version")
    ac = fields.ListField(items_types=(int, ), help_text="ac", required=False, nullable=True)
    an = fields.ListField(items_types=(int,), help_text="an", required=False, nullable=True)
    main_data = fields.StringField(help_text="Main data point", required=False)