from jsonmodels import models, fields

__author__ = "ckopanos"


class ThousandGenomes(models.Base):
    version = fields.StringField(help_text="Version")
    ac = fields.ListField(items_types=(int,), help_text="Allele Count", required=False, nullable=True)
    af = fields.ListField(items_types=(float,), help_text="Allele Frequency", required=False, nullable=True)
    an = fields.ListField(items_types=(int,), help_text="Allele Number", required=False, nullable=True)
    ns = fields.ListField(items_types=(int,), help_text="Number of Samples", required=False, nullable=True)
    afr_af = fields.ListField(items_types=(float,), help_text="Allele Frequency African", required=False, nullable=True)
    amr_af = fields.ListField(items_types=(float,), help_text="Allele Frequency American", required=False,
                              nullable=True)
    eas_af = fields.ListField(items_types=(float,), help_text="Allele Frequency East Asian", required=False,
                              nullable=True)
    eur_af = fields.ListField(items_types=(float,), help_text="Allele Frequency European", required=False,
                              nullable=True)
    sas_af = fields.ListField(items_types=(float,), help_text="Allele Frequency South Asian", required=False,
                              nullable=True)
    main_data = fields.StringField(help_text="Main data point", required=False, nullable=True)
