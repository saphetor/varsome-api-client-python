#!/usr/bin/env nextflow

def helpMessage() {
    log.info """
    Usage:
    The typical command for running the pipeline is as follows:
    nextflow run main.nf --bams sample.bam [Options]

    Inputs Options:
    --input         Input file

    Resource Options:
    --max_cpus      Maximum number of CPUs (int)
                    (default: $params.max_cpus)
    --max_memory    Maximum memory (memory unit)
                    (default: $params.max_memory)
    --max_time      Maximum time (time unit)
                    (default: $params.max_time)
    See here for more info: https://github.com/lifebit-ai/hla/blob/master/docs/usage.md
    """.stripIndent()
}

// Show help message
if (params.help) {
  helpMessage()
  exit 0
}

/*
 * Check all important required inputs
 */

// Check if input file for annotation is provided
if (!params.input) exit 1, "Please provide a vcf file to annotate with VEP with --input [file] argument."


// Header log info
def summary = [:]
if (workflow.revision) summary['Pipeline Release'] = workflow.revision
summary['Max Resources']    = "$params.max_memory memory, $params.max_cpus cpus, $params.max_time time per job"
if (workflow.containerEngine) summary['Container'] = "$workflow.containerEngine - $workflow.container"
summary['Output dir']       = params.outdir
summary['Launch dir']       = workflow.launchDir
summary['Working dir']      = workflow.workDir
summary['Script dir']       = workflow.projectDir
summary['User']             = workflow.userName
summary['Config Profile']   = workflow.profile
summary['Input file']       = params.input
log.info summary.collect { k,v -> "${k.padRight(20)}: $v" }.join("\n")
log.info "-\033[2m--------------------------------------------------\033[0m-"


// Define Channels from input
Channel
    .fromPath(params.input)
    .ifEmpty { exit 1, "Cannot find input file : ${params.input}" }
    .set { ch_input }

// Obtain pathogenicity filter values from file
Channel
    .fromPath(params.pathogenicity_filter_values)
    .splitText()
    .map { '"'+it.trim()+'"'}
    .toList()
    .set { ch_pathogenicity_filter_values_array }

projectDir = workflow.projectDir
ch_varsome_api_script = Channel.fromPath("${projectDir}/bin/scripts/varsome_api_run.py",  type: 'file', followLinks: false)
ch_varsome_api_src   = Channel.fromPath("${projectDir}/bin/varsome_api",  type: 'dir', followLinks: false)
ch_make_variants_list_script = Channel.fromPath("${projectDir}/bin/make_variant_list.sh",  type: 'file', followLinks: false)


process vreate_list_of_variants {

    label 'low_memory'
    publishDir "${params.outdir}", mode: 'copy'

    input:
    file(input_file) from ch_input
    file("make_variant_list.sh") from ch_make_variants_list_script

    output:
    file("${input_file.baseName}_variants.txt") into ch_variant_list

    """
    bash make_variant_list.sh ${input_file} > ${input_file.baseName}_variants.txt
    """
}


process split_variants_in_sets {

    label 'low_memory'
    publishDir "${params.outdir}/variant_sets", mode: 'copy'

    input:
    file(variant_list) from ch_variant_list

    output:
    file("${variant_list.baseName}.*") into ch_variant_query_sets

    """
    split --numeric-suffixes --suffix-length=${params.variant_query_set_suffix_lenght} --lines=${params.variant_query_size} ${variant_list} ${variant_list.baseName}.
    """
}

ch_variant_query_sets = ch_variant_query_sets.flatten()


process annotate_variants {

    publishDir "${params.outdir}/annotated_variant_sets", mode: 'copy'

    input:
    file(variant_query_set) from ch_variant_query_sets
    each file("varsome_api_run.py") from ch_varsome_api_script
    each file("varsome_api") from ch_varsome_api_src

    output:
    file("${variant_query_set}.json") into ch_annotated_variant_sets

    """
    python varsome_api_run.py \
        -g ${params.genome} \
        -k '${params.key}' \
        -i ${variant_query_set} \
        -p add-all-data=${params.add_all_data} \
           add-ACMG-annotation=${params.add_ACMG_annotation} \
           add-source-databases=${params.add_source_databases} \
           add-region-databases=${params.add_region_databases} \
           expand-pubmed-articles=${params.expand_pubmed_articles} \
        -o ${variant_query_set}_multiline.json

    jq -c '.' ${variant_query_set}_multiline.json > ${variant_query_set}.json
    #rm ${variant_query_set}_multiline.json
    """
}


process filter_variants {

    input:
    file(annotated_variant_set) from ch_annotated_variant_sets
    val(pathogenicity_filter_values_array) from ch_pathogenicity_filter_values_array

    output:
    file("${annotated_variant_set}_filtered.json") into ch_filtered_variant_sets

    """
    filters='${pathogenicity_filter_values_array}'

    cat ${annotated_variant_set} \
    | jq ".[] | select( [.acmg_annotation.verdict.ACMG_rules.verdict] | inside(\$filters) )" \
    | jq '.' -s > ${annotated_variant_set}_filtered.json
    """
}


ch_filtered_variant_sets = ch_filtered_variant_sets.collect()


process merge_filtered_variants {

    publishDir "${params.outdir}", mode: 'copy'

    input:
    file(files) from ch_filtered_variant_sets

    output:
    file("${files[1].simpleName}_merged_filtered_variants.json") into ch_merged_filtered_variants

    """
    jq -s '[.[][]]' *.json > "${files[1].simpleName}_merged_filtered_variants.json"
    """
}


/*
 * Completion notification
 */
workflow.onComplete {

    c_green = "\033[0;32m";
    c_purple = "\033[0;35m";
    c_red = "\033[0;31m";
    c_reset = "\033[0m";

    if (workflow.stats.ignoredCount > 0 && workflow.success) {
        log.info "-${c_purple}Warning, pipeline completed, but with errored process(es) ${c_reset}-"
        log.info "-${c_red}Number of ignored errored process(es) : ${workflow.stats.ignoredCount} ${c_reset}-"
        log.info "-${c_green}Number of successfully ran process(es) : ${workflow.stats.succeedCount} ${c_reset}-"
    }

    if (workflow.success) {
        log.info "-${c_purple}[lifebit-ai/vep-nf]${c_green} Pipeline completed successfully${c_reset}-"
    } else {
        log.info "-${c_purple}[lifebit-ai/vep-nf]${c_red} Pipeline completed with errors${c_reset}-"
    }

}
