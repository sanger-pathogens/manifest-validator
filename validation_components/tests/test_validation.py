import unittest
import os

from unittest.mock import patch, MagicMock
from validation_components import manifest_querying as m_query, validation as vl
from _datetime import datetime


class TestNcbiQuerying(unittest.TestCase):

    def setUp(self):
        sample_id = 'study_sample123'
        common_name = 'Danio rerio'
        taxon_id = '7955'
        self.fake_manifest = m_query.ManifestEntry(sample_id, common_name, taxon_id)
        self.ncbi_queries = m_query.NcbiQuery()

    class MockedNcbiQuery:
        def __init__(self):
            self.timestamp = None

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

    @patch('validation_components.manifest_querying.NcbiQuery.build_url')
    @patch('validation_components.manifest_querying.NcbiQuery.ncbi_search')
    def test_query_ncbi_id_matches(self, mocked_search, mocked_url):
        expected_return_value = '7955'
        mocked_search.return_value = {'esearchresult': {'idlist': ['7955']}}
        returned_taxon_id = self.ncbi_queries.query_ncbi_for_taxon_id(self.fake_manifest)
        self.assertEqual(returned_taxon_id, expected_return_value)

    @patch('validation_components.manifest_querying.NcbiQuery.build_url')
    @patch('validation_components.manifest_querying.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_not_found(self, mocked_search, mocked_url):
        expected_common_name = 'Danio rerio'
        mocked_search.return_value = {'result': {'7955': {'scientificname': 'Danio rerio'}}}
        returned_common_name = self.ncbi_queries.query_ncbi_for_common_name(self.fake_manifest)
        self.assertEqual(returned_common_name, expected_common_name)

    @patch('validation_components.manifest_querying.NcbiQuery.build_url')
    @patch('validation_components.manifest_querying.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_not_found(self, mocked_search, mocked_url):
        expected_common_name = '__null__'
        mocked_search.return_value = {'result': {'12': {'scientificname': ''}}}
        returned_common_name = self.ncbi_queries.query_ncbi_for_common_name(self.fake_manifest)
        self.assertEqual(returned_common_name, expected_common_name)

    @patch('validation_components.manifest_querying.NcbiQuery.build_url')
    @patch('validation_components.manifest_querying.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_found(self, mocked_search, mocked_url):
        self.fake_manifest.taxon_id = '7955'
        expected_common_name = '__null__'
        mocked_search.return_value = {'result': {'7955': {'error': 'Doesnt exist'}}}
        returned_common_name = self.ncbi_queries.query_ncbi_for_common_name(self.fake_manifest)
        self.assertEqual(returned_common_name, expected_common_name)

    @patch('time.sleep')
    @patch('validation_components.manifest_querying.NcbiQuery.get_now',
           return_value=datetime(2019, 12, 20, 14, 0, 59, 360000))
    def test_get_time_enough_time_passed(self, mock_datetime, mock_waiting):
        previous_timestamp = self.MockedNcbiQuery()
        previous_timestamp.timestamp = datetime(2019, 12, 20, 14, 0, 59, 0)
        m_query.NcbiQuery.generate_new_timestamp(previous_timestamp)
        mock_waiting.assert_not_called()

    @patch('time.sleep')
    @patch('validation_components.manifest_querying.NcbiQuery.get_now',
           return_value=datetime(2019, 12, 20, 14, 0, 59, 360000))
    def test_get_time_not_enough_time_passed(self, mock_datetime, mock_waiting):
        previous_timestamp = self.MockedNcbiQuery()
        previous_timestamp.timestamp = datetime(2019, 12, 20, 14, 0, 59, 360000)
        m_query.NcbiQuery.generate_new_timestamp(previous_timestamp)
        mock_waiting.assert_called_once()

    @patch('time.sleep')
    @patch('validation_components.manifest_querying.NcbiQuery.get_now',
           return_value=datetime(2019, 12, 20, 14, 0, 59, 360000))
    def test_get_time_not_yet_established(self, mock_datetime, mock_waiting):
        previous_timestamp = self.MockedNcbiQuery()
        m_query.NcbiQuery.generate_new_timestamp(previous_timestamp)
        mock_waiting.assert_not_called()


class TestManifestEntry(unittest.TestCase):

    def setUp(self):
        sample_id = 'study_sample123'
        common_name = 'Danio rerio'
        taxon_id = '7955'
        self.fake_manifest = m_query.ManifestEntry(sample_id, common_name, taxon_id)
        self.ncbi_common_name = 'Real Common Name'

    def test_report_error_code_1_unmatched_returns(self):
        error_code = 1
        common_name_statement = "Common Name Statement First. "
        taxon_id_statement = "Taxon ID Statement Second."
        expected_return = ": Taxon ID and common name don't match. Common Name Statement First. Taxon ID Statement Second."
        actual_return = self.fake_manifest.report_error(error_code, common_name_statement, taxon_id_statement)
        self.assertEqual(expected_return, actual_return)

    def test_report_error_code_2_random_errors(self):
        error_code = 2
        common_name_statement = "Common Name Statement First. "
        taxon_id_statement = "Taxon ID Statement Second."
        expected_return = ': The given common name matches a taxon ID but is not precise. Common Name Statement First. Taxon ID Statement Second.'
        actual_return = self.fake_manifest.report_error(error_code, common_name_statement, taxon_id_statement)
        self.assertEqual(expected_return, actual_return)

    def test_report_error_code_3_random_errors(self):
        error_code = 3
        common_name_statement = "Common Name Statement First. "
        taxon_id_statement = "Taxon ID Statement Second."
        expected_return = ': Common Name Statement First. Taxon ID Statement Second.'
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
        expected_return = "The given common name 'value' does not exist in the NCBI database. "
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
        expected_return = "The given taxon ID num123 does not exist in the NCBI database."
        actual_return = self.fake_manifest.taxon_id_definition(ncbi_data)
        self.assertEqual(expected_return, actual_return)

    def test_taxon_id_returns_statement(self):
        ncbi_data = "value"
        self.fake_manifest.taxon_id = 'num123'
        expected_return = "The official name for the given taxon ID num123 is 'value'."
        actual_return = self.fake_manifest.taxon_id_definition(ncbi_data)
        self.assertEqual(expected_return, actual_return)


class TestValidationRunner(unittest.TestCase):

    def setUp(self):
        sample_id = ''
        common_name = ''
        taxon_id = ''
        self.fake_manifest = m_query.ManifestEntry(sample_id, common_name, taxon_id)
        self.ncbi_common_name = 'Real Common Name'
        self.ncbi_taxon_id = "12345"
        self.mocked_query = MagicMock()
        self.mocked_query.generate_new_timestamp.return_value = 1

    @patch('builtins.print')
    @patch('validation_components.validation.verify_entries')
    @patch('validation_components.manifest_querying.SpreadsheetLoader.__init__')
    @patch('validation_components.manifest_querying.SpreadsheetLoader.load')
    def test_successful_validation(self, mocked_load, patched_spreadsheet, mocked_inner, mocked_print):
        argparse_with_spreadsheet = self.Namespace(spreadsheet='')
        EMPTY_LIST = []
        EXPECTED = 'Manifest successfully validated, no errors found!'
        mocked_inner.return_value = EMPTY_LIST
        patched_spreadsheet.return_value = None
        vl.validation_runner(argparse_with_spreadsheet)
        mocked_load.assert_called_once()
        mocked_print.assert_called_with(EXPECTED)

    @patch('builtins.print')
    @patch('validation_components.validation.verify_entries')
    @patch('validation_components.manifest_querying.SpreadsheetLoader.__init__')
    @patch('validation_components.manifest_querying.SpreadsheetLoader.load')
    def test_unsuccessful_validation(self, mocked_load, patched_spreadsheet, mocked_inner, mocked_print):
        argparse_with_spreadsheet = self.Namespace(spreadsheet='')
        NON_EMPTY_LIST = ['err', 'err2']
        EXPECTED = 'Errors found within manifest:\n\terr\n\terr2\nPlease correct mistakes and validate again.'
        mocked_inner.return_value = NON_EMPTY_LIST
        patched_spreadsheet.return_value = None
        vl.validation_runner(argparse_with_spreadsheet)
        mocked_load.assert_called_once()
        mocked_print.assert_called_with(EXPECTED)

    @patch('validation_components.manifest_querying.NcbiQuery.__init__')
    def test_verify_entries_present_in_dictionary(self, mocked_query):
        mocked_query.return_value = None
        self.fake_manifest.sample_id = 'abc123'
        self.fake_manifest.common_name = '__null__'
        self.fake_manifest.taxon_id = '__null__'
        self.fake_manifest.query_id = '__null____null__'
        ENTRY_LIST = [self.fake_manifest]
        returned_value = vl.verify_entries(ENTRY_LIST)
        expected_return = ["abc123: No taxon ID or common name specified. If unkown please use 32644 - 'unidentified'."]
        self.assertEqual(returned_value, expected_return)

    @patch('validation_components.validation.define_error')
    @patch('validation_components.validation.resolve_common_name')
    @patch('validation_components.validation.resolve_taxon_id')
    @patch('validation_components.manifest_querying.NcbiQuery.__init__')
    def test_verify_entries_matching_gets_one_search(self, mocked_query, mocked_taxon_return, mocked_common_name_return, mocked_error):
        mocked_query.return_value = None
        mocked_taxon_return.return_value = 'species'
        self.fake_manifest.sample_id = 'abc123'
        self.fake_manifest.common_name = 'species'
        self.fake_manifest.taxon_id = '12345'
        self.fake_manifest.query_id = 'species12345'
        ENTRY_LIST = [self.fake_manifest]
        returned_value = vl.verify_entries(ENTRY_LIST)
        expected_return = []
        self.assertEqual(returned_value, expected_return)
        mocked_taxon_return.assert_called_once()
        mocked_common_name_return.assert_not_called()
        mocked_error.assert_not_called()

    @patch('validation_components.validation.resolve_taxon_id')
    @patch('validation_components.manifest_querying.NcbiQuery.__init__')
    def test_verify_entries_matching_gets_one_search_for_repeated_query_ids(self, mocked_query, mocked_taxon_return):
        mocked_query.return_value = None
        mocked_taxon_return.return_value = 'species'
        self.fake_manifest.sample_id = 'abc123'
        self.fake_manifest.common_name = 'species'
        self.fake_manifest.taxon_id = '12345'
        self.fake_manifest.query_id = 'species12345'
        self.fake_manifest2 = self.fake_manifest
        self.fake_manifest2.sample_id = 'xyz456'
        ENTRY_LIST = [self.fake_manifest]
        returned_value = vl.verify_entries(ENTRY_LIST)
        expected_return = []
        self.assertEqual(returned_value, expected_return)
        mocked_taxon_return.assert_called_once()

    @patch('validation_components.validation.define_error')
    @patch('validation_components.validation.resolve_error')
    @patch('validation_components.validation.resolve_common_name')
    @patch('validation_components.validation.resolve_taxon_id')
    @patch('validation_components.manifest_querying.NcbiQuery.__init__')
    def test_verify_entries_non_matching_get_searched_twice(self, mocked_query, mocked_taxon_return, mocked_common_name_return, mocked_resolve, mocked_definition):
        mocked_query.return_value = None
        mocked_common_name_return.return_value = '67890'
        mocked_taxon_return.return_value = 'species2'
        mocked_definition.return_value = 'term1'
        self.fake_manifest.sample_id = 'abc123'
        self.fake_manifest.common_name = 'species'
        self.fake_manifest.taxon_id = '12345'
        self.fake_manifest.query_id = 'species12345'
        ENTRY_LIST = [self.fake_manifest]
        returned_value = vl.verify_entries(ENTRY_LIST)
        expected_return = ['abc123term1']
        self.assertEqual(returned_value, expected_return)
        mocked_common_name_return.assert_called_once()
        mocked_taxon_return.assert_called_once()
        mocked_resolve.assert_called_once()
        mocked_definition.assert_called_once()

    def test_resolve_common_name_present_initial_returns_ncbi_search(self):
        self.fake_manifest.common_name = 'species'
        self.fake_manifest.taxon_id = '12345'
        self.mocked_query.query_ncbi_for_taxon_id.return_value = 'NCBI VALUE'
        returned_value = vl.resolve_common_name(self.mocked_query, self.fake_manifest)
        EXPECTED_RESULT = 'NCBI VALUE'
        self.assertEqual(returned_value, EXPECTED_RESULT)

    def test_resolve_common_name_no_initial_returns_null(self):
        self.fake_manifest.common_name = '__null__'
        self.fake_manifest.taxon_id = '12345'
        self.mocked_query.query_ncbi_for_taxon_id.return_value = 'Not null'
        returned_value = vl.resolve_common_name(self.mocked_query, self.fake_manifest)
        EXPECTED_RESULT = '__null__'
        self.assertEqual(returned_value, EXPECTED_RESULT)

    def test_resolve_taxon_id_no_initial_returns_null(self):
        self.fake_manifest.common_name = 'value'
        self.fake_manifest.taxon_id = '__null__'
        self.mocked_query.query_ncbi_for_common_name.return_value = 'Not null'
        returned_value = vl.resolve_taxon_id(self.mocked_query, self.fake_manifest)
        EXPECTED_RESULT = '__null__'
        self.assertEqual(returned_value, EXPECTED_RESULT)

    def test_resolve_taxon_id_returns_ncbi(self):
        self.fake_manifest.common_name = 'value'
        self.fake_manifest.taxon_id = 'taxId'
        self.mocked_query.query_ncbi_for_common_name.return_value = 'Not null'
        returned_value = vl.resolve_taxon_id(self.mocked_query, self.fake_manifest)
        EXPECTED_RESULT = 'Not null'
        self.assertEqual(returned_value, EXPECTED_RESULT)

    @patch('validation_components.manifest_querying.ManifestEntry.taxon_id_definition')
    @patch('validation_components.manifest_querying.ManifestEntry.common_name_definition')
    @patch('validation_components.manifest_querying.ManifestEntry.report_error')
    def test_define_error(self, mocked_error_report, mocked_name_definition, mocked_id_definition):
        error_code = 1
        ncbi_taxon_id = 'taxId'
        ncbi_common_name = 'value'
        mocked_name_definition.return_value = 'name term'
        mocked_id_definition.return_value = 'taxon term'
        mocked_error_report.return_value = 'full term'
        returned_value = vl.define_error(error_code, self.fake_manifest, ncbi_taxon_id, ncbi_common_name)
        EXPECTED_RESULT = 'full term'
        self.assertEqual(returned_value, EXPECTED_RESULT)
        mocked_name_definition.assert_called_with('taxId')
        mocked_error_report.assert_called_with(1, 'name term', 'taxon term')
        mocked_id_definition.assert_called_with('value')

    def test_resolve_error_correct_non_matching(self):
        ncbi_common_name = 'value'
        ncbi_taxon_id = 'taxId'
        returned_value = vl.resolve_error(ncbi_common_name, ncbi_taxon_id, self.fake_manifest)
        EXPECTED_RESULT = 1
        self.assertEqual(returned_value, EXPECTED_RESULT)

    def test_resolve_error_null_cases(self):
        ncbi_common_name = '__null__'
        ncbi_taxon_id = 'taxId'
        returned_value = vl.resolve_error(ncbi_common_name, ncbi_taxon_id, self.fake_manifest)
        EXPECTED_RESULT = 3
        self.assertEqual(returned_value, EXPECTED_RESULT)

        ncbi_common_name = 'value'
        ncbi_taxon_id = '__null__'
        returned_value = vl.resolve_error(ncbi_common_name, ncbi_taxon_id, self.fake_manifest)
        EXPECTED_RESULT = 3
        self.assertEqual(returned_value, EXPECTED_RESULT)

        ncbi_common_name = '__null__'
        ncbi_taxon_id = '__null__'
        returned_value = vl.resolve_error(ncbi_common_name, ncbi_taxon_id, self.fake_manifest)
        EXPECTED_RESULT = 3
        self.assertEqual(returned_value, EXPECTED_RESULT)

    class Namespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


class TestSpreadsheetParsing(unittest.TestCase):
    data_dir = os.path.dirname(os.path.abspath(__file__))

    def test_empty_row_ignored(self):
        loader = m_query.SpreadsheetLoader(os.path.join(self.data_dir, 'test_spreadsheet_loading.xlsx'))

        sample_id = 'sample1'
        common_name = 'common_name1'
        taxon_id = 'tax_id1'
        fake_manifest_1 = m_query.ManifestEntry(sample_id, common_name, taxon_id)

        sample_id = 'sample2 null name'
        common_name = '__null__'
        taxon_id = 'tax_id2'
        fake_manifest_2 = m_query.ManifestEntry(sample_id, common_name, taxon_id)

        sample_id = 'sample3 null id'
        common_name = 'common_name3'
        taxon_id = '__null__'
        fake_manifest_3 = m_query.ManifestEntry(sample_id, common_name, taxon_id)

        sample_id = 'sample4 after space'
        common_name = 'common_name4'
        taxon_id = 'tax_id4'
        fake_manifest_4 = m_query.ManifestEntry(sample_id, common_name, taxon_id)

        expected = [fake_manifest_1, fake_manifest_2, fake_manifest_3, fake_manifest_4]
        actual = loader.load()
        for position, return_value in enumerate(actual):
            self.assertEqual(return_value.sample_id, expected[position].sample_id)
            self.assertEqual(return_value.common_name, expected[position].common_name)
            self.assertEqual(return_value.taxon_id, expected[position].taxon_id)
            self.assertEqual(return_value.query_id, expected[position].query_id)


if __name__ == '__main__':
    unittest.main()
