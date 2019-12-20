import xlrd
import requests

class ManifestEntry:
    '''A class construct for a single entry from the manifest submitted and query the entries when necessary'''
    def __init__(self, sample_id: str, common_name: str, taxon_id: int):
        self.sample_id = sample_id
        self.common_name = common_name
        self.taxon_id = str(taxon_id)
        self.ncbi_common_name = ''
        self.query_id = common_name + str(taxon_id)
        self.error_code = None

    def report_error(self):
        if self.error_code == 1:
            if self.common_name:
                error = f'Error: single common name found at {self.sample_id}'
            else:
                error = f'Error: single taxon id found at {self.sample_id}'
        elif self.error_code == 2:
            error = f'Error: NCBI cant find {self.common_name}, the official name for {self.taxon_id} is {self.ncbi_common_name}'
        elif self.error_code == 3:
            error = f'Error: {self.common_name} doesnt match {self.taxon_id} the official name for {self.taxon_id} is {self.ncbi_common_name}'
        else:
            error = None
        return error


class NcbiQuery:

    @staticmethod
    def query_ncbi(manifest_entry: object):
        url = NcbiQuery.build_url(manifest_entry, esearch=True)
        tax_id_json = NcbiQuery.ncbi_search(url)
        if 'esearchresult' in tax_id_json and 'idlist' in tax_id_json['esearchresult'] and len(
                tax_id_json['esearchresult']['idlist']) == 1:
            if tax_id_json['esearchresult']['idlist'][0] == manifest_entry.taxon_id:
                manifest_entry.error_code = None
                return manifest_entry
            else:
                manifest_entry.error_code = 3
        else:
            manifest_entry.error_code = 2

        url = NcbiQuery.build_url(manifest_entry, esearch=False)
        common_name_json = NcbiQuery.ncbi_search(url)
        if 'result' in common_name_json and manifest_entry.taxon_id in common_name_json['result'] and 'scientificname' in \
                common_name_json['result'][manifest_entry.taxon_id]:
            manifest_entry.ncbi_common_name = tax_id_json['result'][manifest_entry.taxon_id]['scientificname']
        else:
            manifest_entry.ncbi_common_name = 'unkown as the taxon ID is invalid'
        return manifest_entry

    @staticmethod
    def build_url(manifest_entry, esearch: bool):
        mid_url = '.fcgi?db=taxonomy&'
        base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
        end_url = '&retmode=json'
        if esearch:
            url = base_url + 'esearch' + mid_url + 'field=All%20Names&term=' + manifest_entry.common_name + end_url
        else:
            url = base_url + 'esummary' + mid_url + 'id=' + manifest_entry.taxon_id + end_url
        return url

    @staticmethod
    def ncbi_search(url):
        search_session = requests.Session()
        data = search_session.get(url)
        return data.json()


class SpreadsheetLoader:

    def __init__(self, file):
        self._file = file
        self._workbook = xlrd.open_workbook(self._file)
        self._sheet = self._workbook.sheet_by_index(0)

    def load(self):
        entries = []
        data_row = 0
        header_row = 0
        for row in range(self._sheet.nrows):
            if self._sheet.cell_value(row, 0) == 'SANGER PLATE ID':
                data_row = row + 1
                header_row = row
                break

        for column in range(self._sheet.ncols):
            header_cell = self._sheet.cell_value(header_row, column)
            if header_cell == 'SUPPLIER SAMPLE NAME':
                sample_id_column = column
            elif header_cell == 'TAXON ID':
                taxon_id_column = column
            elif header_cell == 'COMMON NAME':
                common_name_column = column


        for row in range(data_row, self._sheet.nrows):
            common_name = self.__extract_cell_value(row, common_name_column)
            taxon_id = self.__extract_cell_value(row, taxon_id_column)
            sample_id = self.__extract_cell_value(row, sample_id_column)
            if common_name is not None and taxon_id is not None and sample_id_column is not None:
                entry = ManifestEntry(sample_id, common_name, taxon_id)
                entries.append(entry)
        return entries


    def __extract_cell_value(self, row, column):
        if self._sheet.cell_type(row, column) != xlrd.XL_CELL_NUMBER:
            new_data = self._sheet.cell_value(row, column).strip()
            return None if new_data == '' else new_data
        return int(self._sheet.cell_value(row, column))
