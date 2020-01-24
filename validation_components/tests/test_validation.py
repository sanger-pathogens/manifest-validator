import unittest
from unittest.mock import patch, MagicMock
from validation_components import spreadsheet_parsing as ss_parse, validation as vl
from _datetime import datetime


class TestNcbiQuerying(unittest.TestCase):

    def setUp(self):
        sample_id = 'study_sample123'
        common_name = 'Danio rerio'
        taxon_id = '7955'
        self.fake_manifest = ss_parse.ManifestEntry(sample_id, common_name, taxon_id)
        self.ncbi_queries = ss_parse.NcbiQuery()

    @patch('requests.Session')
    def test_ncbi_search(self, mocked_session):
        url = 'https://fake.url.gov/page/id'
        self.ncbi_queries.ncbi_search(url)
        self.assertIn(unittest.mock.call().get('https://fake.url.gov/page/id'),
                      mocked_session.mock_calls)

    def test_build_url_with_common_name(self):
        esearch = True
        expected_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&field=All%20Names&term' \
                       '=Danio rerio&retmode=json'
        returned_url = self.ncbi_queries.build_url(self.fake_manifest, esearch)
        self.assertEqual(returned_url, expected_url)

    def test_build_url_with_taxon_id(self):
        esearch = False
        expected_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy&id=7955&retmode=json'
        returned_url = self.ncbi_queries.build_url(self.fake_manifest, esearch)
        self.assertEqual(returned_url, expected_url)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_id_matches(self, mocked_search, mocked_url):
        expected_return_value = '7955'
        mocked_search.return_value = {'esearchresult': {'idlist': ['7955']}}
        returned_taxon_id = self.ncbi_queries.query_ncbi_for_taxon_id(self.fake_manifest)
        self.assertEqual(returned_taxon_id, expected_return_value)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_not_found(self, mocked_search, mocked_url):
        expected_common_name = 'Danio rerio'
        mocked_search.return_value = {'result': {'7955': {'scientificname': 'Danio rerio'}}}
        returned_common_name = self.ncbi_queries.query_ncbi_for_common_name(self.fake_manifest)
        self.assertEqual(returned_common_name, expected_common_name)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_not_found(self, mocked_search, mocked_url):
        expected_common_name = '__null__'
        mocked_search.return_value = {'result': {'12': {'scientificname': ''}}}
        returned_common_name = self.ncbi_queries.query_ncbi_for_common_name(self.fake_manifest)
        self.assertEqual(returned_common_name, expected_common_name)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_found(self, mocked_search, mocked_url):
        self.fake_manifest.taxon_id = '7955'
        expected_common_name = '__null__'
        mocked_search.return_value = {'result': {'7955': {'error': 'Doesnt exist'}}}
        returned_common_name = self.ncbi_queries.query_ncbi_for_common_name(self.fake_manifest)
        self.assertEqual(returned_common_name, expected_common_name)

    @patch('time.sleep')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.get_now',
           return_value=datetime(2019, 12, 20, 14, 0, 59, 360000))
    def test_get_time_enough_time_passed(self, mock_datetime, mock_waiting):
        previous_timestamp = datetime(2019, 12, 20, 14, 0, 59, 0)
        ss_parse.NcbiQuery.generate_new_timestamp(previous_timestamp)
        mock_waiting.assert_not_called()

    @patch('time.sleep')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.get_now',
           return_value=datetime(2019, 12, 20, 14, 0, 59, 360000))
    def test_get_time_not_enough_time_passed(self, mock_datetime, mock_waiting):
        previous_timestamp = datetime(2019, 12, 20, 14, 0, 59, 360000)
        ss_parse.NcbiQuery.generate_new_timestamp(previous_timestamp)
        mock_waiting.assert_called_once()

    @patch('time.sleep')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.get_now',
           return_value=datetime(2019, 12, 20, 14, 0, 59, 360000))
    def test_get_time_not_yet_established(self, mock_datetime, mock_waiting):
        previous_timestamp = None
        ss_parse.NcbiQuery.generate_new_timestamp(previous_timestamp)
        mock_waiting.assert_not_called()


