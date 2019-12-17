from validation_components.spreadsheet_parsing import SpreadsheetLoader
import argparse

def validation_runner(arguments: argparse.Namespace):
    '''Runs the checks for taxonomy and common_name errors in a given manifest'''
    loader = SpreadsheetLoader(arguments.spreadsheet)
    all_entries = loader.load()

    error_list = []
    registered_values = {}
    for manifest_entry in all_entries:
        if manifest_entry.common_name == None or manifest_entry.taxon_id == None:
            error_list.append(report_error(manifest_entry, 1))
        elif [manifest_entry.common_name, manifest_entry.taxon_id] in registered_values.values():
            pass
        else:
            pass


def report_error(query, error_code):
    if error_code == 1:
        if query.common_name == None:
            error = f'Error: single common name found at {query.sample_id}'
        else:
            error = f'Error: single taxon id found at {query.sample_id}'
        if error_code == 2:
            error = f'Error: NCBI cant find {query.common_name} official name for {query.taxon_id} is {query.ncbi_common_name}'
        if error_code == 3:
            error = f'Error: {query.common_name} doesnt match {query.taxon_id} the official name for {query.taxon_id} is {query.ncbi_common_name}'
        return error
