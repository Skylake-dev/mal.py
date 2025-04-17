import unittest
import sys
from datetime import datetime
sys.path.append('..')
from mal.client import Client
from mal.enums import Field, AnimeRankingType
from mal.base import ReadOnlyIterable


class TestAnime(unittest.TestCase):

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
        # can test only info that don't change
        self.assertEqual(aot.id, 16498)
        self.assertEqual(aot.num_episodes, 25)
        self.assertFalse(aot.is_airing)
        self.assertFalse(aot.not_aired)
        self.assertTrue(aot.is_finished)
        self.assertIsNotNone(aot.main_picture_url)
        self.assertEqual(aot.start_season, 'spring 2013')
        self.assertEqual(aot.year, 2013)
        self.assertEqual(aot.source, 'manga')
        self.assertEqual(aot.average_episode_duration, 1440)
        self.assertEqual(aot.studios, 'Wit Studio')
        self.assertEqual(aot.broadcast_day, 'sunday')
        self.assertEqual(aot.broadcast_time, datetime.strptime('01:58', '%H:%M').time())
        stats = aot.statistics
        assert stats is not None   # for type checker
        self.assertEqual(stats.total_users, sum([stats.watching, stats.completed,
                         stats.plan_to_watch, stats.on_hold, stats.dropped]))

    def test_list(self):
        # if this fails then i have some error when parsing the payload
        anilist = self.client.get_anime_list('skylake_')
        self.assertIsInstance(anilist, ReadOnlyIterable)
        # check status and limit are handled correctly
        completed = self.client.get_anime_list('skylake_', limit=100, status='completed')
        self.assertEqual(len(completed), 100)
        for el in completed:
            self.assertEqual(el.list_status.status, 'completed')
        dropped = self.client.get_anime_list('skylake_', status='dropped')
        for el in dropped:
            self.assertEqual(el.list_status.status, 'dropped')
        plan_to_watch = self.client.get_anime_list('skylake_', status='plan_to_watch')
        for el in plan_to_watch:
            self.assertEqual(el.list_status.status, 'plan_to_watch')
        # check correct override and logic
        nsfw = self.client.get_anime_list('skylake_', status='completed')
        no_nsfw = self.client.get_anime_list('skylake_', status='completed', include_nsfw=False)
        self.assertGreater(len(nsfw), len(no_nsfw))
        for el in no_nsfw:
            self.assertEqual(el.entry.nsfw, 'white')

    # part of this test is commented out since this endpoint does not actually return
    # anime that started in that season (despite the field being called start_season...)
    # but all the anime that were airing in that period
    # TODO: i could verify that with a more complex check
    def test_seasonal(self):
        # test override of parameter
        season = self.client.get_seasonal_anime(2017, 'fall', limit=500, include_nsfw=False)
        self.assertEqual(len(season), 351)
        # for el in season:
        #     self.assertEqual(el.start_season, 'fall 2017')
        #     self.assertEqual(el.year, 2017)
        # now check all
        season = self.client.get_seasonal_anime(2017, 'fall', limit=500)
        self.assertEqual(len(season), 373)
        # for el in season:
        #     self.assertEqual(el.start_season, 'fall 2017')
        #     self.assertEqual(el.year, 2017)
        # limit is used correctly, overriding default behaviour
        season = self.client.get_seasonal_anime(2017, 'fall', limit=10)
        self.assertEqual(len(season), 10)
        # for el in season:
        #     self.assertEqual(el.start_season, 'fall 2017')
        #     self.assertEqual(el.year, 2017)

    def test_ranking(self):
        # if this fails then i have some error when parsing the payload
        airing = self.client.get_anime_ranking(ranking_type=AnimeRankingType.airing, limit=10)
        # limit is used correctly, overriding default behaviour
        self.assertEqual(len(airing), 10)
        for el in airing:
            self.assertEqual(airing[el].status, 'currently_airing')