class TestManifestEntry(unittest.TestCase):

    def setUp(self):
        sample_id = 'study_sample123'
        common_name = 'Danio rerio'
        taxon_id = '7955'
        self.fake_manifest = ss_parse.ManifestEntry(sample_id, common_name, taxon_id)
        self.ncbi_common_name = 'Real Common Name'

    def test_report_error_code_1_no_data(self):
        error_code = 1
        common_name_statement = None
        taxon_id_statement = None
        expected_return = "study_sample123: No taxon ID or common name specified." \
                          " If unkown please use 32644 - 'unidentified'."
        actual_return = self.fake_manifest.report_error(error_code, common_name_statement, taxon_id_statement)
        self.assertEqual(expected_return, actual_return)

    def test_report_error_code_2_unmatched_returns(self):
        error_code = 2
        common_name_statement = "Common Name Statement First. "
        taxon_id_statement = "Taxon ID Statement Second."
        expected_return = "study_sample123: Taxon ID and common name don't match. Common Name Statement First. Taxon ID Statement Second."
        actual_return = self.fake_manifest.report_error(error_code, common_name_statement, taxon_id_statement)
        self.assertEqual(expected_return, actual_return)

    def test_report_error_code_3_(self):
        error_code = 3
        common_name_statement = "Common Name Statement First. "
        taxon_id_statement = "Taxon ID Statement Second."
        expected_return = 'study_sample123: Common Name Statement First. Taxon ID Statement Second.'
        actual_return = self.fake_manifest.report_error(error_code, common_name_statement, taxon_id_statement)
        self.assertEqual(expected_return, actual_return)

    def test_common_name_null_statement(self):
        ncbi_data = None
        self.fake_manifest.common_name = '__null__'
        expected_return = "No common name specified. "
        actual_return = self.fake_manifest.common_name_definition(ncbi_data)
        self.assertEqual(expected_return, actual_return)

    def test_common_name_ncbi_tax_id_null_statement(self):
        ncbi_data = "__null__"
        self.fake_manifest.common_name = 'value'
        expected_return = "The common name 'value' does not exist in the NCBI database. "
        actual_return = self.fake_manifest.common_name_definition(ncbi_data)
        self.assertEqual(expected_return, actual_return)

    def test_common_name_returns_statement(self):
        ncbi_data = "num123"
        self.fake_manifest.common_name = 'value'
        expected_return = "The taxon ID for given name 'value' is num123. "
        actual_return = self.fake_manifest.common_name_definition(ncbi_data)
        self.assertEqual(expected_return, actual_return)

    def test_taxon_id_null_statement(self):
        ncbi_data = None
        self.fake_manifest.taxon_id = '__null__'
        expected_return = "No taxon ID specified."
        actual_return = self.fake_manifest.taxon_id_definition(ncbi_data)
        self.assertEqual(expected_return, actual_return)

    def test_taxon_id_ncbi_common_name_null_statement(self):
        ncbi_data = "__null__"
        self.fake_manifest.taxon_id = 'num123'
        expected_return = "The taxon ID is not officially recognised by NCBI."
        actual_return = self.fake_manifest.taxon_id_definition(ncbi_data)
        self.assertEqual(expected_return, actual_return)

    def test_taxon_id_returns_statement(self):
        ncbi_data = "value"
        self.fake_manifest.taxon_id = 'num123'
        expected_return = "The official name for the given taxon ID num123 is 'value'."
        actual_return = self.fake_manifest.taxon_id_definition(ncbi_data)
        self.assertEqual(expected_return, actual_return)


