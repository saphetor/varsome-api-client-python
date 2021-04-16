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


class ACMGClassification(models.Base):
    met_criteria = fields.BoolField()
    name = fields.StringField(help_text="ACMG Classification Name")
    user_explain = fields.ListField(
        items_types=(str,),
        help_text="Criteria explanation",
        required=False,
        nullable=True,
    )


class ACMGRule(models.Base):
    pathogenic_subscore = fields.StringField(required=False, nullable=True)
    benign_subscore = fields.StringField(required=False, nullable=True)
    verdict = fields.StringField(required=False, nullable=True)


class ACMGVerdict(models.Base):
    classifications = fields.ListField(
        items_types=(str,),
        help_text="Classification names",
        required=False,
        nullable=True,
    )
    ACMG_rules = fields.EmbeddedField(ACMGRule)


class ACMG(models.Base):
    classifications = fields.ListField(
        required=False,
        items_types=(ACMGClassification,),
        help_text="ACMG Classifications",
    )
    verdict = fields.EmbeddedField(
        ACMGVerdict, nullable=True, required=False, help_text="ACMG Verdict"
    )
