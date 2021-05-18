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
from varsome_api.models.fields import NullableItemListField
__author__ = "ckopanos"



class DbNSFP(models.Base):
    version = fields.StringField(help_text="Version")
    mutationtaster_pred = NullableItemListField(items_types=(str,), help_text="MutationTaster Prediction",
                                           required=False)
    mutationtaster_score = NullableItemListField(items_types=(float,),
                                            help_text="MutationTaster Accuracy", required=False, nullable=True)
    sift_score = NullableItemListField(items_types=(float,), help_text="SIFT score", required=False, nullable=True)
    sift_prediction = fields.StringField(help_text="SIFT prediction", required=False, nullable=True)
    phylop100way_vertebrate = NullableItemListField(items_types=(float,), help_text="phyloP100way vertebrate",
                                               required=False)
    phylop46way_placental = NullableItemListField(items_types=(float,), help_text="phyloP46way placental",
                                             required=False)
    phylop46way_primate = NullableItemListField(items_types=(float,), help_text="phyloP46way primate",
                                           required=False)
    mutationtaster_converted_rankscore = NullableItemListField(items_types=(float,),
                                                          help_text="MutationTaster converted rankscore",
                                                          required=False, nullable=True)
    mutationassessor_pred = NullableItemListField(items_types=(str,),
                                             help_text="MutationAssessor prediction",
                                             required=False)
    mutationassessor_score = NullableItemListField(items_types=(float,), help_text="MutationAssessor score",
                                              required=False)
    mutationassessor_score_rankscore = NullableItemListField(items_types=(float,),
                                                        help_text="MutationAssessor rankscore", required=False,
                                                        nullable=True)
    fathmm_mkl_coding_pred = NullableItemListField(items_types=(str,),
                                              help_text="FATHMM-MKL coding prediction", required=False, nullable=True)
    fathmm_mkl_coding_score = NullableItemListField(items_types=(float,), help_text="FATHMM-MKL coding score",
                                               required=False)
    fathmm_mkl_coding_rankscore = NullableItemListField(items_types=(float,),
                                                   help_text="FATHMM-MKL coding rankscore", required=False,
                                                   nullable=True)
    fathmm_pred = NullableItemListField(items_types=(str,), help_text="FATHMM prediction", required=False, nullable=True)
    fathmm_score = NullableItemListField(items_types=(float,), help_text="FATHMM score",
                                    required=False)
    fathmm_converted_rankscore = NullableItemListField(items_types=(float,), help_text="FATHMM converted rankscore",
                                                  required=False, nullable=True)
    sift_converted_rankscore = NullableItemListField(items_types=(float,), help_text="SIFT converted rankscore",
                                                required=False)
    metasvm_pred = NullableItemListField(items_types=(str,), help_text="MetaSVM prediction",
                                    required=False)
    metasvm_score = NullableItemListField(items_types=(float,), help_text="MetaSVM score", required=False, nullable=True)
    metasvm_rankscore = NullableItemListField(items_types=(float,), help_text="MetaSVM rankscore",
                                         required=False)
    metalr_pred = NullableItemListField(items_types=(str,), help_text="MetalR prediction", required=False, nullable=True)
    metalr_score = NullableItemListField(items_types=(float,), help_text="MetalR score", required=False, nullable=True)
    metalr_rankscore = NullableItemListField(items_types=(float,), help_text="MetalR rankscore", required=False,
                                        nullable=True)
    provean_pred = NullableItemListField(items_types=(str,), help_text="Provean prediction",
                                    required=False)
    provean_score = NullableItemListField(items_types=(float,), help_text="Provean score",
                                     required=False)
    provean_converted_rankscore = NullableItemListField(items_types=(float,),
                                                   help_text="Provean converted rankscore", required=False,
                                                   nullable=True)
    lrt_pred = NullableItemListField(items_types=(str,), help_text="LRT prediction", required=False, nullable=True)
    lrt_score = NullableItemListField(items_types=(float,), help_text="LRT score", required=False, nullable=True)
    lrt_converted_rankscore = NullableItemListField(items_types=(float,), help_text="LRT converted rankscore",
                                               required=False)
    lrt_omega = NullableItemListField(items_types=(float,), help_text="LRT Omega", required=False, nullable=True)
    cadd_raw = NullableItemListField(items_types=(float,), help_text="CADD raw score", required=False, nullable=True)
    cadd_raw_rankscore = NullableItemListField(items_types=(float,), help_text="CADD raw rankscore",
                                          required=False)
    cadd_phred = NullableItemListField(items_types=(float,), help_text="CADD phred", required=False, nullable=True)
    gm12878_confidence_value = NullableItemListField(items_types=(float,),
                                                help_text="GM12878 fitCons confidence value", required=False,
                                                nullable=True)
    gm12878_fitcons_score = NullableItemListField(items_types=(float,), help_text="GM12878 fitCons score",
                                             required=False)
    gm12878_fitcons_score_rankscore = NullableItemListField(items_types=(float,),
                                                       help_text="GM12878 fitCons rankscore", required=False,
                                                       nullable=True)
    siphy_29way_logodds_rankscore = NullableItemListField(items_types=(float,),
                                                     help_text="SiPhy29way logOdds rankscore", required=False,
                                                     nullable=True)
    siphy_29way_pi = NullableItemListField(items_types=(float,),
                                      help_text="SiPhy29way pi", required=False, nullable=True)
    phylop20way_mammalian = NullableItemListField(items_types=(float,), help_text="phyloP20way mammalian",
                                             required=False)
    phylop20way_mammalian_rankscore = NullableItemListField(items_types=(float,),
                                                       help_text="phyloP20way mammalian rankscore", required=False,
                                                       nullable=True)
    phylop100way_vertebrate_rankscore = NullableItemListField(items_types=(float,),
                                                         help_text="phyloP100way vertebrate rankscore", required=False,
                                                         nullable=True)
    phastcons20way_mammalian = NullableItemListField(items_types=(float,), help_text="phastCons20way mammalian",
                                                required=False)
    phastcons20way_mammalian_rankscore = NullableItemListField(items_types=(float,),
                                                          help_text="phastCons20way mammalian rankscore",
                                                          required=False, nullable=True)
    phastcons100way_vertebrate = NullableItemListField(items_types=(float,),
                                                  help_text="phastCons100way vertebrate", required=False, nullable=True)
    phastcons100way_vertebrate_rankscore = NullableItemListField(items_types=(float,),
                                                            help_text="phastCons100way vertebrate rankscore",
                                                            required=False, nullable=True)
    vest3_score = NullableItemListField(items_types=(float,), help_text="VEST3 score",
                                   required=False)
    vest3_rankscore = NullableItemListField(items_types=(float,),
                                       help_text="VEST3 rankscore", required=False, nullable=True)


class DBscSNV(models.Base):
    version = fields.StringField(help_text="Version")
    ada_score = NullableItemListField(items_types=(float, ), help_text='ADA Score', required=False, nullable=True)
    rf_score = NullableItemListField(items_types=(float,), help_text='RF Score', required=False, nullable=True)
