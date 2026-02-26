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
    ba_list = []
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
    wb = xlsxwriter.Workbook(fname)
    page = wb.add_worksheet()

    ### Cell formatting
    header_format = wb.add_format(
        {
            "bold": True,
            "num_format": "0",
            "align": "center",
            "valign": "vcenter",
            "border": 1,
        }
    )
    num_format = deepcopy(header_format)
    num_format.pop("bold")

    row_index = 1

    for header in data.keys():
        bom = data[header]

    # page.write(0, 0, "Order", header_format)
    # page.merge_range("B1:C1", "Item", header_format)

    # for row_data in data_list:
    #     for col_index, (cell_key, cell_value) in enumerate(row_data.items()):
    #         if len(cell_value) >= 2:
    #             page.merge_range(
    #                 row_index,
    #                 col_index,
    #                 (row_index + len(cell_value)) - 1,
    #                 col_index,
    #                 int(cell_key),
    #                 header_format,
    #             )
    #         else:
    #             page.write(row_index, col_index, int(cell_key), header_format)
    #         for item_key, item_value in cell_value.items():
    #             page.write(row_index, col_index + 1, item_key, cell_format_str)
    #             page.write(row_index, col_index + 2, int(item_value), cell_format_num)
    #             row_index += 1

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
    xport(report, "PLS_not_in_Cobalt.xlsx")

    # common tech in pls & cobalt, with dedicated version
    report_cobalt = generate_df_dict(cobalt_mapping, diff_common_version)
    report_jbom = generate_df_dict(jbom_mapping, diff_common_version)
    merged = {"Cobalt": report_cobalt, "PLS": report_jbom}
    xport(report, "output/common_version.xlsx")

    # both
    # {'libjpeg-turbo', 'onnxruntime', 'zstd', 'Intel Math Kernel Library', 'Nghttp2 Library', 'Expat', 'xgboost', 'OpenSSL', 'Kerberos', 'Geneva Forecasting', 'Zlib Data Compression Library', 'CRoaring', 'Snappy-C', 'XML::Simple', 'GDAL - Geospatial Data Abstraction Library', 'libfuse', 'DataDirect Technology', 'unixODBC', 'LZ4', 'rdma-core', 'Python', 'librdkafka', 'perl-JSON', 'Intel Integrated Performance Primitives Redistributables', 'LAPACK', 'LZO Compression Technology. (Agreement, Preamble - Pg. 1) (Refer to Other Info Field below)', 'Perl', 'Intel C++ Compiler XE Redistributables', 'IO::String', 'Sys::SigAction', 'Korean Lexer'}

    # cobalt_mapping = {'Python': {'3.13.11': '231335 362597'}, 'OpenSSL': {'openssl-3.5.4': '224311 348731'}, 'Expat': {'2.7.2': '223347 346780'}, 'LAPACK': {'3.12.1': '220516 340549'}, 'GDAL - Geospatial Data Abstraction Library': {'3.10.3': '214155 328698'}, 'Perl': {'5.38.4': '213140 329391'}, 'libjpeg-turbo': {'3.0.3': '114970 180343'}, 'onnxruntime': {'1.20.1': '121441 191899'}, 'xgboost': {'2.0.3': '102606 158681'}, 'Intel Integrated Performance Primitives Redistributables': {'2021.12': '114426 178839'}, 'DataDirect Technology': {'None specified': '8 2242'}, 'Intel Math Kernel Library': {'None specified': '5855 5895'}, 'Intel C++ Compiler XE Redistributables': {'(Agreement covers all versions made available to Oracle during the term (Dec 1, 2014 to present))': '33804 38099'}, 'LZO Compression Technology. (Agreement, Preamble - Pg. 1) (Refer to Other Info Field below)': {'5.0': '48121 56690'}, 'perl-JSON': {'4.10': '87586 138723'}, 'unixODBC': {'2.3.11': '85889 129499', '2.3.12': '108417 169118'}, 'XML::Simple': {'2.25': '49137 58596'}, 'Sys::SigAction': {'0.21': '48232 56878'}, 'IO::String': {'1.08': '17417 56875'}, 'librdkafka': {'2.10.1': '216378 332423'}, 'Nghttp2 Library': {'1.62.1': '109056 173964'}, 'LZ4': {'1.10.0': '110613 175536'}, 'zstd': {'1.5.6': '111963 175542'}, 'Kerberos': {'1.21.3': '109030 170509'}, 'Geneva Forecasting': {'1': '10 2244'}, 'Snappy-C': {'570fc61': '40553 65368'}, 'Korean Lexer': {'1': '26 2260'}, 'Zlib Data Compression Library': {'1.3.1': '102280 162199'}, 'CRoaring': {'1.3.0': '98077 151212'}, 'libfuse': {'2.9.7-16.0.1.el8.x86_64': '90338 138631'}, 'rdma-core': {'rdma-core 34.0-1.0.5': '84401 127113'}}

    # jbom_mapping = {'DataDirect Technology': {'None specified': '8 2242'}, 'Geneva Forecasting': {'1.0': '10 2244'}, 'Korean Lexer': {'1.0': '26 2260'}, 'Projections Code': {'1.0': '32 2264'}, 'Intel Math Kernel Library': {'None specified': '5855 5895'}, 'Apple MDNS (Bonjour)': {'544-1': '51233 22697'}, 'Intel C++ Compiler XE Redistributables': {'(Agreement covers all versions made available to Oracle during the term (Dec 1, 2014 to present))': '33804 38099'}, 'BSON format': {'1.1': '47485 55643'}, 'LZO Compression Technology. (Agreement, Preamble - Pg. 1) (Refer to Other Info Field below)': {'5.0': '48121 56690'}, 'IO::String': {'1.08': '17417 56875'}, 'Sys::SigAction': {'0.21': '48232 56878'}, 'XML::Simple': {'2.25': '49137 58596'}, 'perl-TermReadKey': {'2.38': '49923 60635'}, 'Snappy-C': {'570fc61': '40553 65368'}, 'XMLBeans': {'2.6.0-6': '52605 68205'}, 'bzip2': {'1.0.8': '53267 69186'}, 'DOM': {'Dom Level 3 core specification, Version 1.0': '282 70125'}, 'org.antlr/antlr': {'3.5.2': '26162 70984'}, 'XML::Parser': {'2.46': '57804 82440'}, 'Xerces xercesImpl': {'2.12.2': '216826 129262'}, 'perl-JSON': {'4.10': '87586 138723'}, 'Derby': {'10.15.2.1': '102680 159015'}, 'Jakarta Activation API (JAF)': {'2.1.3': '103358 161441'}, 'Commons Compress': {'1.26.1': '103764 161758'}, 'Zlib Data Compression Library': {'1.3.1': '102280 162199'}, 'libfuse': {'2.9.7-17.0.1': '105027 163614'}, 'OpenAI OpenAPI Spec': {'2.0.0': '105730 164766'}, 'Google Gemini REST API Spec': {'bc11274': '105741 164790'}, 'Vertex AI Gemini API Spec': {'1756ac8': '105758 164819'}, 'Hugging Face API Spec': {'2.0': '105765 164833'}, 'Cohere API Spec': {'7.9.5': '105766 164834'}, 'Ollama API Spec': {'0.1.40': '107446 168028'}, 'Kerberos': {'1.21.3': '109030 170509'}, 'Nghttp2 Library': {'1.62.1': '109056 173964'}, 'DBD-Oracle': {'1.90': '109688 174011'}, 'Javassist': {'3.30.2-GA': '101813 174100'}, 'LZ4': {'1.10.0': '110613 175536'}, 'zstd': {'1.5.6': '111963 175542'}, 'Commons CLI': {'1.9.0': '114248 178621'}, 'Intel Integrated Performance Primitives Redistributables': {'2021.12': '114426 178839'}, 'DBI': {'1.644': '114481 178975'}, 'libjpeg-turbo': {'3.0.3': '114970 180343'}, 'Jakarta Json Processing API (JSON-P)': {'2.1.3': '100668 180891'}, 'Encoding Standard': {'68f9e52': '115934 182112'}, 'Jakarta Restful Web Services JAX-RS API': {'4.0.0': '105975 182971'}, 'Jakarta Servlet': {'4.0.4': '70732 186573'}, 'Entity Framework Core Source Code': {'9.0.0': '121149 191439', '10.0.0': '231565 363718'}, 'onnxruntime': {'1.20.1': '121441 191899'}, 'Jackson Annotations': {'2.18.2': '119312 192959'}, 'Jackson Core': {'2.18.2': '119971 192963'}, 'Jackson Databind': {'2.18.2': '119316 192964'}, 'jackson-datatype-jsr310': {'2.18.2': '121271 192969'}, 'jackson-jaxrs-json-provider': {'2.18.2': '119503 192972'}, 'FastInfoset': {'1.2.13': '122102 195386'}, 'HTML Standard': {'0b5dd5e': '123219 195505'}, 'File API': {'77b2086': '123224 195517'}, 'High Resolution Time': {'060b3c9': '123225 195518'}, 'URL Standard': {'7f3e3b6': '122814 195522'}, 'Streams Standard': {'#2811932': '122815 195524'}, 'Compression Standard': {'ec763b0': '123187 195611'}, 'Web IDL Standard': {'90b5184': '123188 195613'}, 'DOM Standard': {'e6bb175': '123190 195616'}, 'OpenSSL': {'3.0.16': '208197 197166', '3.5.4': '224311 348731'}, 'Jakarta Persistence API (JPA API)': {'3.1.0': '79920 200858'}, 'EclipseLink JPA': {'4.0.5': '122966 321143'}, 'slf4j-api (9938 duplicate of 31983)': {'2.0.16': '111590 321154'}, 'slf4j-jdk14': {'2.0.16': '111821 321155'}, 'Jakarta Bean Validation API': {'3.1.0': '107894 322470'}, 'Jakarta Annotations API': {'3.0.0': '105287 323352'}, 'onnxruntime-extensions core': {'0.13.0': '212414 324998'}, 'GDAL - Geospatial Data Abstraction Library': {'3.10.3': '214155 328698'}, 'Perl': {'5.38.4': '213140 329391'}, 'JavaScript Extension Toolkit (JET)': {'18.0.6': '214146 330748'}, 'BSAFE Software (Crypto J)': {'6.3.1': '215554 330897', '7.0.1': '222635 344116'}, 'Mina SSHD-cli': {'2.15.0': '215617 331110'}, 'Mina SSHD-mina': {'2.15.0': '214055 331113'}, 'Mina SSHD-sftp': {'2.15.0': '211469 331114'}, 'Mina SSHD-core': {'2.15.0': '211468 331115'}, 'Mina SSHD-common': {'2.15.0': '211467 331116'}, 'rdma-core': {'53.0-1.0.3': '211263 331290'}, 'librdkafka': {'2.10.1': '216378 332423'}, 'jackson-module-jsonSchema': {'2.18.2': '217622 335476'}, 'Visual C++ Redistributable': {'14.44.35208.0': '217699 335601'}, 'Lombok': {'1.18.38': '212801 335822'}, 'jackson-module-jaxb-annotations': {'2.18.2': '120639 335832'}, 'CRoaring': {'v4.3.5': '218471 337202'}, 'Commons Lang': {'3.18.0': '217786 339094'}, 'LAPACK': {'3.12.1': '220516 340549'}, 'LLVM': {'21.1.0': '220940 342002'}, 'LangChain Core': {'0.3.74': '222569 343947'}, 'Expat': {'2.7.2': '223347 346780'}, 'faiss': {'1.11.0': '224011 348175'}, 'unixODBC': {'2.3.14': '224816 350292'}, 'PCRE2': {'10.46': '226465 352301'}, 'xgboost': {'3.0.5': '223994 353859'}, 'Storage Performance Development Kit': {'25.05.1': '227430 354018'}, 'jersey-common': {'3.1.11': '220877 357584'}, 'jersey-server': {'3.1.11': '220842 357588'}, 'jersey-client': {'3.1.11': '220872 357589'}, 'jersey-container-servlet-core': {'3.1.11': '220879 357591'}, 'jersey-container-servlet': {'3.1.11': '224831 357593'}, 'jersey-hk2': {'3.1.11': '220881 357594'}, 'Eclipse jersey-media-jaxb': {'3.1.11': '228741 357596'}, 'jersey-entity-filtering': {'3.1.11': '225558 357601'}, 'jersey-media-json-jackson': {'3.1.11': '220883 357602'}, 'Fetch API Standard': {'60e9ff5': '228878 358189'}, 'jersey-apache-connector': {'3.1.11': '220874 358782'}, 'micronaut-http-server-netty': {'3.8.5.11': '230747 361466'}, 'micronaut-management': {'3.8.5.11': '230748 361468'}, 'micronaut-runtime': {'3.8.5.11': '230750 361470'}, 'Python': {'3.13.11': '231335 362597'}, 'OpenJPEG': {'2.5.4': '223337 363703'}}
