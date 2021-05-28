from validation_components.manifest_querying import SpreadsheetLoader, ManifestEntry, NcbiQuery
import argparse

def validation_runner(arguments: argparse.Namespace):
    '''Runs the checks for taxonomy and common_name errors in a given manifest'''
    loader = SpreadsheetLoader(arguments.spreadsheet)
    if loader._format == 'xls':
        all_entries = loader.load()
    else:
        all_entries = loader.load_xlsx()

    error_list = verify_entries(all_entries)

    if len(error_list) > 0:
        print('Errors found within manifest:\n\t' + '\n\t'.join(error_list) + '\nPlease correct mistakes and validate again.')
    else:
        print('Manifest successfully validated, no errors found!')


def verify_entries(all_entries):
    error_list = []
    registered_values = {'__null____null__': ": No taxon ID or common name specified. If unkown please use 32644 - 'unidentified'."}
    connecter = NcbiQuery()
    for manifest_entry in all_entries:
        if manifest_entry.query_id in registered_values.keys():
            error_term = registered_values[manifest_entry.query_id]
            if error_term is not None:
                error_list.append((manifest_entry.sample_id + error_term))
        else:
            ncbi_common_name, ncbi_rank = resolve_taxon_id(connecter, manifest_entry)

            if ncbi_rank not in ['genus', 'species', 'subspecies', 'strain', '', None]:
                error_list.append((manifest_entry.sample_id + f": Given taxon ID corresponds to the rank '{ncbi_rank}'"
                                                              f" - please use a taxon no higher than  genus/species, "
                                                              f" or the ID 32644 with "
                                                              f"'unidentified' if a more accurate rank is not known."))

            if manifest_entry.common_name == ncbi_common_name:
                error_term = None
            else:
                ncbi_taxon_id = resolve_common_name(connecter, manifest_entry)
                error_code = resolve_error(ncbi_common_name, ncbi_taxon_id, manifest_entry)
                error_term = define_error(error_code, manifest_entry, ncbi_taxon_id, ncbi_common_name)
                error_list.append((manifest_entry.sample_id+error_term))
            registered_values[manifest_entry.query_id] = error_term
    return error_list


def define_error(error_code, manifest_entry, ncbi_taxon_id, ncbi_common_name):
    common_name_statement = manifest_entry.common_name_definition(ncbi_taxon_id)
    taxon_id_statement = manifest_entry.taxon_id_definition(ncbi_common_name)

    error_term = manifest_entry.report_error(error_code, common_name_statement, taxon_id_statement)
    return error_term


def resolve_error(ncbi_common_name, ncbi_taxon_id, manifest_entry):
    if manifest_entry.taxon_id == ncbi_taxon_id:
        error_code = 2
    elif ncbi_common_name != '__null__' and ncbi_taxon_id != '__null__':
        error_code = 1
    else:
        error_code = 3
    return error_code


def resolve_taxon_id(connecter, manifest_entry):
    if manifest_entry.taxon_id != '__null__':
        ncbi_common_name, ncbi_rank = connecter.query_ncbi_for_common_name(manifest_entry)
    else:
        ncbi_common_name = "__null__"
        ncbi_rank = None
    return ncbi_common_name, ncbi_rank


def resolve_common_name(connecter, manifest_entry):
    if manifest_entry.common_name != '__null__':
        ncbi_taxon_id = connecter.query_ncbi_for_taxon_id(manifest_entry)
    else:
        ncbi_taxon_id = '__null__'
    return ncbi_taxon_id
