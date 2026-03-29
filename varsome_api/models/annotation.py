from decimal import Decimal
from typing import Any

from pydantic import AnyUrl, BaseModel, ConfigDict, Field


class _GeneratedBase(BaseModel):
    """Common base for all generated models.

    Allows extra fields from the API that are not yet in the schema
    and coerces strings to numbers (the OpenAPI schema sometimes types
    numeric fields as ``string``).
    """

    model_config = ConfigDict(extra="allow")


class UniprotRegionItem(_GeneratedBase):
    absolute_positon: int | None = None
    amino_acid: str | None = None
    chromo: str | None = None
    colour: str | None = None
    description: str | None = None
    length: int | None = None
    position: int | None = None
    protein: str | None = None
    type: str | None = None
    pub_med_references: list[int | None] | None = None


class UniprotRegions(_GeneratedBase):
    version: str | None = None
    items: list[UniprotRegionItem] | None = None


class SubmissionDisease(_GeneratedBase):
    symbols: list[str | None] | None = None
    normalized_disease: list[str | None] | None = None
    names: list[str | None] | None = None
    normalized_cancer: list[str | None] | None = None


class Submission(_GeneratedBase):
    submitter_name: str | None = None
    submitter_date: int | None = None
    review_description: str | None = None
    review_status: str | None = None
    review_date: int | None = None
    submission_description: list[str | None] | None = None
    accession_id: str | None = None
    clinical_significance: list[str | None] | None = None
    diseases: list[SubmissionDisease] | None = None
    method: str | None = None
    date_updated: str | None = None
    origin: str | None = None


class AccessionDisease(_GeneratedBase):
    pub_med_references: list[int | None] | None = None
    symbols: list[str | None] | None = None
    normalized_cancer: list[str | None] | None = None
    keyword: str | None = None
    disease_mechanism: str | None = None
    normalized_disease: list[str | None] | None = None
    names: list[str | None] | None = None


class Accession(_GeneratedBase):
    variation_id: int | None = None
    submissions: list[Submission] | None = None
    review_stars: int | None = None
    review_description: str | None = None
    allele_id: int | None = None
    submission_description: list[str | None] | None = None
    accession_id: str | None = None
    clinical_significance: list[str | None] | None = None
    date_created: str | None = None
    diseases: list[AccessionDisease] | None = None
    title: str | None = None
    review_status: str | None = None
    review_date: str | None = None


class Clinvarregionjson(_GeneratedBase):
    accessions: list[Accession] | None = None
    acmg_class: str | None = None
    allele_id: int | None = None
    clinical_significance: list[str | None] | None = None
    date_created: str | None = None
    last_evaluation: str | None = None
    names: list[str | None] | None = None
    num_submissions: int | None = None
    num_submitters: int | None = None
    review_stars: int | None = None
    review_status: str | None = None
    type: str | None = None
    variation_id: int | None = None


class OverlapData(_GeneratedBase):
    predicted_pathogenicity: str | None = None
    known_cnv_pathogenicity: str | None = None
    overlap_fraction: float | None = None
    overlapping_exons: int | None = None
    total_variant_exons: int | None = None
    overlapping_genes: int | None = None
    total_variant_genes: int | None = None
    variant_contains_cnv: bool | None = None
    type: str | None = None
    size_similarity: float | None = None
    overlapping_genes_indices: str | None = None
    overlapping_genes_names: str | None = None


class ClinvarCnvItem(_GeneratedBase):
    clinvarregionjson: Clinvarregionjson | None = None
    absolute_positon: int | None = None
    chromo: str | None = None
    length: int | None = None
    position: int | None = None
    overlap_data: OverlapData | None = None


class Clinvarcnv(_GeneratedBase):
    version: str | None = None
    items: list[ClinvarCnvItem] | None = None


class DecipherVariantJson(_GeneratedBase):
    contribution: str | None = None
    genotype: str | None = None
    inheritance: str | None = None
    mean_ratio: float | None = None
    normalized_phenotype: list[str | None] | None = None
    pathogenicity: str | None = None
    phenotypes: list[str | None] | None = None
    variant_class: str | None = None
    variant_type: str | None = None


class DecipherItem(_GeneratedBase):
    json_: DecipherVariantJson | None = Field(None, alias="json")
    absolute_positon: int | None = None
    chromo: str | None = None
    colour: str | None = None
    length: int | None = None
    position: int | None = None
    overlap_data: OverlapData | None = None


class Decipher(_GeneratedBase):
    version: str | None = None
    items: list[DecipherItem] | None = None


class NcbiDbVarItem(_GeneratedBase):
    ac: int | None = None
    af: int | None = None
    clnacc: str | None = None
    clnsig: str | None = None
    desc: str | None = None
    experiment: int | None = None
    links: str | None = None
    origin: str | None = None
    regionid: str | None = None
    svlen: str | None = None
    svtype: str | None = None
    absolute_positon: int | None = None
    chromo: str | None = None
    clinical_source: str | None = None
    length: int | None = None
    position: int | None = None
    overlap_data: OverlapData | None = None


class NcbiDbVar(_GeneratedBase):
    version: str | None = None
    items: list[NcbiDbVarItem] | None = None


class ExacCnvItem(_GeneratedBase):
    absolute_positon: int | None = None
    chromo: str | None = None
    colour: str | None = None
    exac_population: str | None = None
    length: int | None = None
    position: int | None = None
    quality: int | None = None


class ExacCnv(_GeneratedBase):
    version: str | None = None
    items: list[ExacCnvItem] | None = None


class Observations(_GeneratedBase):
    observed_gains: int | None = None
    observed_losses: int | None = None
    samplesize: int | None = None


class Dgvregionjson(_GeneratedBase):
    accession: str | None = None
    observations: Observations | None = None
    pubmedids: int | None = None
    sv_type: str | None = None


class TcagDgvItem(_GeneratedBase):
    dgvregionjson: Dgvregionjson | None = None
    absolute_positon: int | None = None
    chromo: str | None = None
    length: int | None = None
    position: int | None = None
    overlap_data: OverlapData | None = None


class TcagDgv(_GeneratedBase):
    version: str | None = None
    items: list[TcagDgvItem] | None = None


class ClingenRegionItem(_GeneratedBase):
    pub_med_references: list[int | None] | None = None
    triplosensitivity_description: str | None = None
    haploinsufficiency_description: str | None = None
    haploinsufficiency_score: int | None = None
    position: int | None = None
    chromo: str | None = None
    absolute_positon: int | None = None
    length: int | None = None
    triplosensitivity_score: int | None = None
    isca_id: str | None = None
    isca_region_name: str | None = None


class ClingenRegions(_GeneratedBase):
    version: str | None = None
    items: list[ClingenRegionItem] | None = None


class ClingenCnvItem(_GeneratedBase):
    colour: str | None = None
    description: str | None = None
    length: int | None = None
    absolute_positon: int | None = None
    chromo: str | None = None
    position: int | None = None
    overlap_data: OverlapData | None = None


class ClingenCnvs(_GeneratedBase):
    version: str | None = None
    items: list[ClingenCnvItem] | None = None


class Expressions(_GeneratedBase):
    adipose_subcutaneous: float | None = None
    adipose_visceral_omentum: float | None = None
    adrenal_gland: float | None = None
    artery_aorta: float | None = None
    artery_coronary: float | None = None
    artery_tibial: float | None = None
    bladder: float | None = None
    brain_amygdala: float | None = None
    brain_anterior_cingulate_cortex_ba24: float | None = None
    brain_caudate_basal_ganglia: float | None = None
    brain_cerebellar_hemisphere: float | None = None
    brain_cerebellum: float | None = None
    brain_cortex: float | None = None
    brain_frontal_cortex_ba9: float | None = None
    brain_hippocampus: float | None = None
    brain_hypothalamus: float | None = None
    brain_nucleus_accumbens_basal_ganglia: float | None = None
    brain_putamen_basal_ganglia: float | None = None
    brain_spinal_cord_cervical_c_1: float | None = None
    brain_substantia_nigra: float | None = None
    breast_mammary_tissue: float | None = None
    cells_cultured_fibroblasts: float | None = None
    cells_ebv_transformed_lymphocytes: float | None = None
    cervix_ectocervix: float | None = None
    cervix_endocervix: float | None = None
    colon_sigmoid: float | None = None
    colon_transverse: float | None = None
    esophagus_gastroesophageal_junction: float | None = None
    esophagus_mucosa: float | None = None
    esophagus_muscularis: float | None = None
    fallopian_tube: float | None = None
    heart_atrial_appendage: float | None = None
    heart_left_ventricle: float | None = None
    kidney_cortex: float | None = None
    kidney_medulla: float | None = None
    liver: float | None = None
    lung: float | None = None
    minor_salivary_gland: float | None = None
    muscle_skeletal: float | None = None
    nerve_tibial: float | None = None
    ovary: float | None = None
    pancreas: float | None = None
    pituitary: float | None = None
    prostate: float | None = None
    skin_not_sun_exposed_suprapubic: float | None = None
    skin_sun_exposed_lower_leg: float | None = None
    small_intestine_terminal_ileum: float | None = None
    spleen: float | None = None
    stomach: float | None = None
    testis: float | None = None
    thyroid: float | None = None
    uterus: float | None = None
    vagina: float | None = None
    whole_blood: float | None = None


class GeneModelPositions(_GeneratedBase):
    chromosome: str | None = None
    end: int | None = None
    start: int | None = None
    strand: str | None = None


class GenePositions(_GeneratedBase):
    chromosome: str | None = None
    end: int | None = None
    start: int | None = None
    strand: str | None = None


class GtExJsonData(_GeneratedBase):
    exon_id: str | None = None
    exon_number: str | None = None
    expressions: Expressions | None = None
    gencode_id: str | None = None
    gene: str | None = None
    gene_model_positions: GeneModelPositions | None = None
    gene_positions: GenePositions | None = None


class NihGtexItem(_GeneratedBase):
    gt_ex_json_data: GtExJsonData | None = Field(None, alias="GTExJsonData")
    absolute_positon: int | None = None
    chromo: str | None = None
    length: int | None = None
    position: int | None = None


class NihGtex(_GeneratedBase):
    version: str | None = None
    items: list[NihGtexItem] | None = None


class IraMHallLabItem(_GeneratedBase):
    end: str | None = None
    svlen: str | None = None
    svtype: str | None = None
    absolute_positon: int | None = None
    chromo: str | None = None
    length: int | None = None
    position: int | None = None
    overlap_data: OverlapData | None = None


