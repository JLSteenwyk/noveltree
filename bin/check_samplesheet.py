#!/usr/bin/env python3

import os
import sys
import errno
import argparse


def parse_args(args=None):
    Description = "Reformat phylorthology samplesheet file and check its contents."
    Epilog = "Example usage: python check_samplesheet.py <FILE_IN> <FILE_OUT>"

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument("FILE_IN", help="Input samplesheet file.")
    parser.add_argument("FILE_OUT", help="Output file.")
    return parser.parse_args(args)


def make_dir(path):
    if len(path) > 0:
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise exception


def print_error(error, context="Line", context_str=""):
    error_str = f"ERROR: Please check samplesheet -> {error}"
    if context != "" and context_str != "":
        error_str = f"ERROR: Please check samplesheet -> {error}\n{context.strip()}: '{context_str.strip()}'"
    print(error_str)
    sys.exit(1)


def check_samplesheet(file_in, file_out):
    """
    This function checks that the samplesheet follows the following structure:
    species,file,tax1,tax2
    genus_species,genus_species.fasta,--lineage archaea_odb10,--lineage eukaryota_odb10
    """

    species_mapping_dict = {}
    with open(file_in, "r", encoding="utf-8-sig") as fin:

        ## Check header
        MIN_COLS = 6
        HEADER = ["species", "file", "tax1", "tax2", "mode", "uniprot"]
        header = [x.strip('"') for x in fin.readline().strip().split(",")]
        if header[: len(HEADER)] != HEADER:
            print(f"ERROR: Please check samplesheet header -> {','.join(header)} != {','.join(HEADER)}")
            sys.exit(1)

        ## Check sample entries
        for line in fin:
            if line.strip():
                lspl = [x.strip().strip('"') for x in line.strip().split(",")]

                ## Check valid number of columns per row
                if len(lspl) < len(HEADER):
                    print_error(
                        f"Invalid number of columns (minimum = {len(HEADER)})!",
                        "Line",
                        line,
                    )

                num_cols = len([x for x in lspl if x])
                if num_cols < MIN_COLS:
                    print_error(
                        f"Invalid number of populated columns (minimum = {MIN_COLS})!",
                        "Line",
                        line,
                    )

                ## Check sample name entries
                species, file, tax1, tax2, mode, uniprot = lspl[: len(HEADER)]
                if species.find(" ") != -1:
                    print(f"WARNING: Spaces have been replaced by underscores for sample: {species}")
                    species = species.replace(" ", "_")
                if not species:
                    print_error("Sample entry has not been specified!", "Line", line)

                ## Check fasta file extension
                for fasta in [file]:
                    if fasta:
                        if fasta.find(" ") != -1:
                            print_error("fasta file contains spaces!", "Line", line)
                        if not fasta.endswith(".fasta") and not fasta.endswith(".fa"):
                            print_error(
                                "Fasta file does not have extension '.fasta' or '.fa'!",
                                "Line",
                                line,
                            )

                ## Check strandedness
                #strandednesses = ["unstranded", "forward", "reverse"]
                #if strandedness:
                #    if strandedness not in strandednesses:
                #        print_error(
                #            f"Strandedness must be one of '{', '.join(strandednesses)}'!",
                #            "Line",
                #            line,
                #        )
                #else:
                #    print_error(
                #        f"Strandedness has not been specified! Must be one of {', '.join(strandednesses)}.",
                #        "Line",
                #        line,
                #    )

                ## populate sample data
                species_info = [file, tax1, tax2, mode, uniprot]  ## [file, tax1, tax2, mode, uniprot]

                ## Create species mapping dictionary = {species: [[ file, tax1, tax2, mode, uniprot ]]}
                if species not in species_mapping_dict:
                    species_mapping_dict[species] = [species_info]
                else:
                    if species_info in species_mapping_dict[species]:
                        print_error("Samplesheet contains duplicate rows!", "Line", line)
                    else:
                        species_mapping_dict[species].append(species_info)

    ## Write validated samplesheet with appropriate columns
    if len(species_mapping_dict) > 0:
        out_dir = os.path.dirname(file_out)
        make_dir(out_dir)
        with open(file_out, "w") as fout:
            fout.write(",".join(["species", "file", "tax1", "tax2", "mode", "uniprot"]) + "\n")
            for species in sorted(species_mapping_dict.keys()):


                ### Check that multiple runs of the same species are of the same strandedness
                #if not all(x[-1] == species_mapping_dict[species][0][-1] for x in species_mapping_dict[species]):
                #    print_error(
                #        f"Multiple runs of a species must have the same strandedness!",
                #        "Species",
                #        species,
                #    )

                for idx, val in enumerate(species_mapping_dict[species]):
                    fout.write(",".join([f"{species}_T{idx+1}"] + val) + "\n")
    else:
        print_error(f"No entries to process!", "Samplesheet: {file_in}")


def main(args=None):
    args = parse_args(args)
    check_samplesheet(args.FILE_IN, args.FILE_OUT)


if __name__ == "__main__":
    sys.exit(main())