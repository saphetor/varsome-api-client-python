# Copyright 2018 Saphetor S.A.
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


class CivicDetails(models.Base):
    variant = fields.StringField(help_text="Variant", required=False, nullable=True)
    variant_summary = fields.StringField(help_text="Variant summary", required=False, nullable=True)
    variant_civic_url = fields.StringField(help_text="Variant CIViC URL", required=False, nullable=True)
    variant_origin = fields.StringField(help_text="Variant origin", required=False, nullable=True)
    pub_med_references = fields.ListField(items_types=(int, ), help_text="PubMed References", required=False, nullable=True)
    clinical_significance = fields.StringField(help_text="Clinical significance", required=False, nullable=True)
    evidence_level = fields.StringField(help_text="Evidence level", required=False, nullable=True)
    evidence_statement = fields.StringField(help_text="Evidence statement", required=False, nullable=True)
    evidence_type = fields.StringField(help_text="Evidence type", required=False, nullable=True)
    evidence_status = fields.StringField(help_text="Evidence status", required=False, nullable=True)
    evidence_direction = fields.StringField(help_text="Evidence direction", required=False, nullable=True)
    evidence_civic_url = fields.StringField(help_text="Evidence CIViC URL", required=False, nullable=True)
    drugs = fields.ListField(items_types=(str, ), help_text="Drugs", required=False, nullable=True)
    transcripts = fields.ListField(items_types=(str, ), help_text="Transcripts", required=False, nullable=True)
    representative_transcript = fields.StringField(help_text="Representative transcript", required=False, nullable=True)
    disease = fields.StringField(help_text="Disease", required=False, nullable=True)
    rating = fields.StringField(help_text="Rating", required=False, nullable=True)
    gene = fields.StringField(help_text="Gene", required=False, nullable=True)
    gene_civic_url = fields.StringField(help_text="Gene CIViC URL", required=False, nullable=True)
    entrez_id = fields.StringField(help_text="Entrez ID", required=False, nullable=True)
    doid = fields.StringField(help_text="DOID", required=False, nullable=True)


class Civic(models.Base):
    version = fields.StringField(help_text="Version")
    items = fields.ListField(help_text='Details', items_types=(CivicDetails, ))