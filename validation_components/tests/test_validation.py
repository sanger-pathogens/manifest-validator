import unittest
from unittest.mock import patch, Mock
from validation_components import spreadsheet_parsing as ss_parse


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
        expected_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&field=All%20Names&term=Danio rerio&retmode=json'
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
        self.fake_manifest.error_code = 1
        self.fake_manifest.taxon_id = '7955'
        mocked_search.return_value = {'esearchresult': {'idlist': ['7955']}}
        returned_manifest = self.ncbi_queries.query_ncbi(self.fake_manifest)
        self.assertIsNone(returned_manifest.error_code)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_id_doesnt_match(self, mocked_search, mocked_url):
       self.fake_manifest.error_code = 1
       self.fake_manifest.taxon_id = '5597'
       mocked_search.return_value = {'esearchresult': {'idlist': ['7955']}}
       returned_manifest = self.ncbi_queries.query_ncbi(self.fake_manifest)
       self.assertEqual(returned_manifest.error_code, 3)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_id_not_found(self, mocked_search, mocked_url):
       self.fake_manifest.error_code = 1
       self.fake_manifest.taxon_id = '5597'
       mocked_search.return_value = {'esearchresult': {'idlist': ['7955', '7954']}}
       returned_manifest = self.ncbi_queries.query_ncbi(self.fake_manifest)
       self.assertEqual(returned_manifest.error_code, 2)

    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_not_found(self, mocked_search, mocked_url):
        self.fake_manifest.taxon_id = '7955'
        expected_common_name = 'Danio rerio'
        mocked_search.return_value = {'result': {'7955': {'scientificname': 'Danio rerio'}}}
        returned_manifest = self.ncbi_queries.query_ncbi(self.fake_manifest)
        self.assertEqual(returned_manifest.ncbi_common_name, expected_common_name)


    @patch('validation_components.spreadsheet_parsing.NcbiQuery.build_url')
    @patch('validation_components.spreadsheet_parsing.NcbiQuery.ncbi_search')
    def test_query_ncbi_name_found(self, mocked_search, mocked_url):
        self.fake_manifest.taxon_id = '7955'
        expected_common_name = 'unkown as the taxon ID is invalid'
        mocked_search.return_value = {'result': {'7955': {'error': 'Doesnt exist'}}}
        returned_manifest = self.ncbi_queries.query_ncbi(self.fake_manifest)
        self.assertEqual(returned_manifest.ncbi_common_name, expected_common_name)
