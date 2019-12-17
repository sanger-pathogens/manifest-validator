import xlrd


class ManifestEntry:
    '''A class construct for a single entry from the manifest submitted'''
    def __init__(self, sample_id, common_name, taxon_id, ncbi_common_name=str):
        self.sample_id = sample_id
        self.common_name = common_name
        self.taxon_id = taxon_id
        self.ncbi_common_name = ncbi_common_name
        self.query_id = common_name + str(taxon_id)


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
