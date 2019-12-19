from validation_components.spreadsheet_parsing import SpreadsheetLoader, ManifestEntry
import argparse

def validation_runner(arguments: argparse.Namespace):
    '''Runs the checks for taxonomy and common_name errors in a given manifest'''
    loader = SpreadsheetLoader(arguments.spreadsheet)
    all_entries = loader.load()

    error_list = []
    registered_values = set()
    for manifest_entry in all_entries:
        if not manifest_entry.common_name or not manifest_entry.taxon_id:
            error_list.append(report_error(manifest_entry, 1))
        elif manifest_entry.query_id in registered_values:
            pass
        else:
            error = manifest_entry.query_ncbi(manifest_entry)
            if error:
                error_list.append(report_error(manifest_entry, error))
            registered_values.add(manifest_entry.query_id)
    if len(error_list) > 0:
        raise Exception('Errors found within manifest:\n\t' + '\n\t'.join(error_list) + '\nPlease correct mistakes and validate again.')
    else:
        print('Manifest successfully validated, no errors found! :D')

def report_error(query, error_code):
    if error_code == 1:
        if not query.common_name:
            error = f'Error: single common name found at {query.sample_id}'
        else:
            error = f'Error: single taxon id found at {query.sample_id}'
        if error_code == 2:
            error = f'Error: NCBI cant find {query.common_name} official name for {query.taxon_id} is {query.ncbi_common_name}'
        if error_code == 3:
            error = f'Error: {query.common_name} doesnt match {query.taxon_id} the official name for {query.taxon_id} is {query.ncbi_common_name}'
        return error
