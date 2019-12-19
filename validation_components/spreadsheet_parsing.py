import xlrd
import requests

class ManifestEntry:
    '''A class construct for a single entry from the manifest submitted'''
    def __init__(self, sample_id: str, common_name: str, taxon_id: int):
        self.sample_id = sample_id
        self.common_name = common_name
        self.taxon_id = str(taxon_id)
        self.ncbi_common_name = ''
        self.query_id = common_name + str(taxon_id)

    def query_ncbi(self):
        tax_id_json = self.ncbi_search(esearch=True)
        if 'esearchresult' in tax_id_json and 'idlist' in tax_id_json['esearchresult'] and len(
                tax_id_json['esearchresult']['idlist']) == 1:
            if tax_id_json['esearchresult']['idlist'][0] == self.taxon_id:
                return None
            else:
                error = 3
        else:
            error = 2

        common_name_json = self.ncbi_search(esearch=False)
        if 'result' in common_name_json and self.taxon_id in common_name_json['result'] and 'scientificname' in \
                common_name_json['result'][self.taxon_id]:
            self.ncbi_common_name = tax_id_json['result'][self.taxon_id]['scientificname']
        else:
            self.ncbi_common_name = 'unkown as the taxon ID is invalid'
        return error

    def ncbi_search(self, esearch: bool):
        mid_url = '.fcgi?db=taxonomy&'
        base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
        end_url = '&retmode=json'
        search_session = requests.Session()

        if esearch:
            url = base_url + 'esearch' + mid_url + 'field=All%20Names&term=' + self.common_name + end_url
        else:
            url = base_url + 'esummary' + mid_url + 'id=' + self.taxon_id + end_url
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