class TestValidationRunner(unittest.TestCase):

    # @patch()
    # Argparse_with_spreadsheet = self.Namespace(spreadsheet='directory/spreadsheet.xlsx')
    # vl.validation_runner(Argparse_with_spreadsheet)

    def setUp(self):
        sample_id = ''
        common_name = ''
        taxon_id = ''
        self.fake_manifest = ss_parse.ManifestEntry(sample_id, common_name, taxon_id)
        self.ncbi_common_name = 'Real Common Name'
        self.mocked_query = MagicMock()
        self.mocked_query.generate_new_timestamp.return_value = 1

    @patch('builtins.print')
    @patch('validation_components.validation.verify_entries')
    @patch('validation_components.spreadsheet_parsing.SpreadsheetLoader.__init__')
    @patch('validation_components.spreadsheet_parsing.SpreadsheetLoader.load')
    def test_successful_validation(self, mocked_load, patched_spreadsheet, mocked_inner, mocked_print):
        Argparse_with_spreadsheet = self.Namespace(spreadsheet='')
        EMPTY_LIST = []
        EXPECTED = 'Manifest successfully validated, no errors found!'
        mocked_inner.return_value = EMPTY_LIST
        patched_spreadsheet.return_value = None
        vl.validation_runner(Argparse_with_spreadsheet)
        mocked_load.assert_called_once()
        mocked_print.assert_called_with(EXPECTED)

    @patch('builtins.print')
    @patch('validation_components.validation.verify_entries')
    @patch('validation_components.spreadsheet_parsing.SpreadsheetLoader.__init__')
    @patch('validation_components.spreadsheet_parsing.SpreadsheetLoader.load')
    def test_unsuccessful_validation(self, mocked_load, patched_spreadsheet, mocked_inner, mocked_print):
        Argparse_with_spreadsheet = self.Namespace(spreadsheet='')
        NON_EMPTY_LIST = ['err','err2']
        EXPECTED = 'Errors found within manifest:\n\terr\n\terr2\nPlease correct mistakes and validate again.'
        mocked_inner.return_value = NON_EMPTY_LIST
        patched_spreadsheet.return_value = None
        vl.validation_runner(Argparse_with_spreadsheet)
        mocked_load.assert_called_once()
        mocked_print.assert_called_with(EXPECTED)

    @patch('validation_components.spreadsheet_parsing.ManifestEntry.report_error')
    @patch('validation_components.validation.resolve_common_name')
    @patch('validation_components.validation.resolve_taxon_id')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.__init__')
    def test_verify_entries_present_in_dictionary(self, mocked_query, mocked_taxon_return, mocked_common_name_return, mocked_error):
        mocked_query.return_value = None
        self.fake_manifest.sample_id = 'abc123'
        self.fake_manifest.common_name = '__null__'
        self.fake_manifest.taxon_id = '__null__'
        self.fake_manifest.query_id = '__null____null__'
        ENTRY_LIST = [self.fake_manifest]
        returned_value = vl.verify_entries(ENTRY_LIST)
        mocked_error.assert_called_with(1, None, None)

    @patch('validation_components.spreadsheet_parsing.ManifestEntry.report_error')
    @patch('validation_components.validation.resolve_common_name')
    @patch('validation_components.validation.resolve_taxon_id')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.__init__')
    def test_verify_entries_matching_gets_one_search(self, mocked_query, mocked_taxon_return, mocked_common_name_return, mocked_error):
        mocked_query.return_value = None
        mocked_common_name_return.return_value = ('quote','12345', 135)
        self.fake_manifest.sample_id = 'abc123'
        self.fake_manifest.common_name = 'species'
        self.fake_manifest.taxon_id = '12345'
        self.fake_manifest.query_id = 'species12345'
        ENTRY_LIST = [self.fake_manifest]
        returned_value = vl.verify_entries(ENTRY_LIST)
        mocked_common_name_return.assert_called_once()
        mocked_taxon_return.assert_not_called()
        mocked_error.assert_not_called()

    @patch('validation_components.spreadsheet_parsing.ManifestEntry.report_error')
    @patch('validation_components.validation.resolve_common_name')
    @patch('validation_components.validation.resolve_taxon_id')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.__init__')
    def test_verify_entries_non_matching_get_searched_twice(self, mocked_query, mocked_taxon_return, mocked_common_name_return, mocked_error):
        mocked_query.return_value = None
        mocked_common_name_return.return_value = ('quote','67890', 135)
        mocked_taxon_return.return_value = (1, 'quote2', 135)
        self.fake_manifest.sample_id = 'abc123'
        self.fake_manifest.common_name = 'species'
        self.fake_manifest.taxon_id = '12345'
        self.fake_manifest.query_id = 'species12345'
        ENTRY_LIST = [self.fake_manifest]
        returned_value = vl.verify_entries(ENTRY_LIST)
        mocked_common_name_return.assert_called_once()
        mocked_taxon_return.assert_called_once()
        mocked_error.assert_called_with(1, 'quote', 'quote2')

    @patch('validation_components.spreadsheet_parsing.ManifestEntry.common_name_definition')
    def test_resolve_common_name_present_initial_returns_ncbi_search(self, mocked_definition):
        mocked_definition.return_value = None
        self.fake_manifest.common_name = 'species'
        self.fake_manifest.taxon_id = '12345'
        self.mocked_query.query_ncbi_for_taxon_id.return_value = 'NCBI VALUE'
        returned_value = vl.resolve_common_name(self.mocked_query, self.fake_manifest, None)
        EXPECTED_RESULT = (None, 'NCBI VALUE', 1)
        self.assertEqual(returned_value, EXPECTED_RESULT)

    @patch('validation_components.spreadsheet_parsing.ManifestEntry.common_name_definition')
    def test_resolve_common_name_no_initial_returns_null(self, mocked_definition):
        mocked_definition.return_value = None
        self.fake_manifest.common_name = '__null__'
        self.fake_manifest.taxon_id = '12345'
        self.mocked_query.query_ncbi_for_taxon_id.return_value = 'Not null'
        returned_value = vl.resolve_common_name(self.mocked_query, self.fake_manifest, None)
        EXPECTED_RESULT = (None, '__null__', None)
        self.assertEqual(returned_value, EXPECTED_RESULT)

    @patch('validation_components.spreadsheet_parsing.ManifestEntry.taxon_id_definition')
    def test_resolve_taxon_id_no_initial_returns_null_and_error_3(self, mocked_definition):
        mocked_definition.return_value = None
        self.fake_manifest.common_name = 'value'
        self.fake_manifest.taxon_id = '__null__'
        self.mocked_query.query_ncbi_for_common_name.return_value = 'Not null'
        returned_value = vl.resolve_taxon_id(self.mocked_query, self.fake_manifest, None, 'Not_Null')
        EXPECTED_RESULT = (3, None, None)
        mocked_definition.assert_called_once_with('__null__')
        self.assertEqual(returned_value, EXPECTED_RESULT)

    @patch('validation_components.spreadsheet_parsing.ManifestEntry.taxon_id_definition')
    def test_resolve_taxon_id_null_ncbi_returns_error_3(self, mocked_definition):
        mocked_definition.return_value = None
        self.fake_manifest.common_name = 'value'
        self.fake_manifest.taxon_id = 'not null'
        self.mocked_query.query_ncbi_for_common_name.return_value = '__null__'
        returned_value = vl.resolve_taxon_id(self.mocked_query, self.fake_manifest, None, 'Not_Null')
        EXPECTED_RESULT = (3, None, 1)
        mocked_definition.assert_called_once_with('__null__')
        self.assertEqual(returned_value, EXPECTED_RESULT)

    @patch('validation_components.spreadsheet_parsing.ManifestEntry.taxon_id_definition')
    def test_resolve_taxon_id_no_ncbi_taxon_id_returns_query_and_error_3(self, mocked_definition):
        mocked_definition.return_value = None
        self.fake_manifest.common_name = 'value'
        self.fake_manifest.taxon_id = 'Not Null'
        self.mocked_query.query_ncbi_for_common_name.return_value = 'Not Null Query'
        returned_value = vl.resolve_taxon_id(self.mocked_query, self.fake_manifest, None, '__null__')
        EXPECTED_RESULT = (3, None, 1)
        mocked_definition.assert_called_once_with('Not Null Query')
        self.assertEqual(returned_value, EXPECTED_RESULT)

    @patch('validation_components.spreadsheet_parsing.ManifestEntry.taxon_id_definition')
    def test_resolve_taxon_id_no_null_values_returns_query_and_error_2(self, mocked_definition):
        mocked_definition.return_value = None
        self.fake_manifest.common_name = 'value'
        self.fake_manifest.taxon_id = 'Not Null'
        self.mocked_query.query_ncbi_for_common_name.return_value = 'Not Null Query'
        returned_value = vl.resolve_taxon_id(self.mocked_query, self.fake_manifest, None, 'Ncbi_taxon_id')
        EXPECTED_RESULT = (2, None, 1)
        mocked_definition.assert_called_once_with('Not Null Query')
        self.assertEqual(returned_value, EXPECTED_RESULT)

    class Namespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


class TestSpreadsheetParsing:

    def test_empty_row_ignored(self):
        pass


if __name__ == '__main__':
    unittest.main()
