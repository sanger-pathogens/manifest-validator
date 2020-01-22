import unittest
from unittest.mock import patch
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


class TestValidationRunner:

    class Namespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    @patch('validation_components.spreadsheet_parsing.SpreadsheetLoader')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery')
    @patch('validation_components.spreadsheet_parsing.ManifestEntry')
    def test_successful_validation(self, mocked_manifest, mocked_query, mocked_spreadsheetloader):
        Argparse_with_spreadsheet = self.Namespace(spreadsheet='directory/spreadsheet.xlsx')
        vl.validation_runner(Argparse_with_spreadsheet)

        # 3 forms of missing data errors correct calling
        # 2 mismatch data errors correct calling
        # successful validation calls
        # pre-existing data calls

class TestSpreadsheetParsing:

    def test_empty_row_ignored(self):
        pass


if __name__ == '__main__':
    unittest.main()
