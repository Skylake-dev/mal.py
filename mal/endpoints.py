"""All the available endpoints of the MAL API v2, excluding the ones that
require user login to perform actions.
"""
from enum import Enum, IntFlag

BASE = 'https://api.myanimelist.net/v2'


class EndpointType(IntFlag):
    ANIME = 1
    MANGA = 2
    LIST = 4
    FORUM = 8


class Endpoint(Enum):
    """Characterize the available endpoints. Each entry has two fields: url and limit.

    Attributes
        url: contains the url to the endpoint
        limit: contains the maximum value for the limit parameter for that endpoint.
    """
    ANIME = (BASE + '/anime', 100, EndpointType.ANIME)
    ANIME_RANKING = (BASE + '/anime/ranking', 500, EndpointType.ANIME)
    ANIME_SEASONAL = (BASE + '/anime/season', 500, EndpointType.ANIME)

    MANGA = (BASE + '/manga', 100, EndpointType.MANGA)
    MANGA_RANKING = (BASE + '/manga/ranking', 500, EndpointType.MANGA)

    USER_ANIMELIST = (BASE + '/users/{username}/animelist',
                      1000, EndpointType.LIST | EndpointType.ANIME)
    USER_MANGALIST = (BASE + '/users/{username}/mangalist',
                      1000, EndpointType.LIST | EndpointType.MANGA)

    FORUM_BOARDS = (BASE + '/forum/boards', 100, EndpointType.FORUM)
    FORUM_TOPICS = (BASE + '/forum/topics', 100, EndpointType.FORUM)
    FORUM_TOPIC_DETAIL = (BASE + '/forum/topic', 100, EndpointType.FORUM)

    def __init__(self, url: str, limit: int, endpoint_type: EndpointType) -> None:
        self.url: str = url
        self.limit: int = limit
        self._type: EndpointType = endpoint_type

    def __str__(self) -> str:
        return self.url

    @property
    def is_anime(self) -> bool:
        return EndpointType.ANIME in self._type

    @property
    def is_manga(self) -> bool:
        return EndpointType.MANGA in self._type

    @property
    def is_list(self) -> bool:
        return EndpointType.LIST in self._type

    @property
    def is_forum(self) -> bool:
        return EndpointType.FORUM in self._type
