from modules.loader import SpreadsheetLoader
import argparse

def main(arguments: argparse.Namespace):
    loader = SpreadsheetLoader(arguments.spreadsheet)
    sheet = loader.load()

    error_list = []
    registered_values = {}
    print(registered_values)
    for taxon_set in sheet.taxon_sets:
        if '' or None in taxon_set:
            error_list = report_error(error_list, sheet, 1)
        elif [taxon_set[1], taxon_set[2]] in registered_values.values():
            pass
        else:
            pass


def report_error(error_list, taxon_set, error_code):
    if error_code == 1:
        for location, section in enumerate(taxon_set):
            if location == 1:
                error_list.append(f'error_single_common_name_found_at_{taxon_set[0]}')
            else:
                error_list.append(f'error_single_taxon_id_found_at_{taxon_set[0]}')
        if error_code == 2:
            error_list.append(f'error_NCBI_cant_find_{taxon_set[1]}_official_name_for_{taxon_set[2]}_is_{taxon_set[3]}')
        if error_code == 3:
            error_list.append(f'error_{taxon_set[1]}_doesnt_match_{taxon_set[2]}_the_official_name_for_{taxon_set[2]}_is_{taxon_set[3]}')
        return error_list
