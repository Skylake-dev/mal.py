from __future__ import annotations
from datetime import datetime, time
from typing import Dict, List, Iterator, Optional, Sequence, Union

from .connection import APICallManager
from .utils import MISSING
from .endpoints import Endpoint
from .enums import AdaptationFrom, AnimeStatus, AnimeMediaType, AnimeListStatus, AnimeRankingType, Field
from .base import Result, UserListEntry, UserList, ListStatus, Ranking, PaginatedObject
from .typed import (
    AnimePayload,
    AnimeSearchPayload,
    GenericPayload,
    SeasonPayload,
    AnimeListEntryPayload,
    AnimeListPayload,
    AnimeListEntryStatusPayload,
    AnimeRankingPayload,
    SeasonalAnimePayload,
    MusicPayload,
    StatisticsPayload
)


class Song:
    """Represents a single song for an anime

    Attributes:
        id: the id of this song in the MAL database
        description: string containing title author and episodes where this
            theme was used
    """

    def __init__(self, data: MusicPayload) -> None:
        self.id: int = data['id']
        self.description: str = data['text']

    def __str__(self) -> str:
        return f'{self.id} - {self.description}'


class Music:
    """Represents opening or ending themes for an anime.
    Iterate over this to get all songs.
    """

    def __init__(self, data: Sequence[MusicPayload]) -> None:
        self._data: List[Song] = []
        for song in data:
            self._data.append(Song(song))

    def __iter__(self) -> Iterator[Song]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return '\n'.join(str(song) for song in self._data)


class Statistics:
    """Current statistics for this anime.

    Attributes:
        watching: number of people who have this title marked as 'watching'
        completed: number of people who have this title marked as 'completed'
        on_hold: number of people who have this title marked as 'on_hold'
        dropped: number of people who have this title marked as 'dropped'
        plan_to_watch: number of people who have this title marked as 'plan_to_watch'
        total_users: total number of people who have this title in their list and it
            is equal to the sum of all the other attributes
    """

    def __init__(self, data: StatisticsPayload) -> None:
        self.watching: int = int(data['status']['watching'])
        self.completed: int = int(data['status']['completed'])
        self.on_hold: int = int(data['status']['on_hold'])
        self.dropped: int = int(data['status']['dropped'])
        self.plan_to_watch: int = int(data['status']['plan_to_watch'])
        self.total_users: int = int(data['num_list_users'])

    def __str__(self) -> str:
        values = vars(self)
        return '\n'.join(f'{attr}: {values[attr]}' for attr in values)


class Anime(Result):
    """Represents a full Anime object with all the possible fields.
    If some fields were excluded from the query then None or a default value
    will be returned for those, see description of each field.

    Attributes:
        status: current publication status, None if not requested or missing
        media_type: the type of anime, None if not requested or missing
        num_episodes: number of episodes
        broadcast_day: day of the week when the episodes are broadcasted
        broadcast_time: time of the day of the broadcasting
        source: from where the anime was adapted or if it is an original, None if not requested or missing
        average_episode_duration: duration of the episodes in seconds
        rating: pg rating of the anime
        openings: opening themes used for this anime, None if not requested or missing
        endings: ending themes used for this anime, None if not requested or missing
        statistics: information about how many people have completed this, watching, etc, None
            if not requested or missing
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, payload: AnimePayload, api_call_manager: APICallManager):
        """Creates an Anime object from the received json data."""
        super().__init__(payload, api_call_manager)
        self._load_data(payload)

    @property
    def start_season(self) -> str:
        """The starting season, for example 'spring 2016'."""
        if self._start_season is not MISSING:
            season = self._start_season['season']
            year = self._start_season['year']
            return f'{season} {year}'
        else:
            return 'information not requested or missing'

    @property
    def studios(self) -> str:
        """All the studios that were involved in the production."""
        return ', '.join(studio['name'] for studio in self._studios)

    @property
    def is_airing(self) -> bool:
        """Returns True if the anime is currently airing, False otherwise."""
        return self.status == AnimeStatus.airing

    @property
    def is_finished(self) -> bool:
        """Returns True if the anime is finished, False otherwise."""
        return self.status == AnimeStatus.finished

    @property
    def not_aired(self) -> bool:
        """Returns True if the anime has not yet aired, False otherwise."""
        return self.status == AnimeStatus.not_aired

    @property
    def url(self) -> str:
        """URL to the MAL page for this anime."""
        return f'https://myanimelist.net/anime/{self.id}'

    @property
    def api_url(self) -> str:
        """URL to request this title from the MAL API."""
        return f'{Endpoint.ANIME}/{self.id}'

    def load_fields(self, *, fields: Sequence[Union[str, Field]] = MISSING) -> None:
        # NOTE: maybe check if fields are for anime?
        payload = super().load_fields(fields=fields)
        self._load_data(payload)

    def _load_data(self, payload: AnimePayload) -> None:
        """Populate all attributes, for internal use."""
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
            # start_time can be missing
            self.broadcast_time: time = datetime.strptime(
                _broadcast_info.get('start_time', '00:00'), '%H:%M').time()
        else:
            self.broadcast_day: str = 'not requested or missing'
            self.broadcast_time: time = datetime.strptime(
                '00:00', '%H:%M').time()
        _source = payload.get('source')
        self.source: Optional[AdaptationFrom] = AdaptationFrom(
            _source) if _source else None
        self.average_episode_duration: int = payload.get(
            'average_episode_duration', 0)
        self.rating: str = payload.get('rating', 'not requested or missing')
        self._studios: Sequence[GenericPayload] = payload.get('studios', [])
        self._start_season: SeasonPayload = payload.get(
            'start_season', MISSING)
        _openings = payload.get('opening_themes')
        self.openings: Optional[Music] = Music(
            _openings) if _openings else None
        _endings = payload.get('ending_themes')
        self.endings: Optional[Music] = Music(
            _endings) if _endings else None
        _stats = payload.get('statistics')
        self.statistics: Optional[Statistics] = Statistics(
            _stats) if _stats else None
        self.raw: AnimePayload = payload


class AnimeSearchResults(PaginatedObject):
    """Container for anime search results. Iterable and printable.

    Attributes:
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, data: AnimeSearchPayload, api_call_manager: APICallManager) -> None:
        super().__init__(data, api_call_manager)
        self._results: List[Anime] = []
        for el in data['data']:
            self._results.append(Anime(el['node'], api_call_manager))
        self.raw: AnimeSearchPayload = data

    def __iter__(self) -> Iterator[Anime]:
        return iter(self._results)

    def __len__(self) -> int:
        return len(self._results)

    def __str__(self) -> str:
        return '\n'.join([str(result) for result in self._results])


