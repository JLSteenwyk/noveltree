// This process is originally from nf-core but is modified to remove the
// meta input

process MAFFT {
    tag "$fasta"
    //label 'process_highthread' // Possible specification for full analysis
    label 'process_medium' // Used for debugging

    conda (params.enable_conda ? "bioconda::mafft=7.490" : null)
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/mafft:7.490--h779adbc_0':
        'quay.io/biocontainers/mafft:7.490--h779adbc_0' }"

    input:
    path(fasta)

    output:
    path("*_mafft.fa") , emit: msas
    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    """
    prefix=\$(basename "${fasta}" .fa)

    # Recode any stop codons "*" as an unknown amino acid to prevent any 
    # downstream consequences
    sed -i "s/*/-/g" *.fa
    
    mafft \\
        --thread -1 \\
        ${args} ${fasta} > \${prefix}_mafft.fa

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        mafft: \$(mafft --version 2>&1 | sed 's/^v//' | sed 's/ (.*)//')
    END_VERSIONS
    """
}