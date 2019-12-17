# Proposal for structure of script (steps 1-3 are part of a loop for the spreadsheet):
#
# Initial Values: spreadsheet = input, error_list = [ ], registered_values_dict = { }
#
# 1    - Read the manifest spreadsheet from row 10 (start of data values) and take the taxon_id(col Y) and
#      - common_name(col Z), ignoring double blanks (use external-import code)
# 1.1  - If one of the target columns is blank and the other is filled add a line to the error_list
#      - [error_single_<[common_name | taxon_id]>_found_at_<line>], then move to the next spreadsheet line
#
# 2    - Check the taxon_id and common_name against the registered_values_dict, formatted {common_name : taxon_id},
#      - if it matches then move to the next spreadsheet line
#
# 3    - If there is no match in the registered_values_dict then query NCBI with common_name
#      - (using an adapted version of James' code)
# 3.1  - If the common_name doesn't match then do 3a, append the error line to the error_list
#      - [error_NCBI_cant_find_<common_name>_official_name_for_<taxon_id>_is_<NCBI_common_name>] and do 3.4
# 3.2  - If the common_name does match but NCBI_taxon_id is not equal to taxon_id then do 3a, append the error line
#      - to the error_list
#      - [error_<common_name>_doesnt_match_<taxon_id>_the_official_name_for_<taxon_id>_is_<NCBI_common_name>] and do 3.4
# 3.3  - If the common_name and taxon_id pair up correctly then do 3.4
# 3.4  - Add {common_name : taxon_id} to the registered_values_dict = { }
#
# 3a   - Query NCBI using taxon_id and return the NCBI_common_name
#
# 4    - Once spreadsheet run-through has been completed, sort the error_list to remove any identical lines
# 4.1  - Print the errors in error_list and save them to a validation_components
#
# Notes: Starting line is 10, cols Y('TAXON ID', value=22) and Z('COMMON NAME', value=23) assuming A=0, external-import
#        has a spreadsheet reading section, ncbi reading tools can be taken and adapted from James Torrance's validation_components