class IraMHallLab(_GeneratedBase):
    version: str | None = None
    items: list[IraMHallLabItem] | None = None


class ChildrenMercyItem(_GeneratedBase):
    end: str | None = None
    svlen: str | None = None
    svtype: str | None = None
    absolute_positon: int | None = None
    chromo: str | None = None
    length: int | None = None
    position: int | None = None
    overlap_data: OverlapData | None = None


class ChildrenMercyResearchInstitute(_GeneratedBase):
    version: str | None = None
    items: list[ChildrenMercyItem] | None = None


class TcagConradEstd20Item(_GeneratedBase):
    end: str | None = None
    svlen: str | None = None
    svtype: str | None = None
    absolute_positon: int | None = None
    chromo: str | None = None
    length: int | None = None
    position: int | None = None
    overlap_data: OverlapData | None = None


class TcagConradEstd20(_GeneratedBase):
    version: str | None = None
    items: list[TcagConradEstd20Item] | None = None


class HprcItem(_GeneratedBase):
    end: str | None = None
    svlen: str | None = None
    svtype: str | None = None
    absolute_positon: int | None = None
    chromo: str | None = None
    length: int | None = None
    position: int | None = None
    overlap_data: OverlapData | None = None


class Hprc(_GeneratedBase):
    version: str | None = None
    items: list[HprcItem] | None = None


class Regions(_GeneratedBase):
    uniprot_regions: UniprotRegions | None = None
    clinvarcnv: Clinvarcnv | None = None
    decipher: Decipher | None = None
    ncbi_db_var: NcbiDbVar | None = Field(None, alias="ncbi_dbVar")
    exac_cnv: ExacCnv | None = Field(None, alias="exacCNV")
    gnomad_sv: dict[str, Any] | None = None
    tcag_dgv: TcagDgv | None = None
    clingen_regions: ClingenRegions | None = None
    clingen_cnvs: ClingenCnvs | None = None
    nih_gtex: NihGtex | None = None
    ira_m_hall_lab: IraMHallLab | None = None
    children_mercy_research_institute: ChildrenMercyResearchInstitute | None = None
    tcag_conrad_estd20: TcagConradEstd20 | None = None
    hprc: Hprc | None = None


class TranscriptItem(_GeneratedBase):
    name: str | None = None
    strand: str | None = None
    coding_impact: str | None = None
    function: list[Any] | None = None
    hgvs: str | None = None
    hgvs_p1: str | None = None
    hgvs_p3: str | None = None
    location: str | None = None
    coding_location: str | None = None
    canonical: bool | None = False
    gene_symbol: str | None = None
    splice_distance: str | None = None
    ensembl_support_level: str | None = None
    ensembl_appris: str | None = None
    mane_select: str | None = None
    mane_plus: str | None = None
    uniprot_id: str | None = None


class RefseqTranscript(_GeneratedBase):
    items: list[TranscriptItem] | None = None
    version: str | None = None


class EnsemblTranscript(_GeneratedBase):
    items: list[TranscriptItem] | None = None
    version: str | None = None


class BroadExacItem(_GeneratedBase):
    version: str | None = None
    ac: int | None = None
    an: int | None = None
    ac_adj: str | None = None
    an_adj: str | None = None
    af: float | None = None
    ac_afr: int | None = None
    ac_amr: int | None = None
    ac_asj: int | None = None
    ac_eas: int | None = None
    ac_fin: int | None = None
    ac_nfe: int | None = None
    ac_oth: int | None = None
    ac_sas: int | None = None
    ac_male: int | None = None
    ac_female: int | None = None
    hom: int | None = None
    hemi: int | None = None
    ac_hom: str | None = None
    ac_hemi: str | None = None
    an_afr: int | None = None
    an_amr: int | None = None
    an_asj: int | None = None
    an_eas: int | None = None
    an_fin: int | None = None
    an_nfe: int | None = None
    an_oth: int | None = None
    an_sas: int | None = None
    an_male: int | None = None
    an_female: int | None = None
    hom_afr: int | None = None
    hom_amr: int | None = None
    hom_asj: int | None = None
    hom_eas: int | None = None
    hom_fin: int | None = None
    hom_nfe: int | None = None
    hom_oth: int | None = None
    hom_sas: int | None = None
    hom_male: int | None = None
    hom_female: int | None = None
    hemi_afr: int | None = None
    hemi_amr: int | None = None
    hemi_asj: int | None = None
    hemi_eas: int | None = None
    hemi_fin: int | None = None
    hemi_nfe: int | None = None
    hemi_oth: int | None = None
    hemi_sas: int | None = None
    af_afr: float | None = None
    af_amr: float | None = None
    af_asj: float | None = None
    af_eas: float | None = None
    af_fin: float | None = None
    af_nfe: float | None = None
    af_oth: float | None = None
    af_sas: float | None = None
    af_male: float | None = None
    af_female: float | None = None
    indel_original_representation: str | None = None


class GnomadExome(_GeneratedBase):
    version: str | None = None
    filter: str | None = None
    ac: int | None = None
    an: int | None = None
    af: float | None = None
    ac_afr: int | None = None
    ac_amr: int | None = None
    ac_ami: int | None = None
    ac_asj: int | None = None
    ac_eas: int | None = None
    ac_eas_kor: int | None = None
    ac_eas_jpn: int | None = None
    ac_eas_oea: int | None = None
    ac_fin: int | None = None
    ac_nfe: int | None = None
    ac_mid: int | None = None
    ac_nfe_bgr: int | None = None
    ac_nfe_est: int | None = None
    ac_nfe_nwe: int | None = None
    ac_nfe_onf: int | None = None
    ac_nfe_seu: int | None = None
    ac_nfe_swe: int | None = None
    ac_oth: int | None = None
    ac_sas: int | None = None
    ac_afr_male: int | None = None
    ac_amr_male: int | None = None
    ac_ami_male: int | None = None
    ac_asj_male: int | None = None
    ac_eas_male: int | None = None
    ac_fin_male: int | None = None
    ac_nfe_male: int | None = None
    ac_mid_male: int | None = None
    ac_oth_male: int | None = None
    ac_sas_male: int | None = None
    ac_afr_female: int | None = None
    ac_amr_female: int | None = None
    ac_ami_female: int | None = None
    ac_asj_female: int | None = None
    ac_eas_female: int | None = None
    ac_fin_female: int | None = None
    ac_nfe_female: int | None = None
    ac_mid_female: int | None = None
    ac_oth_female: int | None = None
    ac_sas_female: int | None = None
    ac_male: int | None = None
    ac_female: int | None = None
    an_afr: int | None = None
    an_amr: int | None = None
    an_ami: int | None = None
    an_asj: int | None = None
    an_eas: int | None = None
    an_eas_kor: int | None = None
    an_eas_jpn: int | None = None
    an_eas_oea: int | None = None
    an_fin: int | None = None
    an_nfe: int | None = None
    an_mid: int | None = None
    an_nfe_bgr: int | None = None
    an_nfe_est: int | None = None
    an_nfe_nwe: int | None = None
    an_nfe_onf: int | None = None
    an_nfe_seu: int | None = None
    an_nfe_swe: int | None = None
    an_oth: int | None = None
    an_sas: int | None = None
    an_afr_male: int | None = None
    an_amr_male: int | None = None
    an_ami_male: int | None = None
    an_asj_male: int | None = None
    an_eas_male: int | None = None
    an_fin_male: int | None = None
    an_nfe_male: int | None = None
    an_mid_male: int | None = None
    an_oth_male: int | None = None
    an_sas_male: int | None = None
    an_afr_female: int | None = None
    an_amr_female: int | None = None
    an_ami_female: int | None = None
    an_asj_female: int | None = None
    an_eas_female: int | None = None
    an_fin_female: int | None = None
    an_nfe_female: int | None = None
    an_mid_female: int | None = None
    an_oth_female: int | None = None
    an_sas_female: int | None = None
    an_male: int | None = None
    an_female: int | None = None
    nhomalt: int | None = None
    nhomalt_afr: int | None = None
    nhomalt_amr: int | None = None
    nhomalt_ami: int | None = None
    nhomalt_asj: int | None = None
    nhomalt_eas: int | None = None
    nhomalt_eas_kor: int | None = None
    nhomalt_eas_jpn: int | None = None
    nhomalt_eas_oea: int | None = None
    nhomalt_fin: int | None = None
    nhomalt_nfe: int | None = None
    nhomalt_mid: int | None = None
    nhomalt_nfe_bgr: int | None = None
    nhomalt_nfe_est: int | None = None
    nhomalt_nfe_nwe: int | None = None
    nhomalt_nfe_onf: int | None = None
    nhomalt_nfe_seu: int | None = None
    nhomalt_nfe_swe: int | None = None
    nhomalt_oth: int | None = None
    nhomalt_sas: int | None = None
    nhomalt_afr_male: int | None = None
    nhomalt_amr_male: int | None = None
    nhomalt_ami_male: int | None = None
    nhomalt_asj_male: int | None = None
    nhomalt_eas_male: int | None = None
    nhomalt_fin_male: int | None = None
    nhomalt_nfe_male: int | None = None
    nhomalt_mid_male: int | None = None
    nhomalt_oth_male: int | None = None
    nhomalt_sas_male: int | None = None
    nhomalt_afr_female: int | None = None
    nhomalt_amr_female: int | None = None
    nhomalt_ami_female: int | None = None
    nhomalt_asj_female: int | None = None
    nhomalt_eas_female: int | None = None
    nhomalt_fin_female: int | None = None
    nhomalt_nfe_female: int | None = None
    nhomalt_mid_female: int | None = None
    nhomalt_oth_female: int | None = None
    nhomalt_sas_female: int | None = None
    nhomalt_male: int | None = None
    nhomalt_female: int | None = None
    age_hist_het_under_30: int | None = None
    age_hist_het_30_35: int | None = None
    age_hist_het_35_40: int | None = None
    age_hist_het_40_45: int | None = None
    age_hist_het_45_50: int | None = None
    age_hist_het_50_55: int | None = None
    age_hist_het_55_60: int | None = None
    age_hist_het_60_65: int | None = None
    age_hist_het_65_70: int | None = None
    age_hist_het_70_75: int | None = None
    age_hist_het_75_80: int | None = None
    age_hist_het_over_80: int | None = None
    age_hist_hom_under_30: int | None = None
    age_hist_hom_30_35: int | None = None
    age_hist_hom_35_40: int | None = None
    age_hist_hom_40_45: int | None = None
    age_hist_hom_45_50: int | None = None
    age_hist_hom_50_55: int | None = None
    age_hist_hom_55_60: int | None = None
    age_hist_hom_60_65: int | None = None
    age_hist_hom_65_70: int | None = None
    age_hist_hom_70_75: int | None = None
    age_hist_hom_75_80: int | None = None
    age_hist_hom_over_80: int | None = None
    variant_type: str | None = Field(
        None,
        description="Only populated for multi-variants, possible values are: "
        "multi-snv, multi-indel, or mixed",
    )
    segdup: bool | None = Field(
        None,
        description="is set if the variant falls within a segmental duplication region",
    )
    lcr: bool | None = None
    original_variant: str | None = None
    main_data: str | None = None
    nonpar: int | None = None


