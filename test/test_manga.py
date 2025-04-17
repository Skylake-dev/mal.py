import unittest
import sys
from datetime import datetime
sys.path.append('..')
from mal.client import Client
from mal.enums import Field, MangaRankingType
from mal.base import ReadOnlyIterable


class TestManga(unittest.TestCase):

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

    def test_manga_parsing(self):
        # if this fails then i have some error when parsing the payload
        db = self.client.get_manga(42)
        # can test only info that don't change
        self.assertEqual(db.id, 42)
        self.assertEqual(db.num_chapters, 520)
        self.assertEqual(db.num_volumes, 42)
        self.assertFalse(db.is_publishing)
        self.assertFalse(db.is_discontinued)
        self.assertFalse(db.not_published)
        self.assertTrue(db.is_finished)
        self.assertIsNotNone(db.main_picture_url)
        self.assertEqual(db.media_type, 'manga')
        self.assertEqual(db.start_date, datetime.date(datetime.strptime('1984-11-20', '%Y-%m-%d')))
        self.assertEqual(db.end_date, datetime.date(datetime.strptime('1995-05-23', '%Y-%m-%d')))
        self.assertEqual(db.serialization, 'Shounen Jump (Weekly)')

    def test_list(self):
        # if this fails then i have some error when parsing the payload
        mangalist = self.client.get_manga_list('skylake_')
        self.assertIsInstance(mangalist, ReadOnlyIterable)
        # check status and limit are handled correctly
        completed = self.client.get_manga_list('skylake_', limit=3, status='completed')
        self.assertEqual(len(completed), 3)
        for el in completed:
            self.assertEqual(el.list_status.status, 'completed')
        dropped = self.client.get_manga_list('skylake_', status='dropped')
        for el in dropped:
            self.assertEqual(el.list_status.status, 'dropped')
        plan_to_read = self.client.get_manga_list('skylake_', status='plan_to_read')
        for el in plan_to_read:
            self.assertEqual(el.list_status.status, 'plan_to_read')
        # check correct override and logic
        nsfw = self.client.get_manga_list('skylake_')
        no_nsfw = self.client.get_manga_list('skylake_', include_nsfw=False)
        self.assertGreater(len(nsfw), len(no_nsfw))
        for el in no_nsfw:
            self.assertEqual(el.entry.nsfw, 'white')

    def test_ranking(self):
        # if this fails then i have some error when parsing the payload
        mangas = self.client.get_manga_ranking(ranking_type=MangaRankingType.manga, limit=10)
        # limit is used correctly, overriding default behaviour
        self.assertEqual(len(mangas), 10)
        for el in mangas:
            self.assertEqual(mangas[el].media_type, 'manga')
