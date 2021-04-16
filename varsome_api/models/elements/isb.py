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


class Kaviar3(models.Base):
    version = fields.StringField(help_text="Version")
    ac = fields.ListField(
        items_types=(int,), help_text="ac", required=False, nullable=True
    )
    an = fields.ListField(
        items_types=(int,), help_text="an", required=False, nullable=True
    )
    main_data = fields.StringField(help_text="Main data point", required=False)
