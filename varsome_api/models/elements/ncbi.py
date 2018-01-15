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

from varsome_api.models.fields import DictField

__author__ = "ckopanos"


class DbSNP(models.Base):
    version = fields.StringField(help_text="Version")
    rsid = fields.ListField(items_types=(int,), help_text="RS ID")


class ClinVar2(models.Base):
    version = fields.StringField(help_text="Version")
    review_status = fields.StringField(help_text="Review status", required=False, nullable=True)
    review_stars = fields.IntField(help_text="Review stars", required=False, nullable=True)
    variation_id = fields.IntField(help_text="Variation ID", required=False, nullable=True)
    num_submitters = fields.IntField(help_text="Number of submitters", required=False, nullable=True)
    pub_med_references = fields.ListField(items_types=(int,), help_text="PubMed references", required=False,
                                          nullable=True)
    clinical_significance = fields.ListField(items_types=(str,), help_text="Clinical significance", required=False,
                                             nullable=True)
    last_evaluation = fields.StringField(help_text="Last evaluation", required=False, nullable=True)
    origin = fields.ListField(items_types=(str,), help_text="Origin", required=False, nullable=True)
    accessions = fields.ListField(items_types=(dict,), help_text="Accessions", required=False, nullable=True)
    main_data = fields.StringField(help_text="Main data point", required=False, nullable=True)
