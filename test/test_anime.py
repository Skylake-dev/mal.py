import unittest
import sys
sys.path.append('..')
from mal.client import Client
from mal.enums import Field


class TestBase(unittest.TestCase):

    client: Client

    @classmethod
    def setUpClass(cls):
        with open('.env', 'r') as f:
            # .env file first line contains client_id=token
            token = str(f.readline().split('=')[1].strip('\n\r '))
        cls.client = Client(token)
        cls.client.anime_fields = Field.all_anime()
        cls.client.manga_fields = Field.all_manga()
        cls.client.limit = 1000
        cls.client.include_nsfw = True

    def test_parsing(self):
        # if this fails then i have some error when parsing the payload
        aot = self.client.get_anime(16498)
        self.assertEqual(aot.id, 16498)
        self.assertFalse(aot.is_airing)
        self.assertFalse(aot.not_aired)
        self.assertTrue(aot.is_finished)
        self.assertIsNotNone(aot.main_picture_url)
        self.assertEqual(aot.start_season, 'spring 2013')
        stats = aot.statistics
        assert stats is not None   # for type checker
        self.assertEqual(stats.total_users, sum([stats.watching, stats.completed,
                         stats.plan_to_watch, stats.on_hold, stats.dropped]))