class GnomadExomesCoverageItem(_GeneratedBase):
    version: str | None = None
    coverage_mean: list[Any] | None = None
    coverage_median: list[Any] | None = None
    coverage_20_frequency: list[Any] | None = None


class GnomadGenome(_GeneratedBase):
    version: str | None = None
    filter: str | None = None
    ac: int | None = None
    an: int | None = None
    af: float | None = None
    ac_afr: int | None = None
    ac_amr: int | None = None
    ac_ami: int | None = None
    ac_asj: int | None = None
    ac_eas: int | None = None
    ac_eas_kor: int | None = None
    ac_eas_jpn: int | None = None
    ac_eas_oea: int | None = None
    ac_fin: int | None = None
    ac_nfe: int | None = None
    ac_mid: int | None = None
    ac_nfe_bgr: int | None = None
    ac_nfe_est: int | None = None
    ac_nfe_nwe: int | None = None
    ac_nfe_onf: int | None = None
    ac_nfe_seu: int | None = None
    ac_nfe_swe: int | None = None
    ac_oth: int | None = None
    ac_sas: int | None = None
    ac_afr_male: int | None = None
    ac_amr_male: int | None = None
    ac_ami_male: int | None = None
    ac_asj_male: int | None = None
    ac_eas_male: int | None = None
    ac_fin_male: int | None = None
    ac_nfe_male: int | None = None
    ac_mid_male: int | None = None
    ac_oth_male: int | None = None
    ac_sas_male: int | None = None
    ac_afr_female: int | None = None
    ac_amr_female: int | None = None
    ac_ami_female: int | None = None
    ac_asj_female: int | None = None
    ac_eas_female: int | None = None
    ac_fin_female: int | None = None
    ac_nfe_female: int | None = None
    ac_mid_female: int | None = None
    ac_oth_female: int | None = None
    ac_sas_female: int | None = None
    ac_male: int | None = None
    ac_female: int | None = None
    an_afr: int | None = None
    an_amr: int | None = None
    an_ami: int | None = None
    an_asj: int | None = None
    an_eas: int | None = None
    an_eas_kor: int | None = None
    an_eas_jpn: int | None = None
    an_eas_oea: int | None = None
    an_fin: int | None = None
    an_nfe: int | None = None
    an_mid: int | None = None
    an_nfe_bgr: int | None = None
    an_nfe_est: int | None = None
    an_nfe_nwe: int | None = None
    an_nfe_onf: int | None = None
    an_nfe_seu: int | None = None
    an_nfe_swe: int | None = None
    an_oth: int | None = None
    an_sas: int | None = None
    an_afr_male: int | None = None
    an_amr_male: int | None = None
    an_ami_male: int | None = None
    an_asj_male: int | None = None
    an_eas_male: int | None = None
    an_fin_male: int | None = None
    an_nfe_male: int | None = None
    an_mid_male: int | None = None
    an_oth_male: int | None = None
    an_sas_male: int | None = None
    an_afr_female: int | None = None
    an_amr_female: int | None = None
    an_ami_female: int | None = None
    an_asj_female: int | None = None
    an_eas_female: int | None = None
    an_fin_female: int | None = None
    an_nfe_female: int | None = None
    an_mid_female: int | None = None
    an_oth_female: int | None = None
    an_sas_female: int | None = None
    an_male: int | None = None
    an_female: int | None = None
    nhomalt: int | None = None
    nhomalt_afr: int | None = None
    nhomalt_amr: int | None = None
    nhomalt_ami: int | None = None
    nhomalt_asj: int | None = None
    nhomalt_eas: int | None = None
    nhomalt_eas_kor: int | None = None
    nhomalt_eas_jpn: int | None = None
    nhomalt_eas_oea: int | None = None
    nhomalt_fin: int | None = None
    nhomalt_nfe: int | None = None
    nhomalt_mid: int | None = None
    nhomalt_nfe_bgr: int | None = None
    nhomalt_nfe_est: int | None = None
    nhomalt_nfe_nwe: int | None = None
    nhomalt_nfe_onf: int | None = None
    nhomalt_nfe_seu: int | None = None
    nhomalt_nfe_swe: int | None = None
    nhomalt_oth: int | None = None
    nhomalt_sas: int | None = None
    nhomalt_afr_male: int | None = None
    nhomalt_amr_male: int | None = None
    nhomalt_ami_male: int | None = None
    nhomalt_asj_male: int | None = None
    nhomalt_eas_male: int | None = None
    nhomalt_fin_male: int | None = None
    nhomalt_nfe_male: int | None = None
    nhomalt_mid_male: int | None = None
    nhomalt_oth_male: int | None = None
    nhomalt_sas_male: int | None = None
    nhomalt_afr_female: int | None = None
    nhomalt_amr_female: int | None = None
    nhomalt_ami_female: int | None = None
    nhomalt_asj_female: int | None = None
    nhomalt_eas_female: int | None = None
    nhomalt_fin_female: int | None = None
    nhomalt_nfe_female: int | None = None
    nhomalt_mid_female: int | None = None
    nhomalt_oth_female: int | None = None
    nhomalt_sas_female: int | None = None
    nhomalt_male: int | None = None
    nhomalt_female: int | None = None
    age_hist_het_under_30: int | None = None
    age_hist_het_30_35: int | None = None
    age_hist_het_35_40: int | None = None
    age_hist_het_40_45: int | None = None
    age_hist_het_45_50: int | None = None
    age_hist_het_50_55: int | None = None
    age_hist_het_55_60: int | None = None
    age_hist_het_60_65: int | None = None
    age_hist_het_65_70: int | None = None
    age_hist_het_70_75: int | None = None
    age_hist_het_75_80: int | None = None
    age_hist_het_over_80: int | None = None
    age_hist_hom_under_30: int | None = None
    age_hist_hom_30_35: int | None = None
    age_hist_hom_35_40: int | None = None
    age_hist_hom_40_45: int | None = None
    age_hist_hom_45_50: int | None = None
    age_hist_hom_50_55: int | None = None
    age_hist_hom_55_60: int | None = None
    age_hist_hom_60_65: int | None = None
    age_hist_hom_65_70: int | None = None
    age_hist_hom_70_75: int | None = None
    age_hist_hom_75_80: int | None = None
    age_hist_hom_over_80: int | None = None
    variant_type: str | None = Field(
        None,
        description="Only populated for multi-variants, "
        "possible values are: multi-snv, multi-indel, or mixed",
    )
    segdup: bool | None = Field(
        None,
        description="is set if the variant falls within "
        "a segmental duplication region",
    )
    lcr: bool | None = None
    original_variant: str | None = None
    main_data: str | None = None
    nonpar: int | None = None


class GnomadGenomesCoverageItem(_GeneratedBase):
    version: str | None = None
    coverage_mean: list[Any] | None = None
    coverage_median: list[Any] | None = None
    coverage_20_frequency: list[Any] | None = None


class ThousandGenome(_GeneratedBase):
    version: str | None = None
    ac: list[int | None] | None = None
    af: list[float | None] | None = None
    an: list[int | None] | None = None
    ns: list[int | None] | None = None
    afr_af: list[float | None] | None = None
    amr_af: list[float | None] | None = None
    eas_af: list[float | None] | None = None
    eur_af: list[float | None] | None = None
    sas_af: list[float | None] | None = None
    main_data: str | None = None


class GerpItem(_GeneratedBase):
    version: str | None = None
    gerp_nr: list[float | None] | None = None
    gerp_rs: list[float | None] | None = None


class IsbKaviar3Item(_GeneratedBase):
    version: str | None = None
    ac: list[int | None] | None = None
    an: list[int | None] | None = None
    main_data: str | None = None


