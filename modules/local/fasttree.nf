process FASTTREE {
    tag "$alignment"
    label 'process_iqtree'

    container "${ workflow.containerEngine == 'docker' ? 'arcadiascience/fasttree_2.1.11:0.0.1':
        '' }"

    publishDir(
        path: "${params.outdir}/fasttree_gene_trees",
        mode: params.publish_dir_mode,
        saveAs: { fn -> fn.substring(fn.lastIndexOf('/')+1) },
    )

    input:
    file(alignment)
    val model // not used

    output:
    path("*.treefile")  , emit: phylogeny
    path "versions.yml" , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    """
    og=\$(echo $alignment | cut -f1 -d "_")

    # Make sure the number of threads are being specified properly
    export OMP_NUM_THREADS=${task.cpus}

    # Efficiently infer a gene family tree using FastTree!
    FastTreeDblMP \\
        $args \\
        $alignment > \${og}_ft.treefile
        
    # prevent zero-length branches (sometimes inferred with fasttree)
    resolve_polytomies.R \${og}_ft.treefile resolved.tree
    mv resolved.tree \${og}_ft.treefile

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        FastTree: \$(FastTreeDblMP 2>&1 | head -n1 | cut -d" " -f5)
    END_VERSIONS
    """
}
