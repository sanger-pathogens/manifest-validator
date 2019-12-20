import unittest
from unittest.mock import patch, Mock
from validation_components import spreadsheet_parsing as ss_parse
from _datetime import datetime


class TestNcbiQuerying(unittest.TestCase):

    def setUp(self):
        sample_id = 'study_sample123'
        common_name = 'Danio rerio'
        taxon_id = 7955
        self.fake_manifest = ss_parse.ManifestEntry(sample_id, common_name, taxon_id)
        self.ncbi_queries = ss_parse.NcbiQuery()

    @patch('requests.Session')
    def test_ncbi_search_with_common_name(self, mocked_session):
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
        self.fake_manifest.taxon_id = '7955'
        mocked_search.return_value = {'esearchresult': {'idlist': ['7955']}}
        returned_error, returned_common_name = self.ncbi_queries.query_ncbi(self.fake_manifest)
        self.assertIsNone(returned_error)
        self.assertIsNone(returned_common_name)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_id_doesnt_match(self, mocked_search, mocked_url):
        self.fake_manifest.taxon_id = '5597'
        mocked_search.return_value = {'esearchresult': {'idlist': ['7955']}}
        returned_error, returned_common_name = self.ncbi_queries.query_ncbi(self.fake_manifest)
        self.assertEqual(returned_error, 3)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_id_not_found(self, mocked_search, mocked_url):
        self.fake_manifest.error_code = 1
        self.fake_manifest.taxon_id = '5597'
        mocked_search.return_value = {'esearchresult': {'idlist': ['7955', '7954']}}
        returned_error, returned_common_name = self.ncbi_queries.query_ncbi(self.fake_manifest)
        self.assertEqual(returned_error, 2)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_not_found(self, mocked_search, mocked_url):
        self.fake_manifest.taxon_id = '7955'
        expected_common_name = 'Danio rerio'
        mocked_search.return_value = {'result': {'7955': {'scientificname': 'Danio rerio'}}}
        returned_error, returned_common_name = self.ncbi_queries.query_ncbi(self.fake_manifest)
        self.assertEqual(returned_common_name, expected_common_name)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_found(self, mocked_search, mocked_url):
        self.fake_manifest.taxon_id = '7955'
        expected_common_name = 'unkown as the taxon ID is invalid'
        mocked_search.return_value = {'result': {'7955': {'error': 'Doesnt exist'}}}
        returned_error, returned_common_name = self.ncbi_queries.query_ncbi(self.fake_manifest)
        self.assertEqual(returned_common_name, expected_common_name)

    @patch('time.sleep')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.get_now', return_value=datetime(2019, 12, 20, 14, 0, 59, 360000))
    def test_get_time_enough_time_passed(self, mock_datetime, mock_waiting):
        previous_timestamp = datetime(2019, 12, 20, 14, 0, 59, 0)
        ss_parse.NcbiQuery.generate_new_timestamp(previous_timestamp)
        mock_waiting.assert_not_called()

    @patch('time.sleep')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.get_now', return_value=datetime(2019, 12, 20, 14, 0, 59, 360000))
    def test_get_time_not_enough_time_passed(self, mock_datetime, mock_waiting):
        previous_timestamp = datetime(2019, 12, 20, 14, 0, 59, 360000)
        ss_parse.NcbiQuery.generate_new_timestamp(previous_timestamp)
        mock_waiting.assert_called_once()

    @patch('time.sleep')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.get_now', return_value=datetime(2019, 12, 20, 14, 0, 59, 360000))
    def test_get_time_not_yet_established(self, mock_datetime, mock_waiting):
        previous_timestamp = None
        ss_parse.NcbiQuery.generate_new_timestamp(previous_timestamp)
        mock_waiting.assert_not_called()

class TestManifestEntry(unittest.TestCase):

    def setUp(self):
        sample_id = 'study_sample123'
        common_name = 'Danio rerio'
        taxon_id = 7955
        self.fake_manifest = ss_parse.ManifestEntry(sample_id, common_name, taxon_id)
        self.ncbi_common_name = 'Real Common Name'

    def test_report_error_code_1_no_taxon_id(self):
        error_code = 1
        expected_return = 'Error: single common name found at study_sample123'
        actual_return = self.fake_manifest.report_error(error_code, self.ncbi_common_name)
        self.assertEqual(expected_return, actual_return)

    def test_report_error_code_1_no_common_name(self):
        error_code = 1
        self.fake_manifest.common_name = None
        expected_return = 'Error: single taxon id found at study_sample123'
        actual_return = self.fake_manifest.report_error(error_code, self.ncbi_common_name)
        self.assertEqual(expected_return, actual_return)

    def test_report_error_code_2_common_name_spelling(self):
        error_code = 2
        expected_return = 'Error: NCBI cant find Danio rerio, the official name for 7955 is Real Common Name'
        actual_return = self.fake_manifest.report_error(error_code, self.ncbi_common_name)
        self.assertEqual(expected_return, actual_return)

    def test_report_error_code_3_common_name_not_matching_taxon(self):
        error_code = 3
        expected_return = 'Error: Danio rerio doesnt match 7955 the official name for 7955 is Real Common Name'
        actual_return = self.fake_manifest.report_error(error_code, self.ncbi_common_name)
        self.assertEqual(expected_return, actual_return)

if __name__ == '__main__':
    unittest.main()
