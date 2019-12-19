from validation_components.spreadsheet_parsing import SpreadsheetLoader, ManifestEntry, NcbiQuery
import argparse

def validation_runner(arguments: argparse.Namespace):
    '''Runs the checks for taxonomy and common_name errors in a given manifest'''
    loader = SpreadsheetLoader(arguments.spreadsheet)
    all_entries = loader.load()

    error_list = []
    registered_values = set()
    for manifest_entry in all_entries:
        if not manifest_entry.common_name or not manifest_entry.taxon_id:
            manifest_entry.error_code = 1
            error_list.append(manifest_entry.report_error())
        elif manifest_entry.query_id in registered_values:
            pass
        else:
            manifest_entry = NcbiQuery.query_ncbi(manifest_entry)
            if manifest_entry.error_code:
                error_list.append(manifest_entry.report_error())
            registered_values.add(manifest_entry.query_id)
    if len(error_list) > 0:
        raise Exception('Errors found within manifest:\n\t' + '\n\t'.join(error_list) + '\nPlease correct mistakes and validate again.')
    else:
        print('Manifest successfully validated, no errors found! :D')
