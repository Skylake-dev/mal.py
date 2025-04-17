from __future__ import annotations
from typing import Dict, List, Iterator, Optional, Union

from .endpoints import Endpoint
from .utils import MISSING
from .enums import MangaStatus, MangaMediaType, MangaListStatus, MangaRankingType
from .base import Result, ListStatus, UserListEntry, UserList, Ranking, PaginatedObject, ReadOnlyIterable
from .typed import (
    AuthorPayload,
    GenericPayload,
    MangaPayload,
    MangaSearchPayload,
    MangaListEntryPayload,
    MangaListEntryStatusPayload,
    MangaListPayload,
    MangaRankingPayload
)


class Author:
    """Represents an author for a manga.

    Attributes:
        id: the id in the MAL database
        first_name: the first name of the author
        last_name: the last name of the author
        role: the role that the author has
    """

    def __init__(self, data: AuthorPayload) -> None:
        person = data['node']
        self.id: int = person.get('id', 0)
        self.first_name: str = person.get('first_name', 'unknown')
        self.last_name: str = person.get('last_name', 'unknown')
        self.role: str = data['role']

    def __str__(self) -> str:
        return f'{self.full_name} - {self.role}'

    @property
    def full_name(self):
        """Returns the full name of the author if available."""
        return f'{self.first_name} {self.last_name}'


class Manga(Result):
    """Represents a full Manga object with all the possible fields.
    If some fields were excluded from the query then None or a default value
    will be returned for those, see description of each field.

    Attributes:
        status: current publication status, None if not requested or missing
        media_type: the type of manga, None if not requested or missing
        authors: list of authors that created the manga
        num_chapters: the number of chapters in total, 0 if not completed
        num_volumes: the number of volumes in total, 0 if not completed
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, payload: MangaPayload) -> None:
        """Creates an Manga object from the received json data."""
        super().__init__(payload)
        self._load_data(payload)

    @property
    def serialization(self):
        """Magazines or other formats where the series is published."""
        return ', '.join(mag['name'] for mag in self._serialization)

    @property
    def is_publishing(self) -> bool:
        """Returns True if the manga is currently publishing, False otherwise."""
        return self.status == MangaStatus.publishing

    @property
    def is_finished(self) -> bool:
        """Returns True if the manga is finished, False otherwise."""
        return self.status == MangaStatus.finished

    @property
    def not_published(self) -> bool:
        """Returns True if the manga has not yet published, False otherwise."""
        return self.status == MangaStatus.not_published

    @property
    def is_discontinued(self) -> bool:
        """Returns True if the manga is discontinued, False otherwise."""
        return self.status == MangaStatus.discontinued

    @property
    def on_hiatus(self) -> bool:
        """Returns True if the manga is on hiatus, False otherwise."""
        return self.status == MangaStatus.on_hiatus

    @property
    def url(self) -> str:
        """URL to the MAL page for this manga."""
        return f'https://myanimelist.net/manga/{self.id}'

    @property
    def api_url(self) -> str:
        """URL to request this title from the MAL API."""
        return f'{Endpoint.MANGA}/{self.id}'

    def _load_data(self, payload: MangaPayload) -> None:
        """Populate all attributes, for internal use."""
        _status = payload.get('status')
        self.status: Optional[MangaStatus] = MangaStatus(
            _status) if _status else None
        _media_type = payload.get('media_type')
        self.media_type: Optional[MangaMediaType] = MangaMediaType(
            _media_type) if _media_type else None
        self.authors: List[Author] = []
        _authors = payload.get('authors', [])
        for author in _authors:
            self.authors.append(Author(author))
        self.num_chapters: int = payload.get('num_chapters', 0)
        self.num_volumes: int = payload.get('num_volumes', 0)
        self._serialization: List[GenericPayload] = []
        _magazines = payload.get('serialization', [])
        for magazine in _magazines:
            self._serialization.append(magazine['node'])
        self.raw: MangaPayload = payload


class MangaSearchResults(PaginatedObject, ReadOnlyIterable[Manga]):
    """Container for manga search results. Iterable and printable.

    Attributes:
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, data: MangaSearchPayload) -> None:
        super().__init__(data)
        self.results: List[Manga] = []
        # satisfy the ReadOnlyProtocol structure
        self._list = self.results
        for el in data['data']:
            self.results.append(Manga(el['node']))
        self.raw: MangaSearchPayload = data


