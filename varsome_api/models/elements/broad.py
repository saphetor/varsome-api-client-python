# Copyright [2018] [Saphetor S.A.]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from jsonmodels import models, fields

__author__ = "ckopanos"


class ExAC(models.Base):
    version = fields.StringField(help_text="Version")
    ac = fields.IntField(help_text="Allele Count", required=False, nullable=True)
    an = fields.IntField(help_text="Allele Number", required=False, nullable=True)
    ac_adj = fields.FloatField(help_text="Allele Count", required=False, nullable=True)
    an_adj = fields.FloatField(help_text="Allele Number", required=False, nullable=True)
    af = fields.FloatField(help_text="Allele Frequency", required=False, nullable=True)
    ac_afr = fields.IntField(help_text="Allele Count African", required=False, nullable=True)
    ac_amr = fields.IntField(help_text="Allele Count American", required=False, nullable=True)
    ac_asj = fields.IntField(help_text="Allele Count Ashkenazi Jewish", required=False, nullable=True)
    ac_eas = fields.IntField(help_text="Allele Count East Asian", required=False, nullable=True)
    ac_fin = fields.IntField(help_text="Allele Count European (Finnish)", required=False, nullable=True)
    ac_nfe = fields.IntField(help_text="Allele Count European (Non-Finnish)", required=False, nullable=True)
    ac_oth = fields.IntField(help_text="Allele Count Other", required=False, nullable=True)
    ac_sas = fields.IntField(help_text="Allele Count South Asian", required=False, nullable=True)
    ac_male = fields.IntField(help_text="Allele Count Male", required=False, nullable=True)
    ac_female = fields.IntField(help_text="Allele Count Female", required=False, nullable=True)
    hom = fields.IntField(help_text="Number of Homozygotes", required=False, nullable=True)
    hemi = fields.IntField(help_text="Number of Hemizygotes", required=False, nullable=True)
    ac_hom = fields.FloatField(help_text="Number of Homozygotes", required=False, nullable=True)
    ac_hemi = fields.FloatField(help_text="Number of Hemizygotes", required=False, nullable=True)
    an_afr = fields.IntField(help_text="Allele Number African", required=False, nullable=True)
    an_amr = fields.IntField(help_text="Allele Number American", required=False, nullable=True)
    an_asj = fields.IntField(help_text="Allele Number Ashkenazi Jewish", required=False, nullable=True)
    an_eas = fields.IntField(help_text="Allele Number East Asian", required=False, nullable=True)
    an_fin = fields.IntField(help_text="Allele Number European (Finnish)", required=False, nullable=True)
    an_nfe = fields.IntField(help_text="Allele Number European (Non-Finnish)", required=False, nullable=True)
    an_oth = fields.IntField(help_text="Allele Number Other", required=False, nullable=True)
    an_sas = fields.IntField(help_text="Allele Number South Asian", required=False, nullable=True)
    an_male = fields.IntField(help_text="Allele Number Male", required=False, nullable=True)
    an_female = fields.IntField(help_text="Allele Number Female", required=False, nullable=True)
    hom_afr = fields.IntField(help_text="Number of Homozygotes African", required=False, nullable=True)
    hom_amr = fields.IntField(help_text="Number of Homozygotes American", required=False, nullable=True)
    hom_asj = fields.IntField(help_text="Number of Homozygotes Ashkenazi Jewish", required=False, nullable=True)
    hom_eas = fields.IntField(help_text="Number of Homozygotes East Asian", required=False, nullable=True)
    hom_fin = fields.IntField(help_text="Number of Homozygotes European (Finnish)", required=False, nullable=True)
    hom_nfe = fields.IntField(help_text="Number of Homozygotes European (Non-Finnish)", required=False, nullable=True)
    hom_oth = fields.IntField(help_text="Number of Homozygotes Other", required=False, nullable=True)
    hom_sas = fields.IntField(help_text="Number of Homozygotes South Asian", required=False, nullable=True)
    hom_male = fields.IntField(help_text="Number of Homozygotes Male", required=False, nullable=True)
    hom_female = fields.IntField(help_text="Number of Homozygotes Female", required=False, nullable=True)
    hemi_afr = fields.IntField(help_text="Number of Hemizygotes African", required=False, nullable=True)
    hemi_amr = fields.IntField(help_text="Number of Hemizygotes American", required=False, nullable=True)
    hemi_asj = fields.IntField(help_text="Number of Hemizygotes Ashkenazi Jewish", required=False, nullable=True)
    hemi_eas = fields.IntField(help_text="Number of Hemizygotes East Asian", required=False, nullable=True)
    hemi_fin = fields.IntField(help_text="Number of Hemizygotes European (Finnish)", required=False, nullable=True)
    hemi_nfe = fields.IntField(help_text="Number of Hemizygotes European (Non-Finnish)", required=False, nullable=True)
    hemi_oth = fields.IntField(help_text="Number of Hemizygotes Other", required=False, nullable=True)
    hemi_sas = fields.IntField(help_text="Number of Hemizygotes South Asian", required=False, nullable=True)
    af_afr = fields.FloatField(help_text="Allele Frequency African", required=False, nullable=True)
    af_amr = fields.FloatField(help_text="Allele Frequency American", required=False, nullable=True)
    af_asj = fields.FloatField(help_text="Allele Frequency Ashkenazi Jewish", required=False, nullable=True)
    af_eas = fields.FloatField(help_text="Allele Frequency East Asian", required=False, nullable=True)
    af_fin = fields.FloatField(help_text="Allele Frequency European (Finnish)", required=False, nullable=True)
    af_nfe = fields.FloatField(help_text="Allele Frequency European (Non-Finnish)", required=False, nullable=True)
    af_oth = fields.FloatField(help_text="Allele Frequency Other", required=False, nullable=True)
    af_sas = fields.FloatField(help_text="Allele Frequency South Asian", required=False, nullable=True)
    af_male = fields.FloatField(help_text="Allele Frequency Male", required=False, nullable=True)
    af_female = fields.FloatField(help_text="Allele Frequency Female", required=False, nullable=True)