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


class Cosmic(models.Base):
    version = fields.StringField(help_text="Version")
    primary_site = fields.ListField(items_types=(str,), help_text="Primary site", required=False, nullable=True)
    pub_med_references = fields.ListField(items_types=(int,), help_text="PUBMED References", required=False,
                                          nullable=True)


class CosmicLicensedDrugEntry(models.Base):
    drug_name = fields.StringField(help_text="Drug name", required=False, nullable=True)
    somatic_status = fields.StringField(help_text="Somatic status", required=False, nullable=True)
    zygosity = fields.StringField(help_text="Zygosity", required=False, nullable=True)
    gene = fields.StringField(help_text="Gene", required=False, nullable=True)
    transcript = fields.StringField(help_text="Transcript", required=False, nullable=True)
    census_gene = fields.StringField(help_text="Census gene", required=False, nullable=True)
    pub_med_references = fields.ListField(items_types=(int,), help_text="PUBMED References", required=False,
                                          nullable=True)
    histology_freq = fields.ListField(items_types=(float,), help_text="Histology frequency", required=False,
                                      nullable=True)
    tissue_freq = fields.ListField(items_types=(float,), help_text="Tissue frequency", required=False, nullable=True)


class CosmicLicensedDetails(models.Base):
    entry_type = fields.StringField(help_text="Entry type", required=False, nullable=True)
    cosmic_id = fields.ListField(items_types=(str,), help_text="Cosmic ID", required=False, nullable=True)
    pub_med_references = fields.ListField(items_types=(int,), help_text="PUBMED References", required=False,
                                          nullable=True)
    histology_freq = fields.ListField(items_types=(int, str, float), help_text="Histology frequency", required=False,
                                      nullable=True)
    genome_wide_screen_freq = fields.ListField(items_types=(int, str, float), help_text="Histology frequency", required=False,
                                               nullable=True)
    loh_freq = fields.ListField(items_types=(int, str, float), help_text="LOH frequency", required=False, nullable=True)
    age_freq = fields.ListField(items_types=(int, str, float), help_text="Age frequency", required=False, nullable=True)
    zygosity_freq = fields.ListField(items_types=(int, str, float), help_text="Zygosity frequency", required=False,
                                     nullable=True)
    tumour_origin_freq = fields.ListField(items_types=(int, str, float,), help_text="Tumour original frequency", required=False,
                                          nullable=True)
    somatic_status_freq = fields.ListField(items_types=(int, str, float), help_text="Somatic status frequency", required=False,
                                           nullable=True)
    primary_site_freq = fields.ListField(items_types=(int, str, float), help_text="Primary site frequency", required=False, nullable=True)
    description = fields.ListField(items_types=(str,), help_text="Description", required=False, nullable=True)
    accession_number = fields.ListField(items_types=(str,), help_text="Accession number", required=False, nullable=True)
    fathmm_prediction = fields.StringField(help_text="FATHMM prediction", required=False, nullable=True)
    fathmm_score = fields.FloatField(help_text="FATHMM score", required=False, nullable=True)
    num_entries = fields.IntField(help_text="Number of entries", required=False, nullable=True)
    num_samples = fields.IntField(help_text="Number of samples", required=False, nullable=True)
    gene = fields.ListField(items_types=(str,), help_text="Gene", required=False, nullable=True)

    fathmm_mkl_coding_score = fields.FloatField(help_text="FATHMM_MKL coding score", required=False, nullable=True)
    fathmm_mkl_coding_groups = fields.StringField(help_text="FATHMM_MKL coding groups", required=False, nullable=True)
    fathmm_mkl_non_coding_score = fields.FloatField(help_text="FATHMM_MKL non coding score", required=False,
                                                    nullable=True)
    fathmm_mkl_non_coding_groups = fields.StringField(help_text="FATHMM_MKL non coding groups", required=False,
                                                      nullable=True)
    whole_exome_freq = fields.ListField(items_types=(str, int, float,), help_text="Whole exome frequency", required=False,
                                        nullable=True)
    whole_genome_reseq_freq = fields.ListField(items_types=(str, int, float,), help_text="Whole genome reseq frequency",
                                               required=False, nullable=True)

    resistance_mutation = fields.ListField(items_types=(str,), help_text="Resistance mutation", required=False,
                                           nullable=True)
    drug_entries = fields.ListField(items_types=(CosmicLicensedDrugEntry,), help_text="Drug entries", required=False,
                                    nullable=True)


class ComsicPublicDetails(models.Base):
    num_samples = fields.IntField(help_text='Number of samples')
    id = fields.StringField(help_text='Cosmic ID')


class CosmicPublic(models.Base):
    version = fields.StringField(help_text="Version")
    items = fields.ListField(items_types=(ComsicPublicDetails, ), help_text="Details", required=False, nullable=True)


class CosmicLicensed(models.Base):
    version = fields.StringField(help_text="Version")
    items = fields.ListField(items_types=(CosmicLicensedDetails,), help_text="Details")