class AnimeListEntryStatus(ListStatus):
    """Represents the status for an entry in a user anime list.
    Note that since this is marked by the user it can be inconsistent,
    for example can be marked as completed even if the anime is not yet finished.

    Attributes:
        status: completed, plan_to_watch, etc
        num_episodes_watched: number of episodes that the user has seen so far
        is_rewatching: whether the user is rewatching this series
        num_times_rewatched: number of times the user has rewatched the series
        rewatch_value: integer number quantifying the rewatch value
    """

    def __init__(self, data: AnimeListEntryStatusPayload) -> None:
        super().__init__(data)
        self.status: AnimeListStatus = AnimeListStatus(data.get('status'))
        self.num_episodes_watched: int = data.get('num_episodes_watched', 0)
        self.is_rewatching: bool = data.get('is_rewatching', False)
        self.num_times_rewatched: int = data.get('num_times_rewatched', 0)
        self.rewatch_value: int = data.get('rewatch_value', 0)

    def __str__(self) -> str:
        if self.is_rewatching:
            s = f'Status: {self.status} (rewatching)\n'
        else:
            s = f'Status: {self.status}\n'
        if self.score != 0:
            s += f' - scored: {self.score}\n'
        if self.num_episodes_watched != 0:
            s += f' - episodes watched: {self.num_episodes_watched}\n'
        return s

    @property
    def completed(self) -> bool:
        """True if the user has marked this series as completed."""
        return self.status is AnimeListStatus.completed


class AnimeListEntry(UserListEntry):
    """Represents a row in the anime list.

    Attributes:
        entry: the anime of this entry
        list_status: all the information about the status
    """

    def __init__(self, data: AnimeListEntryPayload, api_call_manager: APICallManager) -> None:
        self.entry: Anime = Anime(data['node'], api_call_manager)
        self.list_status: AnimeListEntryStatus = AnimeListEntryStatus(
            data['list_status'])

    def __str__(self) -> str:
        return f'{self.entry.title} - {str(self.list_status)}'


class AnimeList(UserList):
    """Iterable object containing the anime list of a user."""

    def __init__(self, data: AnimeListPayload, api_call_manager: APICallManager) -> None:
        super().__init__(data, api_call_manager)
        self.raw: AnimeListPayload = data
        self._list: List[AnimeListEntry] = []
        for item in data['data']:
            self._list.append(AnimeListEntry(item, api_call_manager))
        self.average_score: float = self._compute_average_score()

    def __iter__(self) -> Iterator[AnimeListEntry]:
        return iter(self._list)

    def __len__(self) -> int:
        return super().__len__()

    def __str__(self) -> str:
        return super().__str__()


class AnimeRanking(Ranking):
    """Container for anime rankings.

    Attributes:
        type: the criterion of this ranking
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, data: AnimeRankingPayload, api_call_manager: APICallManager) -> None:
        super().__init__(data, api_call_manager)
        self._ranking: Dict[int, Anime] = {}
        for node in data['data']:
            self._ranking[node['ranking']['rank']] = Anime(
                node['node'], api_call_manager)
        self.raw: AnimeRankingPayload = data
        if self._type is not MISSING:
            self._type: AnimeRankingType = AnimeRankingType(self._type)

    @property
    def type(self) -> AnimeRankingType:
        return self._type

    @type.setter
    def type(self, type: Union[str, AnimeRankingType]) -> None:
        if isinstance(type, str):
            type = AnimeRankingType(type)
        self._type = type

    def __iter__(self) -> Iterator[int]:
        return super().__iter__()

    def __len__(self) -> int:
        return super().__len__()

    def __str__(self) -> str:
        return super().__str__()

    def get(self, rank: int) -> Anime:
        """Returns the entry corresponding to the given rank.

        Args:
            rank: the rank of the entry to get

        Raises:
            KeyError: the rank is not present
        """
        return self._ranking[rank]


class Seasonal(PaginatedObject):
    """Container for seasonal anime searches.

    Attributes:
        year: the year of this season
        season: which season was requested
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, data: SeasonalAnimePayload, api_call_manager: APICallManager) -> None:
        super().__init__(data, api_call_manager)
        self._list: List[Anime] = []
        for item in data['data']:
            self._list.append(Anime(item['node'], api_call_manager))
        self.year: int = data['season']['year']
        self.season: str = data['season']['season']
        self.raw: SeasonalAnimePayload = data

    def __str__(self) -> str:
        s = f'{self.season} {self.year} anime:\n'
        s += '\n'.join([str(anime) for anime in self._list])
        return s

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self) -> Iterator[Anime]:
        return iter(self._list)

    @property
    def season_info(self) -> str:
        """Information about the season."""
        return f'{self.season} {self.year}, {len(self._list)} anime'
