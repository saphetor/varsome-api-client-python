from jsonmodels import models, fields

__author__ = "ckopanos"


class Occurrence(models.Base):
    affected = fields.IntField(required=False, nullable=True, help_text="Affected number")
    donors = fields.IntField(required=False, nullable=True, help_text="Donors number")
    project = fields.StringField(required=False, nullable=True, help_text="Project")


class Somatic(models.Base):
    version = fields.StringField(help_text="Version")
    id = fields.StringField(help_text="ID", required=False, nullable=True)
    occurrence = fields.ListField(required=False, nullable=True, items_types=(Occurrence, ), help_text="Occurrence")
    affected_donors = fields.IntField(help_text="Affected Donors", required=False, nullable=True)
    project_count = fields.IntField(help_text="Project Count", required=False, nullable=True)
    main_data = fields.StringField(help_text="Main data point", required=False, nullable=True)