class DbnsfpItem(_GeneratedBase):
    version: str | None = None
    ensembl_proteinid: list[str | None] | None = None
    ensembl_transcriptid: list[str | None] | None = None
    mutationtaster_pred: list[str | None] | None = None
    mutationtaster_score: list[float | None] | None = None
    sift_score: list[float | None] | None = None
    sift_pred: list[str | None] | None = None
    phylop100way_vertebrate: list[float | None] | None = None
    phylop46way_placental: list[float | None] | None = None
    phylop46way_primate: list[float | None] | None = None
    mutationtaster_converted_rankscore: list[float | None] | None = None
    mutationassessor_pred: list[str | None] | None = None
    mutationassessor_score: list[float | None] | None = None
    mutationassessor_rankscore: list[float | None] | None = None
    fathmm_mkl_coding_pred: list[str | None] | None = None
    fathmm_mkl_coding_score: list[float | None] | None = None
    fathmm_mkl_coding_rankscore: list[float | None] | None = None
    fathmm_pred: list[str | None] | None = None
    fathmm_score: list[float | None] | None = None
    fathmm_converted_rankscore: list[float | None] | None = None
    sift_converted_rankscore: list[float | None] | None = None
    metasvm_pred: list[str | None] | None = None
    metasvm_score: list[float | None] | None = None
    metasvm_rankscore: list[float | None] | None = None
    metalr_pred: list[str | None] | None = None
    metalr_score: list[float | None] | None = None
    metalr_rankscore: list[float | None] | None = None
    provean_pred: list[str | None] | None = None
    provean_score: list[float | None] | None = None
    provean_converted_rankscore: list[float | None] | None = None
    lrt_pred: list[str | None] | None = None
    lrt_score: list[float | None] | None = None
    lrt_converted_rankscore: list[float | None] | None = None
    lrt_omega: list[float | None] | None = None
    cadd_raw: list[float | None] | None = None
    cadd_raw_rankscore: list[float | None] | None = None
    cadd_phred: list[float | None] | None = None
    gm12878_confidence_value: list[float | None] | None = None
    gm12878_fitcons_score: list[float | None] | None = None
    gm12878_fitcons_rankscore: list[float | None] | None = None
    siphy_29way_logodds_rankscore: list[float | None] | None = None
    siphy_29way_pi: list[float | None] | None = None
    siphy_29way_logodds: float | None = None
    phylop20way_mammalian: list[float | None] | None = None
    phylop20way_mammalian_rankscore: list[float | None] | None = None
    phylop100way_vertebrate_rankscore: list[float | None] | None = None
    phastcons20way_mammalian: list[float | None] | None = None
    phastcons20way_mammalian_rankscore: list[float | None] | None = None
    phastcons100way_vertebrate: list[float | None] | None = None
    phastcons100way_vertebrate_rankscore: list[float | None] | None = None
    vest3_score: list[float | None] | None = None
    vest3_rankscore: list[float | None] | None = None
    aloft_confidence: list[str | None] | None = None
    aloft_fraction_transcripts_affected: list[str | None] | None = None
    aloft_pred: list[str | None] | None = None
    aloft_prob_dominant: list[float | None] | None = None
    aloft_prob_recessive: list[float | None] | None = None
    aloft_prob_tolerant: list[float | None] | None = None
    bstatistic: float | None = None
    bstatistic_rankscore: float | None = None
    deogen2_pred: list[str | None] | None = None
    deogen2_rankscore: float | None = None
    deogen2_score: list[float | None] | None = None
    eigen_pc_phred_coding: float | None = None
    eigen_pc_raw_coding: float | None = None
    eigen_pc_raw_coding_rankscore: float | None = None
    eigen_pred_coding: float | None = None
    eigen_raw_coding: float | None = None
    eigen_raw_coding_rankscore: float | None = None
    fathmm_xf_coding_score: float | None = None
    fathmm_xf_coding_rankscore: float | None = None
    fathmm_xf_coding_pred: list[str | None] | None = None
    integrated_confidence_value: int | None = None
    integrated_fitcons_score: float | None = None
    integrated_fitcons_rankscore: float | None = None
    h1_hesc_confidence_value: int | None = None
    h1_hesc_fitcons_score: float | None = None
    h1_hesc_fitcons_rankscore: float | None = None
    huvec_confidence_value: int | None = None
    huvec_fitcons_score: float | None = None
    huvec_fitcons_rankscore: float | None = None
    phylop17way_primate: float | None = None
    phylop17way_primate_rankscore: float | None = None
    phylop30way_mammalian: float | None = None
    phylop30way_mammalian_rankscore: float | None = None
    phastcons17way_primate: float | None = None
    phastcons17way_primate_rankscore: float | None = None
    phastcons30way_mammalian: float | None = None
    phastcons30way_mammalian_rankscore: float | None = None
    polyphen2_hdiv_pred: list[str | None] | None = None
    polyphen2_hdiv_rankscore: float | None = None
    polyphen2_hdiv_score: list[float | None] | None = None
    polyphen2_hvar_pred: list[str | None] | None = None
    polyphen2_hvar_rankscore: float | None = None
    polyphen2_hvar_score: list[float | None] | None = None
    primateai_pred: list[str | None] | None = None
    primateai_score: list[float | None] | None = None
    primateai_rankscore: list[float | None] | None = None
    mpc_score: list[float | None] | None = None
    mpc_rankscore: float | None = None
    mutpred_score: list[float | None] | None = None
    mutpred_rankscore: float | None = None
    mvp_score: list[float | None] | None = None
    mvp_rankscore: float | None = None
    sift4g_score: list[float | None] | None = None
    sift4g_converted_rankscore: float | None = None
    sift4g_pred: list[str | None] | None = None
    revel_score: list[float | None] | None = None
    revel_rankscore: float | None = None
    list_s2_pred: list[str | None] | None = None
    list_s2_score: list[float | None] | None = None
    list_s2_rankscore: float | None = None
    bayesdel_addaf_pred: list[str | None] | None = None
    bayesdel_addaf_score: float | None = None
    bayesdel_addaf_rankscore: float | None = None
    bayesdel_noaf_pred: list[str | None] | None = None
    bayesdel_noaf_score: float | None = None
    bayesdel_noaf_rankscore: float | None = None
    metarnn_pred: list[str | None] | None = None
    metarnn_score: list[float | None] | None = None
    metarnn_rankscore: float | None = None
    m_cap_pred: list[str | None] | None = None
    m_cap_score: float | None = None
    m_cap_rankscore: float | None = None
    dann_score: float | None = None
    dann_rankscore: float | None = None
    gmvp_score: list[float | None] | None = None
    gmvp_rankscore: float | None = None
    varity_r_score: list[float | None] | None = None
    varity_r_rankscore: float | None = None
    varity_er_score: list[float | None] | None = None
    varity_er_rankscore: float | None = None
    varity_r_loo_score: list[float | None] | None = None
    varity_r_loo_rankscore: float | None = None
    varity_er_loo_score: list[float | None] | None = None
    varity_er_loo_rankscore: float | None = None
    esm1b_score: list[float | None] | None = None
    esm1b_converted_rankscore: float | None = None
    esm1b_pred: list[str | None] | None = None
    clinpred_score: float | None = None
    clinpred_rankscore: float | None = None
    clinpred_pred: list[str | None] | None = None
    phactboost_score: list[float | None] | None = None
    phactboost_rankscore: float | None = None
    mutpred2_score: list[float | None] | None = None
    mutpred2_rankscore: float | None = None
    mutpred2_pred: list[str | None] | None = None


class DannSnv(_GeneratedBase):
    version: str | None = None
    dann_score: float | None = None


class DbnsfpDbscsnvItem(_GeneratedBase):
    version: str | None = None
    ada_score: list[float | None] | None = None
    rf_score: list[float | None] | None = None


class NcbiDbsnpItem(_GeneratedBase):
    version: str | None = None
    rsid: list[int | None] | None = None


class SangerCosmicItem(_GeneratedBase):
    version: str | None = None
    primary_site: list[str | None] | None = None
    pub_med_references: list[Any] | None = None


class CosmicPublicEntry(_GeneratedBase):
    id: str | None = None
    num_samples: int | None = None
    is_consistent: bool | None = None


class SangerCosmicPublicItem(_GeneratedBase):
    version: str | None = None
    items: list[CosmicPublicEntry] | None = None


class DrugEntry(_GeneratedBase):
    drug_name: str | None = None
    somatic_status: str | None = None
    zygosity: str | None = None
    gene: str | None = None
    transcript: str | None = None
    census_gene: str | None = None
    pub_med_references: list[Any] | None = None
    histology_freq: list[Any] | None = None
    tissue_freq: list[Any] | None = None


class CosmicLicensedEntry(_GeneratedBase):
    entry_type: str | None = None
    cosmic_id: list[Any] | None = None
    pub_med_references: list[Any] | None = None
    legacy_cosmic_id: list[str | None] | None = None
    histology_freq: list[Any] | None = None
    genome_wide_screen_freq: list[Any] | None = None
    loh_freq: list[Any] | None = None
    age_freq: list[Any] | None = None
    zygosity_freq: list[Any] | None = None
    tumour_origin_freq: list[Any] | None = None
    somatic_status_freq: list[Any] | None = None
    primary_site_freq: list[Any] | None = None
    description: list[Any] | None = None
    accession_number: list[Any] | None = None
    fathmm_prediction: str | None = None
    fathmm_score: float | None = None
    num_entries: int | None = None
    num_samples: int | None = None
    gene: list[Any] | None = None
    fathmm_mkl_coding_score: float | None = None
    fathmm_mkl_coding_groups: str | None = None
    fathmm_mkl_non_coding_score: float | None = None
    fathmm_mkl_non_coding_groups: str | None = None
    whole_exome_freq: list[Any] | None = None
    whole_genome_reseq_freq: list[Any] | None = None
    resistance_mutation: list[Any] | None = None
    drug_entries: list[DrugEntry] | None = None


class SangerCosmicLicensedItem(_GeneratedBase):
    version: str | None = None
    items: list[CosmicLicensedEntry] | None = None


class NcbiClinvar2Item(_GeneratedBase):
    version: str | None = None
    review_status: str | None = None
    review_stars: int | None = None
    variation_id: int | None = None
    num_submitters: int | None = None
    pub_med_references: list[Any] | None = None
    clinical_significance: list[Any] | None = None
    last_evaluation: str | None = None
    origin: list[Any] | None = None
    accessions: list[Any] | None = None
    main_data: str | None = None
    names: list[Any] | None = None
    variant_type: str | None = None


class ProjectCodeItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class OncotreeCodeItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class CancerNameItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class CancerTypeItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class TissueTypeItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class IcgcSomaticItem(_GeneratedBase):
    version: str | None = None
    affected_donors: int | None = None
    mutation_id: str | None = None
    project_code: list[ProjectCodeItem] | None = None
    project_count: int | None = None
    tested_donors: int | None = None
    total_donors: int | None = None
    pub_med_references: list[Any] | None = None
    oncotree_code: list[OncotreeCodeItem] | None = None
    cancer_name: list[CancerNameItem] | None = None
    cancer_type: list[CancerTypeItem] | None = None
    tissue_type: list[TissueTypeItem] | None = None


class SexItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class AgeFreqItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class CountryItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class PatientItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class InheritanceItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class GermlineCarrierItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class AgeAtDiagnosi(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class OsStatu(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class IarcTp53GermlineItem(_GeneratedBase):
    version: str | None = None
    sex: list[SexItem] | None = None
    age_freq: list[AgeFreqItem] | None = None
    country: list[CountryItem] | None = None
    hotspot: bool | None = None
    effect: str | None = None
    pub_med_references: list[Any] | None = None
    total_samples: int | None = None
    oncotree_code: list[OncotreeCodeItem] | None = None
    cancer_name: list[CancerNameItem] | None = None
    cancer_type: list[CancerTypeItem] | None = None
    tissue_type: list[TissueTypeItem] | None = None
    patient: list[PatientItem] | None = None
    inheritance: list[InheritanceItem] | None = None
    germline_carrier: list[GermlineCarrierItem] | None = None
    age_at_diagnosis: list[AgeAtDiagnosi] | None = None
    os_status: list[OsStatu] | None = None
    unaffected: bool | None = None


class StageItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class GradeItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class InfectiousAgentItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class SampleSourceItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class RaceItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class IarcTp53SomaticItem(_GeneratedBase):
    version: str | None = None
    sex: list[SexItem] | None = None
    age_freq: list[AgeFreqItem] | None = None
    country: list[CountryItem] | None = None
    hotspot: bool | None = None
    effect: str | None = None
    pub_med_references: list[Any] | None = None
    total_samples: int | None = None
    oncotree_code: list[OncotreeCodeItem] | None = None
    cancer_name: list[CancerNameItem] | None = None
    cancer_type: list[CancerTypeItem] | None = None
    tissue_type: list[TissueTypeItem] | None = None
    structural_motif: str | None = None
    stage: list[StageItem] | None = None
    grade: list[GradeItem] | None = None
    infectious_agent: list[InfectiousAgentItem] | None = None
    sample_source: list[SampleSourceItem] | None = None
    race: list[RaceItem] | None = None
    mut_rate: float | None = None


class Evidences(_GeneratedBase):
    pub_med_references: list[Any] | None = None
    cosmic_study: list[Any] | None = None


class AssociationItem(_GeneratedBase):
    disease: str | None = None
    disease_description: str | None = None
    disease_symbol: str | None = None
    disease_alt_symbol: str | None = None
    evidences: Evidences | None = None


class UniprotVariantEntry(_GeneratedBase):
    annotation_id: str | None = None
    protein_id: str | None = None
    proteinname: str | None = None
    somaticstatus: str | None = None
    frequency: float | None = None
    gene: str | None = None
    clinicalsignificances: list[Any] | None = None
    transcripts: list[Any] | None = None
    association: list[AssociationItem] | None = None
    siftscore: str | None = None
    siftprediction: str | None = None
    polyphenscore: str | None = None
    polyphenprediction: str | None = None
    evidences: Evidences | None = None
    xrefs: dict[str, Any] | None = None
    variant_type: str | None = None
    disease: str | None = None
    disease_symbol: str | None = None
    disease_alt_symbol: str | None = None
    bed_comments: str | None = None
    pub_med_references: list[Any] | None = None


class UniprotVariant(_GeneratedBase):
    version: str | None = None
    items: list[UniprotVariantEntry] | None = None


class UoiDvdItem(_GeneratedBase):
    version: str | None = None
    comment: str | None = None
    disease: str | None = None
    pathogenicity: str | None = None
    pub_med_references: list[Any] | None = None


class PmkbInterpretation(_GeneratedBase):
    tier: int | None = None
    definition: list[Any] | None = None
    interpretations: str | None = None
    tissues: list[Any] | None = None
    tumour_types: list[Any] | None = None
    disease_or_trait: str | None = None
    pub_med_references: list[Any] | None = None
    variants: list[Any] | None = None


class WeillCornellMedicinePmkbItem(_GeneratedBase):
    version: str | None = None
    items: list[PmkbInterpretation] | None = None


class AscoEntry(_GeneratedBase):
    asco_citation_id: str | None = None
    asco_abstract_id: str | None = None


class AssertionDetail(_GeneratedBase):
    amp_category: str | None = None
    assertion_civic_url: str | None = None
    assertion_description: str | None = None
    assertion_direction: str | None = None
    assertion_id: str | None = None
    assertion_summary: str | None = None
    assertion_type: str | None = None
    clinical_significance: str | None = None
    disease: str | None = None
    doid: str | None = None
    drugs: list[str | None] | None = None
    evidence_item_ids: list[str | None] | None = None
    fda_companion_test: bool | None = None
    gene: str | None = None
    nccn_guideline: str | None = None
    nccn_guideline_version: str | None = None
    normalized_drug: list[str | None] | None = None
    regulatory_approval: bool | None = None


class GroupDetails(_GeneratedBase):
    description: str | None = None
    variant_group_civic_url: str | None = None


class VariantGroup(_GeneratedBase):
    group: str | None = None
    group_details: GroupDetails | None = None


class VariantItem(_GeneratedBase):
    gene: str | None = None
    hgvs: str | None = None
    variant_ids: list[str | None] | None = None


class CivicMolecularProfileDetail(_GeneratedBase):
    evidence_item_ids: list[int | None] | None = None
    name: str | None = None
    summary: str | None = None
    variant: list[VariantItem] | None = None


class MolecularProfile(_GeneratedBase):
    molecular_profile: CivicMolecularProfileDetail | None = None
    molecular_profile_civic_id: int | None = None


class CivicEvidenceEntry(_GeneratedBase):
    asco_entry: AscoEntry | None = None
    clinical_significance: str | None = None
    disease: str | None = None
    doid: str | None = None
    drug_interaction_type: str | None = None
    drugs: list[str | None] | None = None
    entrez_id: str | None = None
    evidence_civic_url: str | None = None
    evidence_direction: str | None = None
    evidence_level: str | None = None
    evidence_statement: str | None = None
    evidence_status: str | None = None
    evidence_type: str | None = None
    gene: str | None = None
    gene_civic_url: str | None = None
    last_review_date: str | None = None
    nct_ids: list[str | None] | None = None
    normalized_drug: list[str | None] | None = None
    phenotypes: list[str | None] | None = None
    pub_med_references: list[int | None] | None = None
    rating: str | None = None
    representative_transcript: str | None = None
    transcripts: list[Any] | None = None
    variant: str | None = None
    variant_civic_url: str | None = None
    variant_origin: str | None = None
    variant_summary: str | None = None
    assertion_details: list[AssertionDetail] | None = None
    civic_variant_evidence_score: str | None = None
    variant_groups: list[VariantGroup] | None = None
    molecular_profile_civic_url: str | None = None
    molecular_profiles: list[MolecularProfile] | None = None


class WustlCivicItem(_GeneratedBase):
    version: str | None = None
    items: list[CivicEvidenceEntry] | None = None


class GwasEntry(_GeneratedBase):
    gwas_symbol: str | None = None
    date: str | None = None
    study: str | None = None
    disease_or_trait: str | None = None
    mapped_traits: list[Any] | None = None
    mapped_trait_urls: list[Any] | None = None
    strongest_snp_risk_allele: str | None = None
    odds_ratio: float | None = None
    p_value: str | None = None
    confidence_range_95_low: float | None = None
    confidence_range_95_high: float | None = None
    confidence_comment: str | None = None
    initial_sample_size: str | None = None
    replication_sample_size: str | None = None
    pub_med_references: list[Any] | None = None


class Gwa(_GeneratedBase):
    version: str | None = None
    items: list[GwasEntry] | None = None


class TumorStatu(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class TumorTissueSiteItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class PathTStageItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class PathNStageItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class PathMStageItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class ClinTStageItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class ClinNStageItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class ClinMStageItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class AjccPathologicTumorStageItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class StudyNameItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class PriorDxItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class DrugItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class MeasureOfResponseItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class TherapyTypeItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class RouteOfAdministrationItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class TherapyOngoingItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class ClinicalSignificanceItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class NihGdcItem(_GeneratedBase):
    version: str | None = None
    sex: list[SexItem] | None = None
    age_freq: list[AgeFreqItem] | None = None
    os_status: list[OsStatu] | None = None
    race: list[RaceItem] | None = None
    tumor_status: list[TumorStatu] | None = None
    tumor_tissue_site: list[TumorTissueSiteItem] | None = None
    path_t_stage: list[PathTStageItem] | None = None
    path_n_stage: list[PathNStageItem] | None = None
    path_m_stage: list[PathMStageItem] | None = None
    clin_t_stage: list[ClinTStageItem] | None = None
    clin_n_stage: list[ClinNStageItem] | None = None
    clin_m_stage: list[ClinMStageItem] | None = None
    ajcc_pathologic_tumor_stage: list[AjccPathologicTumorStageItem] | None = None
    total_samples: int | None = None
    study_name: list[StudyNameItem] | None = None
    prior_dx: list[PriorDxItem] | None = None
    drug: list[DrugItem] | None = None
    measure_of_response: list[MeasureOfResponseItem] | None = None
    therapy_type: list[TherapyTypeItem] | None = None
    route_of_administration: list[RouteOfAdministrationItem] | None = None
    therapy_ongoing: list[TherapyOngoingItem] | None = None
    clinical_significance: list[ClinicalSignificanceItem] | None = None
    pub_med_references: list[Any] | None = None
    oncotree_code: list[OncotreeCodeItem] | None = None
    cancer_name: list[CancerNameItem] | None = None
    cancer_type: list[CancerTypeItem] | None = None
    tissue_type: list[TissueTypeItem] | None = None


class BravoItem(_GeneratedBase):
    version: str | None = None
    filter: str | None = None
    ac: int | None = None
    an: int | None = None
    af: float | None = None
    het: int | None = None
    hom: int | None = None
    ns: int | None = None
    vrt: int | None = None
    main_data: str | None = None
    original_variant: str | None = None


class NcbiClinvar2AnnotationItem(_GeneratedBase):
    functions: list[str | None] | None = None
    coding_impact: str | None = None
    acmg_confirmed: bool | None = None
    acmg_class: str | None = None
    acmg_reannotated: str | None = None
    source: str | None = None
    codon: int | None = None
    gene_symbol: str | None = None
    hgvs: str | None = None
    transcript: str | None = None
    review_status: str | None = None
    submission_count: int | None = None
    review_stars: int | None = None
    accession_count: int | None = None
    publication_count: int | None = None
    clinical_significance: list[str | None] | None = None
    pub_med_references: list[int | None] | None = None
    possible_functional_studies: list[str | None] | None = None
    disease_name: list[str | None] | None = None
    is_conflicting: bool | None = None
    submissions_b: int | None = None
    submissions_p: int | None = None
    submissions_vus: int | None = None


class SaphetorVarsomeAiVariantItem(_GeneratedBase):
    functions: list[str | None] | None = None
    coding_impact: str | None = None
    acmg_confirmed: bool | None = None
    acmg_class: str | None = None
    acmg_reannotated: str | None = None
    source: str | None = None
    codon: int | None = None
    gene_symbol: str | None = None
    hgvs: str | None = None
    transcript: str | None = None
    original_variant: str | None = None
    pub_med_references: list[Any] | None = None


class MitimpactItem(_GeneratedBase):
    apogee: str | None = None
    apogee_score: float | None = None
    mitimpact_id: str | None = None


class ChopMitotipItem(_GeneratedBase):
    functions: list[str | None] | None = None
    coding_impact: str | None = None
    acmg_confirmed: bool | None = None
    acmg_class: str | None = None
    acmg_reannotated: str | None = None
    source: str | None = None
    codon: int | None = None
    gene_symbol: str | None = None
    hgvs: str | None = None
    transcript: str | None = None
    count: float | None = None
    mitotip_score: float | None = None
    mitomap_status: str | None = None
    percentage: float | None = None
    quartile: str | None = None


class ChopMitomapItem(_GeneratedBase):
    functions: list[str | None] | None = None
    coding_impact: str | None = None
    acmg_confirmed: bool | None = None
    acmg_class: str | None = None
    acmg_reannotated: str | None = None
    source: str | None = None
    codon: int | None = None
    gene_symbol: str | None = None
    hgvs: str | None = None
    transcript: str | None = None
    diseases: list[Any] | None = None
    possible_functional_studies: list[str | None] | None = None
    pub_med_references: list[int | None] | None = None


class SaphetorVarsomeCommentItem(_GeneratedBase):
    functions: list[str | None] | None = None
    coding_impact: str | None = None
    acmg_confirmed: bool | None = None
    acmg_class: str | None = None
    acmg_reannotated: str | None = None
    source: str | None = None
    codon: int | None = None
    gene_symbol: str | None = None
    hgvs: str | None = None
    transcript: str | None = None
    comment: str | None = None
    flagged_at_timestamp: str | None = None
    id: int | None = None
    saphetor_class: str | None = Field(None, alias="saphetorClass")
    user_id: int | None = None
    variant_id: int | None = None
    is_lifted_over: bool | None = None
    lifted_from: str | None = None


class SaphetorPubmeduserentryItem(_GeneratedBase):
    functions: list[str | None] | None = None
    coding_impact: str | None = None
    acmg_confirmed: bool | None = None
    acmg_class: str | None = None
    acmg_reannotated: str | None = None
    source: str | None = None
    codon: int | None = None
    gene_symbol: str | None = None
    hgvs: str | None = None
    transcript: str | None = None
    pub_med_references: list[int | None] | None = None
    pathogenicity: str | None = None
    id: int | None = None
    confirmed_by_functional_study: bool | None = Field(
        None, alias="confirmedByFunctionalStudy"
    )
    is_lifted_over: bool | None = None
    lifted_from: str | None = None


class UniprotUniprotVariant(_GeneratedBase):
    functions: list[str | None] | None = None
    coding_impact: str | None = None
    acmg_confirmed: bool | None = None
    acmg_class: str | None = None
    acmg_reannotated: str | None = None
    source: str | None = None
    codon: int | None = None
    gene_symbol: str | None = None
    hgvs: str | None = None
    transcript: str | None = None
    possible_functional_studies: list[int | None] | None = None
    pub_med_references: list[int | None] | None = None
    disease_name: list[str | None] | None = None
    disease_symbol: list[str | None] | None = None
    annotation_id: str | None = None
    variant_type: str | None = None
    disease: str | None = None


class Annotations(_GeneratedBase):
    ncbi_clinvar2: list[NcbiClinvar2AnnotationItem] | None = None
    saphetor_varsome_ai_variant: list[SaphetorVarsomeAiVariantItem] | None = None
    mitimpact: list[MitimpactItem] | None = None
    chop_mitotip: list[ChopMitotipItem] | None = None
    chop_mitomap: list[ChopMitomapItem] | None = None
    saphetor_varsome_comment: list[SaphetorVarsomeCommentItem] | None = None
    saphetor_pubmeduserentry: list[SaphetorPubmeduserentryItem] | None = None
    uniprot_uniprot_variants: list[UniprotUniprotVariant] | None = None


class KnownPathogenicityEntry(_GeneratedBase):
    annotations: Annotations | None = None


class SaphetorKnownPathogenicityItem(_GeneratedBase):
    version: str | None = None
    items: list[KnownPathogenicityEntry] | None = None


class MitotipItem(_GeneratedBase):
    count: float | None = None
    mitotip_score: float | None = None
    mitomap_status: str | None = None
    percentage: float | None = None
    quartile: str | None = None


class MitomapItem(_GeneratedBase):
    version: str | None = None
    ac: int | None = None
    af: float | None = None
    disease_status: str | None = None
    diseases: list[Any] | None = None
    heteroplasmy: str | None = None
    homoplasmy: str | None = None
    pub_med_references: list[Any] | None = None
    main_data: str | None = None


class AlphaMissenseItem(_GeneratedBase):
    version: str | None = None
    main_data: str | None = None
    alpha_missense_score: float | None = None


class ChemicalRelation(_GeneratedBase):
    significant: bool | None = None
    curator_notes: str | None = None
    annotation_id: int | None = None
    drug_variant_relation: str | None = None
    pub_med_references: list[Any] | None = None
    id: str | None = None
    name: str | None = None
    normalized_drug: list[str | None] | None = None
    association: str | None = None
    pharmacodynamic: bool | None = None
    pharmacokinetic: bool | None = None
    drug_label_annotations: list[Any] | None = None


class DiseaseRelation(_GeneratedBase):
    pub_med_references: list[Any] | None = None
    pharmacodynamic: bool | None = None
    pharmacokinetic: bool | None = None
    name: str | None = None
    association: str | None = None
    id: str | None = None


class EvidenceItem(_GeneratedBase):
    summary: str | None = None
    evidence_url: str | None = None
    evidence_id: str | None = None
    score: float | None = None
    evidence_type: str | None = None


class ClinicalAnnotation(_GeneratedBase):
    pub_med_references: list[Any] | None = None
    url: str | None = None
    annotation_text: list[Any] | None = None
    evidence: list[EvidenceItem] | None = None
    score: float | None = None
    id: int | None = None
    annotation_type: str | None = None
    chemical_relations: list[Any] | None = None
    level_of_evidence: str | None = None


class VariantInfoItem(_GeneratedBase):
    url: AnyUrl | None = None
    variant: str | None = None
    variant_id: str | None = None


class PharmgkbItem(_GeneratedBase):
    version: str | None = None
    chemical_relations: list[ChemicalRelation] | None = None
    disease_relations: list[DiseaseRelation] | None = None
    clinical_annotations: list[ClinicalAnnotation] | None = None
    variant_info: list[VariantInfoItem] | None = None


class TranscriptCandidate(_GeneratedBase):
    canonical: bool | None = None
    gene_id: int | None = None
    gene_symbol: str | None = None
    is_splicing: bool | None = None
    name: str | None = None
    coding_impact: str | None = None
    blosum_score: int | None = None
    total_coding_length: int | None = None
    total_exon_length: int | None = None
    user_specifier: bool | None = None
    gene_transcript: str | None = None


class AcmgRules(_GeneratedBase):
    approx_score: int | None = None
    benign_score: int | None = None
    benign_subscore: str | None = None
    clinical_score: float | None = None
    pathogenic_score: int | None = None
    pathogenic_subscore: str | None = None
    total_score: int | None = None
    verdict: str | None = None


class AcmgVerdict(_GeneratedBase):
    acmg_rules: AcmgRules | None = Field(None, alias="ACMG_rules")
    classifications: list[str | None] | None = None


class AcmgClassification(_GeneratedBase):
    name: str | None = None
    met_criteria: bool | None = None
    user_explain: list[str | None] | None = None
    user_explain_failed: list[str | None] | None = None
    strength: str | None = None


class AcmgSampleFindings(_GeneratedBase):
    inheritance: str | None = None
    phenotypes: str | None = None
    disease: str | None = None
    mode_of_inheritance: str | None = None
    ethinicity: str | None = None


class ThrottlingInfo(_GeneratedBase):
    throttling_msg: str | None = None


class Error(_GeneratedBase):
    classifier: str | None = None
    exception: str | None = None


class AcmgAnnotation(_GeneratedBase):
    version_name: str | None = None
    gene_symbol: str | None = None
    transcript: str | None = None
    transcript_reason: str | None = None
    transcript_candidates: list[TranscriptCandidate] | None = None
    coding_impact: str | None = None
    blosum_score: int | None = None
    verdict: AcmgVerdict | None = None
    classifications: list[AcmgClassification] | None = None
    gene_id: int | None = None
    sample_findings: AcmgSampleFindings | None = None
    throttling_info: ThrottlingInfo | None = None
    errors: list[Error] | None = None
    is_cancer_explain: str | None = None


class AmpVerdict(_GeneratedBase):
    tier: str | None = None
    approx_score: float | None = None


class UserExplain(_GeneratedBase):
    tier_1: list[Any] | None = None
    tier_2: list[Any] | None = None
    tier_3: list[Any] | None = None
    tier_4: list[Any] | None = None


class AmpClassification(_GeneratedBase):
    name: str | None = None
    tier: str | None = None
    user_explain: UserExplain | None = None
    total_samples: int | None = None
    approx_score: float | None = None


class AmpSampleFindings(_GeneratedBase):
    sex: str | None = None
    inheritance: str | None = None
    age: str | None = None
    age_match: str | None = None
    tissue_type_match: list[Any] | None = None
    cancer_type_match: list[Any] | None = None
    ethnic_frequency: str | None = None


class ApprovedTherapyDrug(_GeneratedBase):
    drug_name: str | None = None
    id: int | None = None
    normalized_drug: str | None = None


class TherapyDescription(_GeneratedBase):
    description: str | None = None
    pub_med_references: list[int | None] | None = None


class ApprovedTherapy(_GeneratedBase):
    approval_status: str | None = None
    evidence_type: str | None = None
    efficacy_evidence: str | None = None
    response_type: str | None = None
    amp_tier: str | None = None
    cap_level: str | None = None
    therapy: str | None = None
    therapy_id: int | None = None
    normalized_drug_name: str | None = None
    indication: str | None = None
    normalized_cancer: str | None = None
    pub_med_references: list[int | None] | None = None
    molecular_profile: str | None = None
    approved_authorities: list[str | None] | None = None
    drugs: list[ApprovedTherapyDrug] | None = None
    therapy_descriptions: list[TherapyDescription] | None = None


class AmpAnnotation(_GeneratedBase):
    version_name: str | None = None
    verdict: AmpVerdict | None = None
    classifications: list[AmpClassification] | None = None
    sample_findings: AmpSampleFindings | None = None
    approved_therapies: list[ApprovedTherapy] | None = None
    throttling_info: ThrottlingInfo | None = None
    errors: list[Error] | None = None


class DbnsfpPremiumItem(_GeneratedBase):
    version: str | None = None
    ensembl_proteinid: list[str | None] | None = None
    ensembl_transcriptid: list[str | None] | None = None
    polyphen2_hdiv_pred: list[str | None] | None = None
    polyphen2_hdiv_rankscore: float | None = None
    polyphen2_hdiv_score: list[float | None] | None = None
    polyphen2_hvar_pred: list[str | None] | None = None
    polyphen2_hvar_rankscore: float | None = None
    polyphen2_hvar_score: list[float | None] | None = None


class CaddItem(_GeneratedBase):
    version: str | None = None
    cadd_score: float | None = None


class SampleIdItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class SampleTypeItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class MutationStatu(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class ValidationStatu(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class CenterItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class OsMonth(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class DfsMonth(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class PfsStatu(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class RadiationTherapyItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class NewTumorEventAfterInitialTreatmentItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class DssStatu(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class SomaticStatusFreqItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class CbioPortalItem(_GeneratedBase):
    version: str | None = None
    total_samples: int | None = None
    sample_id: list[SampleIdItem] | None = None
    sample_type: list[SampleTypeItem] | None = None
    study_name: list[StudyNameItem] | None = None
    mutation_status: list[MutationStatu] | None = None
    validation_status: list[ValidationStatu] | None = None
    center: list[CenterItem] | None = None
    t_ref_count: int | None = None
    t_alt_count: int | None = None
    n_ref_count: int | None = None
    n_alt_count: int | None = None
    n_depth: int | None = None
    t_depth: int | None = None
    canonical: bool | None = None
    hotspot: bool | None = None
    ensp: str | None = None
    ccds: str | None = None
    cdsposition: str | None = None
    cdnaposition: str | None = None
    biotype: str | None = None
    uniparc: str | None = None
    pick: float | None = None
    sex: list[SexItem] | None = None
    age_freq: list[AgeFreqItem] | None = None
    os_months: list[OsMonth] | None = None
    os_status: list[OsStatu] | None = None
    race: list[RaceItem] | None = None
    tumor_status: list[TumorStatu] | None = None
    dfs_months: list[DfsMonth] | None = None
    path_t_stage: list[PathTStageItem] | None = None
    pfs_status: list[PfsStatu] | None = None
    radiation_therapy: list[RadiationTherapyItem] | None = None
    path_n_stage: list[PathNStageItem] | None = None
    path_m_stage: list[PathMStageItem] | None = None
    new_tumor_event_after_initial_treatment: (
        list[NewTumorEventAfterInitialTreatmentItem] | None
    ) = None
    ajcc_pathologic_tumor_stage: list[AjccPathologicTumorStageItem] | None = None
    dss_status: list[DssStatu] | None = None
    prior_dx: list[PriorDxItem] | None = None
    somatic_status_freq: list[SomaticStatusFreqItem] | None = None
    grade: list[GradeItem] | None = None
    pub_med_references: list[Any] | None = None
    oncotree_code: list[OncotreeCodeItem] | None = None
    cancer_name: list[CancerNameItem] | None = None
    cancer_type: list[CancerTypeItem] | None = None
    tissue_type: list[TissueTypeItem] | None = None


class SomaticItem(_GeneratedBase):
    key: str | None = None
    value: int | None = None


class CancerHotspot(_GeneratedBase):
    version: str | None = None
    total_samples: int | None = None
    t_ref_count: int | None = None
    t_alt_count: int | None = None
    n_ref_count: int | None = None
    n_alt_count: int | None = None
    n_depth: int | None = None
    t_depth: int | None = None
    somatic: list[SomaticItem] | None = None
    canonical: bool | None = None
    ensp: str | None = None
    ccds: str | None = None
    cdsposition: str | None = None
    cdnaposition: str | None = None
    biotype: str | None = None
    feature: str | None = None
    uniparc: str | None = None
    pick: float | None = None
    pub_med_references: list[Any] | None = None
    oncotree_code: list[OncotreeCodeItem] | None = None
    cancer_name: list[CancerNameItem] | None = None
    cancer_type: list[CancerTypeItem] | None = None
    tissue_type: list[TissueTypeItem] | None = None


class JaxCkbItem(_GeneratedBase):
    ckb_id: int | None = None
    version: str | None = None
    coding_impact: str | None = None
    evidence: list[Any] | None = None
    extended_evidence: list[Any] | None = None
    gene_variant_descriptions: list[Any] | None = None
    protein_effect: str | None = None
    cap_asco_evidence_level: str | None = None
    polymorphism: bool | None = None
    transforming_activity: bool | None = None
    associated_with_drug_resistance: bool | None = None


class Phastcons100wayItem(_GeneratedBase):
    version: str | None = None
    conservation_score: list[Decimal | None] | None = None


class Phylop100wayItem(_GeneratedBase):
    version: str | None = None
    conservation_score: list[Decimal | None] | None = None


class MaxentscanItem(_GeneratedBase):
    version: str | None = None
    maxentscan_score: list[float | None] | None = None


class GnomadMitoItem(_GeneratedBase):
    version: str | None = None
    filter: str | None = None
    ac: int | None = None
    an: int | None = None
    af: float | None = None
    ac_afr: int | None = None
    ac_ami: int | None = None
    ac_amr: int | None = None
    ac_asj: int | None = None
    ac_eas: int | None = None
    ac_fin: int | None = None
    ac_nfe: int | None = None
    ac_oth: int | None = None
    ac_sas: int | None = None
    ac_mid: int | None = None
    ac_hom: int | None = None
    ac_het: int | None = None
    ac_afr_hom: int | None = None
    ac_ami_hom: int | None = None
    ac_amr_hom: int | None = None
    ac_asj_hom: int | None = None
    ac_eas_hom: int | None = None
    ac_fin_hom: int | None = None
    ac_nfe_hom: int | None = None
    ac_oth_hom: int | None = None
    ac_sas_hom: int | None = None
    ac_mid_hom: int | None = None
    ac_afr_het: int | None = None
    ac_ami_het: int | None = None
    ac_amr_het: int | None = None
    ac_asj_het: int | None = None
    ac_eas_het: int | None = None
    ac_fin_het: int | None = None
    ac_nfe_het: int | None = None
    ac_oth_het: int | None = None
    ac_sas_het: int | None = None
    ac_mid_het: int | None = None
    an_afr: int | None = None
    an_ami: int | None = None
    an_amr: int | None = None
    an_asj: int | None = None
    an_eas: int | None = None
    an_fin: int | None = None
    an_nfe: int | None = None
    an_oth: int | None = None
    an_sas: int | None = None
    an_mid: int | None = None
    age_hist_het_under_30: int | None = None
    age_hist_het_30_35: int | None = None
    age_hist_het_35_40: int | None = None
    age_hist_het_40_45: int | None = None
    age_hist_het_45_50: int | None = None
    age_hist_het_50_55: int | None = None
    age_hist_het_55_60: int | None = None
    age_hist_het_60_65: int | None = None
    age_hist_het_65_70: int | None = None
    age_hist_het_70_75: int | None = None
    age_hist_het_75_80: int | None = None
    age_hist_het_over_80: int | None = None
    age_hist_hom_under_30: int | None = None
    age_hist_hom_30_35: int | None = None
    age_hist_hom_35_40: int | None = None
    age_hist_hom_40_45: int | None = None
    age_hist_hom_45_50: int | None = None
    age_hist_hom_50_55: int | None = None
    age_hist_hom_55_60: int | None = None
    age_hist_hom_60_65: int | None = None
    age_hist_hom_65_70: int | None = None
    age_hist_hom_70_75: int | None = None
    age_hist_hom_75_80: int | None = None
    age_hist_hom_over_80: int | None = None
    mitotip_score: float | None = None
    mitotip_trna_prediction: str | None = None
    pon_ml_probability_of_pathogenicity: float | None = None
    pon_mt_trna_prediction: str | None = None
    original_variant: str | None = None
    main_data: str | None = None


class VariantPubmedAutomapItem(_GeneratedBase):
    version: str | None = None
    pub_med_references: list[int | None] | None = None


class DocmDisease(_GeneratedBase):
    disease: str | None = None
    doid: str | None = None
    pub_med_references: list[Any] | None = None
    tags: list[Any] | None = None


class DocmDrug(_GeneratedBase):
    effect: str | None = None
    evidence: str | None = None
    pathway: str | None = None
    source: str | None = None
    status: str | None = None
    therapeutic_context: str | None = None
    pub_med_references: list[Any] | None = None


class WustlDocmItem(_GeneratedBase):
    version: str | None = None
    diseases: list[DocmDisease] | None = None
    drugs: list[DocmDrug] | None = None
    pub_med_references: list[Any] | None = None
    hgvs: str | None = None


class EveScoreEntry(_GeneratedBase):
    aa_change: str | None = None
    class_75: str | None = None
    current_variant: bool | None = None
    eve_score: Decimal | None = None


class EveItem(_GeneratedBase):
    version: str | None = None
    items: list[list[EveScoreEntry]] | None = None


class Reference(_GeneratedBase):
    pub_med_references: list[int | None] | None = None
    reference_number: int | None = None
    title: str | None = None
    source: str | None = None
    authors: str | None = None


class OmimPhenotypeEntry(_GeneratedBase):
    description: str | None = None
    mutations: str | None = None
    omim_id: int | None = None
    number: int | None = None
    phenotype_name: str | None = None
    alternative_phenotype_names: list[str | None] | None = None
    references: list[Reference] | None = None


class OmimItem(_GeneratedBase):
    version: str | None = None
    items: list[OmimPhenotypeEntry] | None = None


class NihClingenVariant(_GeneratedBase):
    version: str | None = None
    approval_date: str | None = None
    disease: str | None = None
    evidence_met: list[str | None] | None = None
    evidence_not_met: list[str | None] | None = None
    expert_panel: str | None = None
    guideline: str | None = None
    mode_of_inheritance: str | None = None
    mondo_id: str | None = None
    pathogenicity: str | None = None
    pub_med_references: list[int | None] | None = None
    published_date: str | None = None
    repo_link: str | None = None
    retracted: str | None = None
    summary: str | None = None


class Gene(_GeneratedBase):
    gene_id: int | None = None
    hgnc_id: int | None = None
    gene_symbol: str | None = None


class Pathogenicity(_GeneratedBase):
    clinical_classification_submitter: str | None = None
    clinical_classification_curator: str | None = None
    effect_submitter: str | None = None
    effect_curator: str | None = None
    effect_symbol: str | None = None
    lovd_link: str | None = None


class LovdVariantInfoItem(_GeneratedBase):
    variant_id: str | None = None
    variant_notation: str | None = None


class Variant(_GeneratedBase):
    comments: list[str | None] | None = None
    is_current: bool | None = None
    is_lifted_over: bool | None = None
    lovd_link: str | None = None
    pathogenicity: Pathogenicity | None = None
    variant_info: list[LovdVariantInfoItem] | None = None


class Individual(_GeneratedBase):
    comments: list[str | None] | None = None
    gender: str | None = None
    phenotypes: list[str | None] | None = None
    pub_med_references: list[int | None] | None = None
    variants: list[Variant] | None = None


class LumcLovdItem(_GeneratedBase):
    version: str | None = None
    genes: list[Gene] | None = None
    individuals: list[Individual] | None = None
    is_lifted_over: bool | None = None
    pathogenicities: list[Pathogenicity] | None = None


class Abstract(_GeneratedBase):
    abstract: str | None = None
    link: str | None = None


class MainType(_GeneratedBase):
    id: int | None = None
    name: str | None = None
    tumor_form: str | None = None


class TumorType(_GeneratedBase):
    children: dict[str, Any] | None = None
    code: str | None = None
    color: str | None = None
    id: int | None = None
    level: int | None = None
    main_type: MainType | None = None
    name: str | None = None
    parent: str | None = None
    tissue: str | None = None
    tumor_form: str | None = None


class DiagnosticImplication(_GeneratedBase):
    abstracts: list[Abstract] | None = None
    alterations: list[str | None] | None = None
    description: str | None = None
    level_of_evidence: str | None = None
    pmids: list[str | None] | None = None
    tumor_type: TumorType | None = None


class PrognosticTumorType(_GeneratedBase):
    children: dict[str, Any] | None = None
    code: str | None = None
    color: str | None = None
    id: int | None = None
    level: int | None = None
    main_type: MainType | None = None
    name: str | None = None
    parent: str | None = None
    tissue: str | None = None
    tumor_form: str | None = None


class PrognosticImplication(_GeneratedBase):
    abstracts: list[Abstract] | None = None
    alterations: list[str | None] | None = None
    description: str | None = None
    level_of_evidence: str | None = None
    pmids: list[str | None] | None = None
    tumor_type: PrognosticTumorType | None = None


class OncokbDrug(_GeneratedBase):
    drug_name: str | None = None
    ncit_code: str | None = None


class LevelAssociatedCancerType(_GeneratedBase):
    children: dict[str, Any] | None = None
    code: str | None = None
    color: str | None = None
    id: int | None = None
    level: int | None = None
    main_type: MainType | None = None
    name: str | None = None
    parent: str | None = None
    tissue: str | None = None
    tumor_form: str | None = None


class Treatment(_GeneratedBase):
    abstracts: list[Abstract] | None = None
    alterations: list[str | None] | None = None
    description: str | None = None
    approved_indications: list[Any] | None = None
    drugs: list[OncokbDrug] | None = None
    fda_level: str | None = None
    level: str | None = None
    level_associated_cancer_type: LevelAssociatedCancerType | None = None
    pmids: list[str | None] | None = None


class OncokbItem(_GeneratedBase):
    version: str | None = None
    allele_exist: bool | None = None
    diagnostic_implications: list[DiagnosticImplication] | None = None
    diagnostic_summary: str | None = None
    gene_exist: bool | None = None
    gene_summary: str | None = None
    highest_diagnostic_implication_level: str | None = None
    highest_fda_level: str | None = None
    highest_prognostic_implication_level: str | None = None
    highest_resistance_level: str | None = None
    highest_sensitive_level: str | None = None
    hotspot: bool | None = None
    last_update: str | None = None
    mutation_effect: dict[str, Any] | None = None
    oncogenic: str | None = None
    other_significant_resistance_levels: list[str | None] | None = None
    other_significant_sensitive_levels: list[str | None] | None = None
    prognostic_implications: list[PrognosticImplication] | None = None
    prognostic_summary: str | None = None
    query: dict[str, Any] | None = None
    treatments: list[Treatment] | None = None
    tumor_type_summary: str | None = None
    variant_exist: bool | None = None
    variant_summary: str | None = None
    variant_id: int | None = None
    vus: bool | None = None


class SpliceVaultEntry(_GeneratedBase):
    event_rank: int | None = None
    exon_no: int | None = None
    tx_id: str | None = None
    gtex_sample_count: int | None = None
    skipped_exons_id: str | None = None
    splicing_event_class: str | None = None
    sra_sample_count: int | None = None
    ss_type: str | None = None
    cryptic_distance: int | None = None
    skipped_exons_count: int | None = None
    gtex_max_uniq_map_reads: int | None = None
    intropolis_sample_count: int | None = None
    splice_junction_coordinates: str | None = None
    missplicing_inframe: bool | None = None


class KncSpliceVaultItem(_GeneratedBase):
    version: str | None = None
    items: list[list[SpliceVaultEntry]] | None = None


class VariantSpecificDetail(_GeneratedBase):
    classification: str | None = None
    pubmedid: int | None = None
    validation_doi: str | None = None
    validation_metric1: str | None = None
    validation_metric2: str | None = None
    tissue: str | None = None
    method: str | None = None
    outcome: str | None = None


class SplicevardbJson(_GeneratedBase):
    variant_specific_details: list[VariantSpecificDetail] | None = None
    overall_validation_method: list[str | None] | None = None
    overall_classification: str | None = None
    hgvs_refseq: str | None = None
    gene_symbol_list: str | None = None
    locations: str | None = None


class CompbioSpliceVarDb(_GeneratedBase):
    version: str | None = None
    splicevardb_json: SplicevardbJson | None = None


class VariantVariantApi(_GeneratedBase):
    original_variant: str | None = None
    chromosome: str | None = None
    alt: str | None = None
    ref: str | None = None
    pos: int | None = None
    regions: Regions | None = None
    variant_type: str | None = None
    cytobands: str | None = None
    refseq_transcripts: list[RefseqTranscript] | None = None
    ensembl_transcripts: list[EnsemblTranscript] | None = None
    broad_exac: list[BroadExacItem] | None = None
    gnomad_exomes: list[GnomadExome] | None = None
    gnomad_exomes_coverage: list[GnomadExomesCoverageItem] | None = None
    gnomad_genomes: list[GnomadGenome] | None = None
    gnomad_genomes_coverage: list[GnomadGenomesCoverageItem] | None = None
    thousand_genomes: list[ThousandGenome] | None = None
    gerp: list[GerpItem] | None = None
    isb_kaviar3: list[IsbKaviar3Item] | None = None
    dbnsfp: list[DbnsfpItem] | None = None
    dann_snvs: list[DannSnv] | None = None
    dbnsfp_dbscsnv: list[DbnsfpDbscsnvItem] | None = None
    ncbi_dbsnp: list[NcbiDbsnpItem] | None = None
    sanger_cosmic: list[SangerCosmicItem] | None = None
    sanger_cosmic_public: list[SangerCosmicPublicItem] | None = None
    sanger_cosmic_licensed: list[SangerCosmicLicensedItem] | None = None
    ncbi_clinvar2: list[NcbiClinvar2Item] | None = None
    icgc_somatic: list[IcgcSomaticItem] | None = None
    iarc_tp53_germline: list[IarcTp53GermlineItem] | None = None
    iarc_tp53_somatic: list[IarcTp53SomaticItem] | None = None
    pub_med_articles: dict[str, Any] | None = None
    publications: dict[str, Any] | None = None
    publication_counts: list[Any] | None = None
    uniprot_variants: list[UniprotVariant] | None = None
    uoi_dvd: list[UoiDvdItem] | None = None
    weill_cornell_medicine_pmkb: list[WeillCornellMedicinePmkbItem] | None = None
    wustl_civic: list[WustlCivicItem] | None = None
    gwas: list[Gwa] | None = None
    nih_gdc: list[NihGdcItem] | None = None
    bravo: list[BravoItem] | None = None
    saphetor_known_pathogenicity: list[SaphetorKnownPathogenicityItem] | None = None
    mitimpact: list[MitimpactItem] | None = None
    mitotip: list[MitotipItem] | None = None
    mitomap: list[MitomapItem] | None = None
    alpha_missense: list[AlphaMissenseItem] | None = None
    pharmgkb: list[PharmgkbItem] | None = None
    acmg_annotation: AcmgAnnotation | None = None
    amp_annotation: AmpAnnotation | None = None
    not_subscribed_sources: dict[str, Any] | None = None
    dbnsfp_premium: list[DbnsfpPremiumItem] | None = None
    cadd: list[CaddItem] | None = None
    cbio_portal: list[CbioPortalItem] | None = None
    cancer_hotspots: list[CancerHotspot] | None = None
    jax_ckb: list[JaxCkbItem] | None = None
    phastcons100way: list[Phastcons100wayItem] | None = None
    phylop100way: list[Phylop100wayItem] | None = None
    maxentscan: list[MaxentscanItem] | None = None
    gnomad_mito: list[GnomadMitoItem] | None = None
    variant_pubmed_automap: list[VariantPubmedAutomapItem] | None = None
    wustl_docm: list[WustlDocmItem] | None = None
    eve: list[EveItem] | None = None
    omim: list[OmimItem] | None = None
    nih_clingen_variants: list[NihClingenVariant] | None = None
    lumc_lovd: list[LumcLovdItem] | None = None
    oncokb: list[OncokbItem] | None = None
    knc_splice_vault: list[KncSpliceVaultItem] | None = None
    compbio_splice_var_db: CompbioSpliceVarDb | None = None


class VariantVariantBatchRequestApi(_GeneratedBase):
    variants: list[str | None] | None = Field(None, max_length=200, min_length=1)
    variants_specs: dict[str, Any] | None = None
    variants_transcripts: dict[str, Any] | None = None
