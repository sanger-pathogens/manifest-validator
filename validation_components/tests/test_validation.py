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
        esearch = True
        self.ncbi_queries.ncbi_search(self.fake_manifest, esearch)
        self.assertIn(unittest.mock.call().get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy'
                                               '&field=All%20Names&term=Danio rerio&retmode=json'),
                      mocked_session.mock_calls)

    @patch('requests.Session')
    def test_ncbi_search_with_taxon_id(self, mocked_session):
       esearch = False
       self.ncbi_queries.ncbi_search(self.fake_manifest, esearch)
       self.assertIn(unittest.mock.call().get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy'
                                              '&id=7955&retmode=json'), mocked_session.mock_calls)

    def test_query_ncbi_id_matches(self):
        pass

    def test_query_ncbi_id_doesnt_match(self):
        pass

    def test_query_ncbi_id_not_found(self):
        pass

    def test_query_ncbi_name_not_found(self):
        pass

    def test_query_ncbi_name_found(self):
        pass
