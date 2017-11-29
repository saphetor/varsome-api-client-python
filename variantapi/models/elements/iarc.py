from jsonmodels import models, fields

__author__ = "ckopanos"


class TP53GermlineDetails(models.Base):
    age_at_diagnosis = fields.IntField(help_text="Age at diagnosis", required=False, nullable=True)
    country = fields.StringField(help_text="Country", required=False, nullable=True)
    effect = fields.StringField(help_text="Effect", required=False, nullable=True)
    familycase = fields.StringField(help_text="Family case", required=False, nullable=True)
    familycase_group = fields.StringField(help_text="Family case group", required=False, nullable=True)
    family_code = fields.StringField(help_text="Family code", required=False, nullable=True)
    generation = fields.StringField(help_text="Generation", required=False, nullable=True)
    morphology = fields.StringField(help_text="Morphology", required=False, nullable=True)
    sex = fields.StringField(help_text="Sex", required=False, nullable=True)
    topography = fields.StringField(help_text="Topography", required=False, nullable=True)
    unaffected = fields.IntField(help_text="Unaffected", required=False, nullable=True)


class TP53SomaticDetails(models.Base):
    age = fields.IntField(help_text="Age", required=False, nullable=True)
    country = fields.StringField(help_text="Country", required=False, nullable=True)
    effect = fields.StringField(help_text="Effect", required=False, nullable=True)
    morphology = fields.StringField(help_text="Morphology", required=False, nullable=True)
    mut_rate = fields.IntField(help_text="Mutation rate", required=False, nullable=True)
    pub_med_references = fields.ListField(items_types=(int,), help_text="PubMed References", required=False,
                                          nullable=True)
    sample_source = fields.StringField(help_text="Sample source", required=False, nullable=True)
    stage = fields.StringField(help_text="Stage", required=False, nullable=True)
    structural_motif = fields.StringField(help_text="Structural Motif", required=False, nullable=True)
    topography = fields.StringField(help_text="Topography", required=False, nullable=True)


class TP53Germline(models.Base):
    version = fields.StringField(help_text="Version")
    items = fields.ListField(help_text='Details', items_types=(TP53GermlineDetails,))


class TP53Somatic(models.Base):
    version = fields.StringField(help_text="Version")
    items = fields.ListField(help_text='Details', items_types=(TP53SomaticDetails,))
