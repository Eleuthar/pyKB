"""
tech in COBALT, not in PLS
tech in PLS, not in COBALT
common tech but different version
"""

import json
import argparse
import pandas as pd
import xlsxwriter
from os import system
from copy import deepcopy


def argue():
    """Mandatory and optional arguments"""
    parser = argparse.ArgumentParser(
        description="""Utility for comparing technology name between COBALT & PLS
            Usage: python3 dbdiff.py --csv export.csv --bom dx.sbom.json" [--output]
        """
    )
    parser.add_argument(
        "--csv",
        help="""Input CSV filename exported from Cobalt.
            Example: --csv input.csv """,
        type=str,
        required=True,
    )
    parser.add_argument(
        "--bom",
        help="""CycloneDX input sbom.json filename
            Example: --sbom inputDX.sbom.json """,
        type=str,
        required=True,
    )
    opt = parser.parse_args()

    return opt


def group_tech(ba: list, lt: list, pkg: list, ver: list) -> dict:
    """Group packages by version mapped to LT & BA"""
    group = {}
    for ndx, version in enumerate(ver):
        tech = pkg[ndx]
        baid = ba[ndx]
        ltid = lt[ndx]
        group.setdefault(tech, {})
        group[tech][version] = f"LT: {ltid}, BA: {baid}"
    return group


def generate_df_dict(mapping: dict, diff_rezult: set) -> dict:
    """Generate Excel dataframe based on group_tech output"""
    tech_list = []
    version_list = []
    lt_list = []
    ba_list = [ ]
    for tech in diff_rezult:
        for version_ltba in mapping[tech].items():
            version, ltba = version_ltba
            lt, ba = ltba.split()
            tech_list.append(tech)
            version_list.append(version)
            lt_list.append(lt)
            ba_list.append(ba)
    return {
        "Tech name": tech_list,
        "Version": version_list,
        "LT": lt_list,
        "BA": ba_list,
    }


def xport(data: dict, fname: str):
    """Export to xlsx"""
    global header_format

    wb = xlsxwriter.Workbook(fname)
    page = wb.add_worksheet()
    header_format = wb.add_format(
        {
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "border": 2,
        }
    )
    regular_format = deepcopy(header_format)
    regular_format.bold = False
    regular_format.border = 1

    header_begin_col = ord('A') # 65
    
    for header in data.keys():
        title_end_col = header_begin_col + len(data[header].keys())
        
        # headers are on the same row, but different columns
        page.merge_range(f"{chr(header_begin_col)}1:{chr(title_end_col)}1", header, header_format)
        
        # visual separation of the compared tables
        header_begin_col = title_end_col + 1
        bom = data.pop(header)
        
        # subheaders & their data
        next_header_col = 0
        head_row = 2

        for bom_header, bom_data in bom.items():
            head_col = chr(header_begin_col + next_header_col)
            page.write(f"{head_col}{head_row}", bom_header, header_format)
            next_header_col += 1

            # first column is index, can support row merging
            data_row = 3
            # tech name as index key
            from pdb import set_trace
            set_trace()

            # map of indexed duplicates to be skipped 
            # during iteration of bom_data object
            found_duplicate = {}

            for ndx, pkg in enumerate(bom_data):
                    
                if pkg in found_duplicate:
                    continue

                pkg_count = bom_data.count(pkg)
                
                if pkg_count == 1:
                    page.write(f"{head_col}{data_row}", pkg, regular_format)
                    data_row += 1

                else:
                    found_duplicate[pkg] = pkg_count    
                    # add all other fields that do not require row merging
                    for row in range(data_row, data_row + pkg_count):
                        for col in range(ord(head_col), ord(head_col + len(bom_data))):
                            page.write(f"{col}{row}", pkg, regular_format)
                    # merge index field rows
                    page.merge_range(f"{head_col}{data_row}:{head_col}{data_row + pkg_count}", pkg, regular_format)
                    data_row += pkg_count + 1
    page.autofit()
    wb.close()


if __name__ == "__main__":

    option = argue()
    csf = option.csv
    bom = option.bom

    with open(bom, encoding="utf-8") as sbom:
        jbom = json.load(sbom)

    # build cobalt tech group
    df = pd.read_csv(csf)
    cobba = df["BA"].to_list()
    coblt = df["LT"].to_list()
    cobpkg = df["Name Of Software Package"].to_list()
    cobver = df["Version"].to_list()
    cobalt_mapping = group_tech(cobba, coblt, cobpkg, cobver)

    # build PLS tech group
    bomba = []
    bomlt = []
    bomver = []
    bompkg = []

    for prop in jbom["components"]:
        description = prop["description"].split()
        bomba.append(description[-1])
        bomlt.append(description[-3].rstrip(","))
        bomver.append(prop["version"])
        bompkg.append(prop["name"])

    jbom_mapping = group_tech(bomba, bomlt, bompkg, bomver)
    # end build PLS tech group

    # RUN DIFF
    cobalt_set = set(cobalt_mapping.keys())
    jbom_set = set(jbom_mapping.keys())

    diff_cobalt_not_in_jbom = cobalt_set - jbom_set
    diff_jbom_not_in_cobalt = jbom_set - cobalt_set
    
    diff_common_version = jbom_set.intersection(cobalt_set)

    # <<<<<<<<<<<<< BEGIN output export
    system("mkdir output")

    # tech in cobalt, but not in pls
    report = generate_df_dict(
        cobalt_mapping,
        diff_cobalt_not_in_jbom,
    )
    report = {"Cobalt": report}
    
    xport(report, "output/Cobalt_not_in_PLS.xlsx")

    # tech in pls, but not in cobalt
    report = generate_df_dict(jbom_mapping, diff_jbom_not_in_cobalt)
    report = {"PLS": report}

    xport(report, "output/PLS_not_in_Cobalt.xlsx")

    # common tech in pls & cobalt, with dedicated version
    report_cobalt = generate_df_dict(cobalt_mapping, diff_common_version)
    report_jbom = generate_df_dict(jbom_mapping, diff_common_version)
    merged = {"Cobalt": report_cobalt, "PLS": report_jbom}
    
    xport(report, "output/common_version.xlsx")
