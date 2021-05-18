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

projectDir = workflow.projectDir
ch_varsome_api_script = Channel.fromPath("${projectDir}/bin/scripts/varsome_api_run.py",  type: 'file', followLinks: false)
ch_varsome_api_src   = Channel.fromPath("${projectDir}/bin/scripts/varsome_api",  type: 'dir', followLinks: false)
ch_make_variants_list_script = Channel.fromPath("${projectDir}/bin/make_variant_list.sh",  type: 'file', followLinks: false)

// Define Process
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
