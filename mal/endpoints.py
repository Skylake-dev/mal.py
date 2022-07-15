"""All the available endpoints of the MAL API v2, excluding the ones that
require user login to perform actions.
"""
from enum import Enum

BASE = 'https://api.myanimelist.net/v2'


class Endpoint(Enum):
    """Characterize the available endpoints. Each entry has two fields: url and limit.

    Attributes
        url: contains the url to the endpoint
        limit: optional, contains the maximum value for the limit parameter for that endpoint.
    """
    ANIME = (BASE + '/anime', 100)
    ANIME_RANKING = (BASE + '/anime/ranking', 500)
    ANIME_SEASONAL = (BASE + '/anime/season', 500)
    ANIME_SUGGESTIONS = (BASE + '/anime/suggestions', 100)

    MANGA = (BASE + '/manga', 100)
    MANGA_RANKING = (BASE + '/manga/ranking', 500)

    USER = (BASE + '/users', None)
    # replace {username} before using
    USER_ANIMELIST = (BASE + '/users/{username}/animelist', 1000)
    USER_MANGALIST = (BASE + '/users/{username}/mangalist', 1000)

    FORUM_BOARDS = (BASE + '/forum/boards', None)
    FORUM_TOPICS = (BASE + '/forum/topics', 100)
    FORUM_TOPIC_DETAIL = (BASE + '/forum/topic', 100)

    def __init__(self, url: str, limit: int) -> None:
        self.url: str = url
        self.limit: int = limit

    def __str__(self) -> str:
        return self.url

    @property
    def is_anime(self) -> bool:
        anime_endpoints = [
            self.ANIME,
            self.ANIME_RANKING,
            self.ANIME_SEASONAL,
            self.ANIME_SUGGESTIONS,
            self.USER_ANIMELIST
        ]
        return self in anime_endpoints

    @property
    def is_manga(self) -> bool:
        manga_endpoints = [
            self.MANGA,
            self.MANGA_RANKING,
            self.USER_MANGALIST
        ]
        return self in manga_endpoints

    @property
    def is_list(self) -> bool:
        list_endpoints = [
            self.USER_ANIMELIST,
            self.USER_MANGALIST
        ]
        return self in list_endpoints

    @property
    def is_forum(self) -> bool:
        forum_endpoints = [
            self.FORUM_BOARDS,
            self.FORUM_TOPIC_DETAIL,
            self.FORUM_TOPICS
        ]
        return self in forum_endpoints