class MangaListEntryStatus(ListStatus):
    """Represents the status for an entry in a user manga list.
    Note that since this is marked by the user it can be inconsistent,
    for example can be marked as completed even if the manga is not yet finished.

    Attributes:
        status: completed, plan_to_watch, etc
        num_volumes_read: number of volumes that the user has read so far
        num_chapters_read: number of chapters that the user has read so far
        is_rereading: whether the user is rereading this series
        num_times_reread: number of times the user has reread the series
        rewatch_value: integer number quantifying the rewatch value
    """

    def __init__(self, data: MangaListEntryStatusPayload) -> None:
        super().__init__(data)
        self.status: MangaListStatus = MangaListStatus(data.get('status'))
        self.num_volumes_read: int = data.get('num_volumes_read', 0)
        self.num_chapters_read: int = data.get('num_chapters_read', 0)
        self.is_rereading: bool = data.get('is_rereading', False)
        self.num_times_reread: int = data.get('num_times_reread', 0)
        self.rewatch_value: int = data.get('rewatch_value', 0)

    def __str__(self) -> str:
        if self.is_rereading:
            s = f'Status: {self.status} (rereading)\n'
        else:
            s = f'Status: {self.status}\n'
        if self.score != 0:
            s += f' - scored: {self.score}\n'
        if self.num_chapters_read != 0:
            s += f' - chapters read: {self.num_chapters_read}\n'
        return s

    @property
    def completed(self) -> bool:
        """True if the user has marked this series as completed."""
        return self.status is MangaListStatus('completed')


class MangaListEntry(UserListEntry):
    """Represents a row in the manga list.

    Attributes:
        entry: the manga of this entry
        list_status: all the information about the status
    """

    def __init__(self, data: MangaListEntryPayload) -> None:
        self.entry: Manga = Manga(data['node'])
        self.list_status: MangaListEntryStatus = MangaListEntryStatus(
            data['list_status'])

    def __str__(self) -> str:
        return f'{self.entry.title} - {str(self.list_status)}'


class MangaList(UserList, ReadOnlyIterable[MangaListEntry]):
    """Iterable object containing the manga list of a user. Directly iterate over this
    object to retrieve the entries.

    Attributes:
        entries: list with all the entries
        raw: The raw json data for this object as returned by the API
    """

    def __init__(self, data: MangaListPayload) -> None:
        super().__init__(data)
        self.raw: MangaListPayload = data
        self.entries: List[MangaListEntry] = []
        # satisfy the ReadOnlyProtocol structure
        self._list = self.entries
        for item in data['data']:
            self.entries.append(MangaListEntry(item))
        self.average_score: float = self._compute_average_score()

    def __str__(self) -> str:
        return super().__str__()


class MangaRanking(Ranking):
    """Container for manga rankings.

    Attributes:
        type: the criterion of this ranking
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, data: MangaRankingPayload) -> None:
        super().__init__(data)
        self._ranking: Dict[int, Manga] = {}
        for node in data['data']:
            self._ranking[node['ranking']['rank']] = Manga(
                node['node'])
        self.raw: MangaRankingPayload = data
        if self._type is not MISSING:
            self._type: MangaRankingType = MangaRankingType(self._type)

    @property
    def type(self) -> MangaRankingType:
        return self._type

    @type.setter
    def type(self, type: Union[str, MangaRankingType]) -> None:
        if isinstance(type, str):
            type = MangaRankingType(type)
        self._type = type

    def __iter__(self) -> Iterator[int]:
        return super().__iter__()

    def __len__(self) -> int:
        return super().__len__()

    def __getitem__(self, idx: int) -> Manga:
        return self._ranking[idx]

    def __str__(self) -> str:
        return super().__str__()

    def get(self, rank: int) -> Manga:
        """Returns the entry corresponding to the given rank.

        Args:
            rank: the rank of the entry to get

        Raises:
            KeyError: the rank is not present
        """
        return self._ranking[rank]
