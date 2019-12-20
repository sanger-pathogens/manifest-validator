from validation_components.spreadsheet_parsing import SpreadsheetLoader, ManifestEntry, NcbiQuery
import argparse

def validation_runner(arguments: argparse.Namespace):
    '''Runs the checks for taxonomy and common_name errors in a given manifest'''
    loader = SpreadsheetLoader(arguments.spreadsheet)
    all_entries = loader.load()

    error_list = []
    registered_values = set()
    timestamp = None
    for manifest_entry in all_entries:
        if not manifest_entry.common_name or not manifest_entry.taxon_id:
            error_code = 1
            error_list.append(manifest_entry.report_error(error_code))
        elif manifest_entry.query_id in registered_values:
            pass
        else:
            connecter = NcbiQuery()
            timestamp = connecter.generate_new_timestamp(timestamp)
            error_code, ncbi_common_name = connecter.query_ncbi(manifest_entry)
            if error_code:
                error_list.append(manifest_entry.report_error(error_code, ncbi_common_name))
            registered_values.add(manifest_entry.query_id)
    if len(error_list) > 0:
        print('Errors found within manifest:\n\t' + '\n\t'.join(error_list) + '\nPlease correct mistakes and validate again.')
    else:
        print('Manifest successfully validated, no errors found! :D')
