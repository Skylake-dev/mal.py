from mal.endpoints import Endpoint
import unittest
import sys
sys.path.append('..')


class TestEnums(unittest.TestCase):

    def test_type(self):
        # this is very verbose and probably there is a better way but it's better
        # to check all possibilities
        # ANIME
        self.assertTrue(Endpoint.ANIME.is_anime)
        self.assertFalse(Endpoint.ANIME.is_manga)
        self.assertFalse(Endpoint.ANIME.is_list)
        self.assertFalse(Endpoint.ANIME.is_forum)
        self.assertTrue(Endpoint.ANIME_RANKING.is_anime)
        self.assertFalse(Endpoint.ANIME_RANKING.is_manga)
        self.assertFalse(Endpoint.ANIME_RANKING.is_list)
        self.assertFalse(Endpoint.ANIME_RANKING.is_forum)
        self.assertTrue(Endpoint.ANIME_SEASONAL.is_anime)
        self.assertFalse(Endpoint.ANIME_SEASONAL.is_manga)
        self.assertFalse(Endpoint.ANIME_SEASONAL.is_list)
        self.assertFalse(Endpoint.ANIME_SEASONAL.is_forum)
        # MANGA
        self.assertTrue(Endpoint.MANGA.is_manga)
        self.assertFalse(Endpoint.MANGA.is_anime)
        self.assertFalse(Endpoint.MANGA.is_list)
        self.assertFalse(Endpoint.MANGA.is_forum)
        self.assertTrue(Endpoint.MANGA_RANKING.is_manga)
        self.assertFalse(Endpoint.MANGA_RANKING.is_anime)
        self.assertFalse(Endpoint.MANGA_RANKING.is_list)
        self.assertFalse(Endpoint.MANGA_RANKING.is_forum)
        # LIST
        self.assertTrue(Endpoint.USER_ANIMELIST.is_list)
        self.assertTrue(Endpoint.USER_ANIMELIST.is_anime)
        self.assertFalse(Endpoint.USER_ANIMELIST.is_manga)
        self.assertFalse(Endpoint.USER_ANIMELIST.is_forum)
        self.assertTrue(Endpoint.USER_MANGALIST.is_list)
        self.assertTrue(Endpoint.USER_MANGALIST.is_manga)
        self.assertFalse(Endpoint.USER_MANGALIST.is_anime)
        self.assertFalse(Endpoint.USER_MANGALIST.is_forum)
        # FORUM
        self.assertTrue(Endpoint.FORUM_BOARDS.is_forum)
        self.assertFalse(Endpoint.FORUM_BOARDS.is_anime)
        self.assertFalse(Endpoint.FORUM_BOARDS.is_manga)
        self.assertFalse(Endpoint.FORUM_BOARDS.is_list)
        self.assertTrue(Endpoint.FORUM_TOPICS.is_forum)
        self.assertFalse(Endpoint.FORUM_TOPICS.is_anime)
        self.assertFalse(Endpoint.FORUM_TOPICS.is_manga)
        self.assertFalse(Endpoint.FORUM_TOPICS.is_list)
        self.assertTrue(Endpoint.FORUM_TOPIC_DETAIL.is_forum)
        self.assertFalse(Endpoint.FORUM_TOPIC_DETAIL.is_anime)
        self.assertFalse(Endpoint.FORUM_TOPIC_DETAIL.is_manga)
        self.assertFalse(Endpoint.FORUM_TOPIC_DETAIL.is_list)
