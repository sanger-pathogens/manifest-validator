import xlrd


class Spreadsheet:

    @staticmethod
    def new_instance(row, common_name, taxon_id, ncbi_common_name=str):
        result = Spreadsheet()
        result.row = row
        result.common_name = common_name
        result.taxon_id = taxon_id
        result.ncbi_common_name = ncbi_common_name
        return result


class SpreadsheetLoader:

    def __init__(self, file):
        self._file = file
        self._workbook = xlrd.open_workbook(self._file)
        self._sheet = self._workbook.sheet_by_index(0)

    def load(self):
        result = Spreadsheet()
        data_row = 0
        header_row = 0
        for i in range(self._sheet.nrows):
            if self._sheet.cell_value(i, 0) == 'SANGER PLATE ID':
                data_row = i + 1
                header_row = i
                break

        for i in range(self._sheet.ncols):
            if self._sheet.cell_value(header_row, i) == 'COMMON NAME':
                common_name_column = i
            if self._sheet.cell_value(header_row, i) == 'TAXON ID':
                taxon_id_column = i

        taxon_set = []
        for i in range(data_row, self._sheet.nrows):
            common_name = self.__extract_text_value(i, common_name_column)
            taxon_id = self.__extract_float_value(i, taxon_id_column)
            if common_name is not None and taxon_id is not None:
                taxon_set.append([i, common_name, taxon_id])
        result.taxon_sets = taxon_set
        return result

    def __extract_text_value(self, row, column):
        new_data = self._sheet.cell_value(row, column).strip()
        return None if new_data == '' else new_data

    def __extract_float_value(self, row, column):
        if self._sheet.cell_type(row, column) != xlrd.XL_CELL_NUMBER:
            return self.__extract_text_value(row, column)
        return str(int(self._sheet.cell_value(row, column)))
