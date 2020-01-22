from validation_components.spreadsheet_parsing import SpreadsheetLoader, ManifestEntry, NcbiQuery
import argparse

def validation_runner(arguments: argparse.Namespace):
    '''Runs the checks for taxonomy and common_name errors in a given manifest'''
    loader = SpreadsheetLoader(arguments.spreadsheet)
    all_entries = loader.load()

    error_list = verify_entries(all_entries)

    if len(error_list) > 0:
        print('Errors found within manifest:\n\t' + '\n\t'.join(error_list) + '\nPlease correct mistakes and validate again.')
    else:
        print('Manifest successfully validated, no errors found!')


def verify_entries(all_entries):
    error_list = []
    registered_values = {'__null____null__': [1, None, None]}
    timestamp = None
    for manifest_entry in all_entries:
        if manifest_entry.query_id in registered_values.keys():
            print(manifest_entry.common_name, manifest_entry.taxon_id)
            error_code = registered_values[manifest_entry.query_id][0]
            common_name_statement = registered_values[manifest_entry.query_id][1]
            taxon_id_statement = registered_values[manifest_entry.query_id][2]
            if error_code != 0:
                error_list.append(manifest_entry.report_error(error_code, common_name_statement, taxon_id_statement))

        else:
            connecter = NcbiQuery()

            if manifest_entry.common_name != '__nul__':
                timestamp = connecter.generate_new_timestamp(timestamp)
                ncbi_taxon_id = connecter.query_ncbi_for_taxon_id(manifest_entry)
            else:
                ncbi_taxon_id = None

            if manifest_entry.taxon_id == ncbi_taxon_id:
                error_code = 0
                common_name_statement = None
                taxon_id_statement = None
            else:
                if manifest_entry.taxon_id != '__nul__':
                    timestamp = connecter.generate_new_timestamp(timestamp)
                    ncbi_common_name = connecter.query_ncbi_for_common_name(manifest_entry)
                else:
                    ncbi_common_name = None

                if ncbi_common_name != None and ncbi_common_name != '__null__' and ncbi_taxon_id != None and ncbi_taxon_id != '__null__':
                    error_code = 2
                else:
                    error_code = 3

                common_name_statement = manifest_entry.common_name_definition(ncbi_taxon_id)
                taxon_id_statement = manifest_entry.taxon_id_definition(ncbi_common_name)

            if error_code != 0:
                error_list.append(manifest_entry.report_error(error_code, common_name_statement, taxon_id_statement))
            registered_values[manifest_entry.query_id] = (error_code, common_name_statement, taxon_id_statement)
    return error_list
