from modules.spreadsheet_parsing import SpreadsheetLoader
import argparse

def main(arguments: argparse.Namespace):
    loader = SpreadsheetLoader(arguments.spreadsheet)
    query_stack = loader.load()

    error_list = []
    registered_values = {}
    print(registered_values)
    for query in query_stack:
        if '' or None in query_stack:
            error_list = report_error(error_list, query, 1)
        elif [query.common_name, query.taxon_id] in registered_values.values():
            pass
        else:
            pass


def report_error(error_list, query, error_code):
    if error_code == 1:
        if query.common_name == None:
            error_list.append(f'Error: single common name found at {query.row}')
        else:
            error_list.append(f'Error: single taxon id found at {query.row}')
        if error_code == 2:
            error_list.append(f'Error: NCBI cant find {query.common_name} official name for {query.taxon_id} is {query.ncbi_common_name}')
        if error_code == 3:
            error_list.append(f'Error: {query.common_name} doesnt match {query.taxon_id} the official name for {query.taxon_id} is {query.ncbi_common_name}')
        return error_list
