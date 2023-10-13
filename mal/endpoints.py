"""All the available endpoints of the MAL API v2, excluding the ones that
require user login to perform actions.
"""
from enum import Enum

BASE = 'https://api.myanimelist.net/v2'


class Endpoint(Enum):
    """Characterize the available endpoints. Each entry has two fields: url and limit.

    Attributes
        url: contains the url to the endpoint
        limit: contains the maximum value for the limit parameter for that endpoint.
    """
    ANIME = (BASE + '/anime', 100)
    ANIME_RANKING = (BASE + '/anime/ranking', 500)
    ANIME_SEASONAL = (BASE + '/anime/season', 500)

    MANGA = (BASE + '/manga', 100)
    MANGA_RANKING = (BASE + '/manga/ranking', 500)

    USER_ANIMELIST = (BASE + '/users/{username}/animelist', 1000)
    USER_MANGALIST = (BASE + '/users/{username}/mangalist', 1000)

    FORUM_BOARDS = (BASE + '/forum/boards', 100)
    FORUM_TOPICS = (BASE + '/forum/topics', 100)
    FORUM_TOPIC_DETAIL = (BASE + '/forum/topic', 100)

    def __init__(self, url: str, limit: int) -> None:
        self.url: str = url
        self.limit: int = limit

    def __str__(self) -> str:
        return self.url

    @property
    def is_anime(self) -> bool:
        if 'anime' in self.url:
            return True
        return False

    @property
    def is_manga(self) -> bool:
        if 'manga' in self.url:
            return True
        return False

    @property
    def is_list(self) -> bool:
        if 'list' in self.url:
            return True
        return False

    @property
    def is_forum(self) -> bool:
        if 'forum' in self.url:
            return True
        return False
