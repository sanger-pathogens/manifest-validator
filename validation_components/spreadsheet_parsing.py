import xlrd
import requests
from datetime import datetime
import time

class ManifestEntry:
    '''A class construct for a single entry from the manifest submitted and query the entries when necessary'''
    def __init__(self, sample_id: str, common_name, taxon_id):
        self.sample_id = sample_id
        self.common_name = common_name
        self.taxon_id = taxon_id
        if common_name and taxon_id:
            self.query_id = common_name + str(taxon_id)
        else:
            self.query_id = 'invalid'

    def report_error(self, error_code, ncbi_common_name=None):
        if error_code == 1:
            if self.common_name:
                error = (f'Error: Single common name found at {self.sample_id}')
            elif self.taxon_id:
                error = (f'Error: Single taxon id found at {self.sample_id}')
            else:
                error = (f'Error: No taxonomy data found at {self.sample_id}')
        elif error_code == 2:
            error = (f'Error: NCBI cant find {self.common_name}, the official name for {self.taxon_id} is {ncbi_common_name}')
        elif error_code == 3:
            error = (f'Error: {self.common_name} doesnt match {self.taxon_id} the official name for {self.taxon_id} is {ncbi_common_name}')
        else:
            error = None
        return error


class NcbiQuery:

    @staticmethod
    def get_now():
        return datetime.now()

    @staticmethod
    def generate_new_timestamp(previous_timestamp):
        if previous_timestamp != None:
            time_since_last_query = NcbiQuery.get_now() - previous_timestamp

            required_microsecond_delay = 335000
            if time_since_last_query.days == 0 and time_since_last_query.seconds == 0 and time_since_last_query.microseconds < required_microsecond_delay:
                time.sleep((required_microsecond_delay - time_since_last_query.microseconds) / 1000000)

        new_timestamp = NcbiQuery.get_now()
        return new_timestamp


    def query_ncbi(self, manifest_entry: object):
        url = self.build_url(manifest_entry, esearch=True)
        tax_id_json = self.ncbi_search(url)
        if 'esearchresult' in tax_id_json and 'idlist' in tax_id_json['esearchresult'] and len(
                tax_id_json['esearchresult']['idlist']) == 1:
            if tax_id_json['esearchresult']['idlist'][0] == manifest_entry.taxon_id:
                error_code = None
                ncbi_common_name = None
                return error_code, ncbi_common_name
            else:
                error_code = 3
        else:
            error_code = 2

        url = self.build_url(manifest_entry, esearch=False)
        common_name_json = self.ncbi_search(url)
        if 'result' in common_name_json and manifest_entry.taxon_id in common_name_json['result'] and 'scientificname' in \
                common_name_json['result'][manifest_entry.taxon_id]:
            ncbi_common_name = common_name_json['result'][manifest_entry.taxon_id]['scientificname']
        else:
            ncbi_common_name = 'unkown as the taxon ID is invalid'
        return error_code, ncbi_common_name

    def build_url(self, manifest_entry, esearch: bool):
        mid_url = '.fcgi?db=taxonomy&'
        base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
        end_url = '&retmode=json'
        if esearch:
            url = base_url + 'esearch' + mid_url + 'field=All%20Names&term=' + manifest_entry.common_name + end_url
        else:
            url = base_url + 'esummary' + mid_url + 'id=' + manifest_entry.taxon_id + end_url
        return url


    def ncbi_search(self, url):
        search_session = requests.Session()
        data = search_session.get(url)
        if not data:
            raise ConnectionError('Could not connect to NCBI database - Aborting')
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
            if sample_id is not None:
                entry = ManifestEntry(sample_id, common_name, taxon_id)
                entries.append(entry)
        return entries


    def __extract_cell_value(self, row, column):
        if self._sheet.cell_type(row, column) != xlrd.XL_CELL_NUMBER:
            new_data = self._sheet.cell_value(row, column).strip()
            return None if new_data == '' else new_data
        new_data = str(int(self._sheet.cell_value(row, column)))
        return None if new_data == '' else new_data
