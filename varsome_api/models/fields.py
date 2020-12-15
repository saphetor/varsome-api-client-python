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

from jsonmodels import fields

__author__ = "ckopanos"


class DictField(fields.BaseField):

    types = (dict,)


class NullableItemListField(fields.ListField):
    """
    A list field that accepts None as item types
    """

    def validate_single_value(self, item):
        if item is None:
            return
        super().validate_single_value(item)

    def parse_value(self, values):
        """Cast value to proper collection."""
        result = self.get_default_value()

        if not values:
            return result

        if not isinstance(values, list):
            return values

        return [self._cast_value(value) if value is not None else None for value in values]



