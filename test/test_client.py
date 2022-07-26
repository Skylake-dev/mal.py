import unittest

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
