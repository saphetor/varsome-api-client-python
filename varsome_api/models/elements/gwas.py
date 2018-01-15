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


class GWASDetails(models.Base):
    gwas_symbol = fields.StringField(help_text="GWAS symbol", required=False, nullable=True)
    date = fields.StringField(help_text="Date", required=False, nullable=True)
    study = fields.StringField(help_text="Study", required=False, nullable=True)
    disease_or_trait = fields.StringField(help_text="Disease or trait", required=False, nullable=True)
    mapped_traits = fields.ListField(items_types=(str,), help_text="Mapped trait", required=False, nullable=True)
    mapped_trait_urls = fields.ListField(items_types=(str,), help_text="Mapped trait URL", required=False,
                                         nullable=True)
    strongest_snp_risk_allele = fields.StringField(help_text="Strongest SNP risk allele", required=False, nullable=True)
    odds_ratio = fields.FloatField(help_text="Odds ratio", required=False, nullable=True)
    p_value = fields.StringField(help_text="p value", required=False, nullable=True)
    confidence_range_95_low = fields.FloatField(help_text="Confidence range 95% low", required=False, nullable=True)
    confidence_range_95_high = fields.FloatField(help_text="Confidence range 95% high", required=False, nullable=True)
    confidence_comment = fields.StringField(help_text="Confidence comment", required=False, nullable=True)
    initial_sample_size = fields.StringField(help_text="Initial sample size", required=False, nullable=True)
    replication_sample_size = fields.StringField(help_text="Replication sample size", required=False, nullable=True)
    pub_med_references = fields.ListField(items_types=(int,), help_text="PubMed References", required=False,
                                          nullable=True)


class GWAS(models.Base):
    version = fields.StringField(help_text="Version")
    items = fields.ListField(help_text='Details', items_types=(GWASDetails,))
