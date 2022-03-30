from datetime import datetime, time
from typing import List, Iterator, Optional

from .utils import MISSING
from .enums import AdaptationFrom, AnimeStatus, AnimeMediaType, AnimeListStatus
from .base import Result, UserListEntry, UserList, ListStatus
from .typed import (
    AnimePayload,
    AnimeSearchPayload,
    GenericPayload,
    SeasonPayload,
    AnimeListEntryPayload,
    AnimeListPayload,
    AnimeListEntryStatusPayload
)


class Anime(Result):
    """Represents a full Anime object with all the possible fields.
    If some fields were excluded from the query then None or a default value
    will be returned for those, see description of each field.

    Attributes:
        status: current publication status, None if not requested
        media_type: the type of anime, None if not requested
        num_episodes: number of episodes
        broadcast_day: day of the week when the episodes are broadcasted
        broadcast_time: time of the day of the broadcasting
        source: from where the anime was adapted or if it is an original, None if not requested
        average_episode_duration: duration of the episodes in seconds
        rating: pg rating of the anime
    """

    def __init__(self, payload: AnimePayload):
        """Creates an Anime object from the received json data."""
        super().__init__(payload)
        _status = payload.get('status')
        self.status: Optional[AnimeStatus] = AnimeStatus(
            _status) if _status else None
        _media_type = payload.get('media_type')
        self.media_type: Optional[AnimeMediaType] = AnimeMediaType(
            _media_type) if _media_type else None
        self.num_episodes: int = payload.get('num_episodes', 0)
        _broadcast_info = payload.get('broadcast', MISSING)
        if _broadcast_info is not MISSING:
            self.broadcast_day: str = _broadcast_info['day_of_the_week']
            self.broadcast_time: time = datetime.strptime(
                _broadcast_info['start_time'], '%H:%M').time()
        else:
            self.broadcast_day: str = 'not requested'
            self.broadcast_time: time = datetime.strptime(
                '00:00', '%H:%M').time()
        _source = payload.get('source')
        self.source: Optional[AdaptationFrom] = AdaptationFrom(
            _source) if _source else None
        self.average_episode_duration: int = payload.get(
            'average_episode_duration', 0)
        self.rating: str = payload.get('rating', 'not requested')
        self._studios: List[GenericPayload] = payload.get('studios', [])
        self._start_season: SeasonPayload = payload.get(
            'start_season', MISSING)

    @property
    def start_season(self) -> str:
        if self._start_season is not MISSING:
            season = self._start_season['season']
            year = self._start_season['year']
            return f'{season} {year}'
        else:
            return 'information not requested or unavailable'

    @property
    def studios(self) -> str:
        return ', '.join(studio['name'] for studio in self._studios)


class AnimeSearchResults:
    """Container for anime search results."""

    def __init__(self, data: AnimeSearchPayload) -> None:
        self._results: List[Anime] = []
        for el in data['data']:
            self._results.append(Anime(el['node']))

    def __iter__(self) -> Iterator[Anime]:
        return iter(self._results)

    def __str__(self) -> str:
        return '\n'.join([str(result) for result in self._results])


class AnimeListEntryStatus(ListStatus):
    def __init__(self, data: AnimeListEntryStatusPayload) -> None:
        super().__init__(data)
        self.status: AnimeListStatus = AnimeListStatus(data.get('status'))
        self.num_episodes_watched: int = data.get('num_episodes_watched', 0)
        self.is_rewatching: bool = data.get('is_rewatching', False)
        self.num_times_rewatched: int = data.get('num_times_rewatched', 0)
        self.rewatch_value: int = data.get('rewatch_value', 0)

    @property
    def completed(self) -> bool:
        return self.status is AnimeListStatus('completed')


class AnimeListEntry(UserListEntry):
    def __init__(self, data: AnimeListEntryPayload) -> None:
        super().__init__(data)
        self.entry: Anime = Anime(data['node'])
        self.list_status: AnimeListEntryStatus = AnimeListEntryStatus(
            data['list_status'])


class AnimeList(UserList):
    def __init__(self, data: AnimeListPayload) -> None:
        super().__init__(data)
        self._list: List[AnimeListEntry] = []
        for item in data['data']:
            self._list.append(AnimeListEntry(item))

    def __iter__(self) -> Iterator[AnimeListEntry]:
        return iter(self._list)
