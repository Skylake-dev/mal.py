import unittest

import time
import sys
sys.path.append('..')
from mal.client import Client
from mal.enums import Field


class TestClient(unittest.TestCase):

    TOKEN: str = ''

    @classmethod
    def setUpClass(cls):
        with open('.env', 'r') as f:
            # .env file first line contains client_id=token
            cls.TOKEN = str(f.readline().split('=')[1].strip('\n\r '))

    @classmethod
    def tearDownClass(cls):
        cls.TOKEN = ''

    def setUp(self):
        self.client = Client(self.TOKEN)

    def test_limit(self):
        self.assertEqual(self.client.limit, 10)
        self.client.limit = 100
        self.assertEqual(self.client.limit, 100)
        with self.assertRaises(ValueError):
            self.client.limit = -10
        with self.assertRaises(ValueError):
            self.client.limit = 0
        # purposefully wrong values
        with self.assertRaises(ValueError):
            self.client.limit = 0.1  # type: ignore
        with self.assertRaises(ValueError):
            self.client.limit = "-10"   # type: ignore
        self.assertGreater(self.client.limit, 0)    # type: ignore

    def test_fields(self):
        self.assertEqual(self.client.anime_fields, Field.default_anime())
        # check that only fields of the correct type are accepted
        all_fields = [f for f in Field]
        # anime
        self.client.anime_fields = all_fields
        self.assertNotEqual(self.client.anime_fields, all_fields)
        self.assertTrue(all([f.is_anime for f in self.client.anime_fields]))
        # manga
        self.client.manga_fields = all_fields
        self.assertNotEqual(self.client.manga_fields, all_fields)
        self.assertTrue(all([f.is_manga for f in self.client.manga_fields]))

    def test_nsfw(self):
        with_nsfw = self.client.get_anime_list(
            'skylake_', status='completed', include_nsfw=True, limit=1000)
        no_nsfw = self.client.get_anime_list('skylake_', status='completed', limit=1000)
        self.assertTrue(len(with_nsfw) > len(no_nsfw))

    def test_pagination(self):
        # search term that yields many results so i can test pagination
        paginated_search = self.client.manga_search('kanojo', limit=2)
        self.assertIsNone(paginated_search.prev_page)
        next_page = self.client.next_page(paginated_search)
        self.assertIsNotNone(next_page)

    def test_pagination_offset(self):
        # using offsets, can go back in pages
        paginated_search_with_offset = self.client.manga_search('kanojo', limit=2, offset=2)
        previous_page = self.client.previous_page(paginated_search_with_offset)
        self.assertIsNotNone(previous_page)
        self.assertIsNone(self.client.previous_page(previous_page))  # type: ignore

    def test_delay(self):
        self.client.delay = 5.0
        start = time.time()
        self.client.get_anime(53887)
        self.client.get_anime(40357)
        end = time.time()
        self.assertTrue((end - start) > 5.0)

    def test_auto_truncation(self):
        self.client.auto_truncate = False
        # queries that are too long
        with self.assertRaises(ValueError):
            self.client.anime_search('b' * 100)
        with self.assertRaises(ValueError):
            self.client.manga_search('b' * 100)
        with self.assertRaises(ValueError):
            self.client.get_topics(query='b' * 400)
        # queries that are too short
        with self.assertRaises(ValueError):
            self.client.anime_search('b')
        with self.assertRaises(ValueError):
            self.client.manga_search('b')
        with self.assertRaises(ValueError):
            self.client.get_topics(query='b')
        # enable truncation
        self.client.auto_truncate = True
        # long queries are truncated and the operation is logged
        with self.assertLogs('mal.client', level='INFO'):
            self.client.anime_search('b' * 100)
        with self.assertLogs('mal.client', level='INFO'):
            self.client.manga_search('b' * 100)
        with self.assertLogs('mal.client', level='INFO'):
            self.client.get_topics(query='b' * 400)
        # short queries are unaffected
        with self.assertRaises(ValueError):
            self.client.anime_search('b')
        with self.assertRaises(ValueError):
            self.client.manga_search('b')
        with self.assertRaises(ValueError):
            self.client.get_topics(query='b')

    def test_argument_validation(self):
        with self.assertRaises(ValueError):
            self.client.get_anime_list('skylake_', status='invalid_status')
        with self.assertRaises(ValueError):
            self.client.get_manga_list('skylake_', status='invalid_status')
        with self.assertRaises(ValueError):
            self.client.get_seasonal_anime(2014, 'winter', sort='invalid_sort')
        with self.assertRaises(ValueError):
            self.client.get_seasonal_anime(2014, 'invalid_season')

    def test_logging(self):
        with self.assertLogs('mal.client', level='INFO'):
            self.client.anime_fields = Field.default_anime()
        with self.assertLogs('mal.client', level='INFO'):
            self.client.manga_fields = Field.default_manga()
        with self.assertLogs('mal.client', level='INFO'):
            self.client.character_fields = Field.default_character()
        with self.assertLogs('mal.client', level='INFO'):
            self.client.limit = 100
        # delay too short causes a warning
        with self.assertLogs('mal.client', level='WARNING'):
            self.client.delay = 0.1
        with self.assertLogs('mal.client', level='INFO'):
            self.client.delay = 2.0
        with self.assertLogs('mal.client', level='INFO'):
            self.client.auto_truncate = True
