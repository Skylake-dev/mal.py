"""Contains the definitions for the base classes used in other modules."""
from __future__ import annotations

import logging
from datetime import datetime, date
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union

from .connection import APICallManager
from .utils import MISSING
from .titles import Titles
from .enums import NSFWlevel
from .genre import Genre
from .typed import (
    BaseResultPayload,
    ResultPayload,
    PicturePayload,
    RelationPayload,
    RecommendationPayload,
    ListStatusPayload,
    ListEntryPayload,
    AnimeListPayload,
    MangaListPayload,
    RankingPayload,
    PaginatedPayload
)

_log = logging.getLogger(__name__)

from collections.abc import Iterable, Sized
from typing import TypeVar, Protocol, runtime_checkable

T = TypeVar('T')


@runtime_checkable
class ReadOnlyIterable(Iterable[T], Sized, Protocol[T]):
    """Base class for all the objects supporting iteration. This is widely
    used throughout the library for objects returning list of values.

    Objects implementing this protocol offer the following functionality:
    - can be iterated over directly (i.e. use in a for)
    - have a size (i.e. can use `len` on them to get number of elements)
    - access elements with subscript (e.g. a[0]). do not support slices
    - default __str__ and __repr__ methods
    """
    _list: List[T]

    def __iter__(self) -> Iterator[T]:
        return iter(self._list)

    def __len__(self) -> int:
        return len(self._list)

    def __getitem__(self, idx: int) -> T:
        return self._list[idx]

    def __str__(self) -> str:
        return '\n'.join(str(el for el in self._list))

    def __repr__(self) -> str:
        return self.__str__()


class PaginatedObject:
    """Base class for results that can consist of multiple pages. Implements the method
    to request the next page.
    """

    def __init__(self, data: PaginatedPayload) -> None:
        paging = data['paging']
        self.prev_page: Optional[str] = paging['previous'] if 'previous' in paging else None
        self.next_page: Optional[str] = paging['next'] if 'next' in paging else None


class BaseResult:
    """Represents the base for an Anime or Manga objects. This fields are always returned
    by the API no matter the fields that are requested.

    Attributes:
        id: the id of the result
            NOTE: this is not unique for each object only between objects of the same category
            for example, all anime have different id but an anime and a manga can have same id
        titles: Titles object for title information.
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, payload: BaseResultPayload) -> None:
        """Creates an Anime object from the received json data."""
        self.id: int = payload['id']
        self.titles: Titles = Titles(payload['title'], MISSING)
        self._main_picture: PicturePayload = payload.get(
            'main_picture', MISSING)
        self.raw: Any = payload

    def __int__(self) -> int:
        return self.id

    def __str__(self) -> str:
        return self.title

    @property
    def title(self) -> str:
        """Title of the result. Shorthand for result.titles.title."""
        return self.titles.title

    @property
    def main_picture_url(self) -> Optional[str]:
        """URL to the highest resolution picture available for this title.
        If no image is available returns None.
        """
        if self._main_picture is MISSING:
            return None
        # the API returns up to two pictures categorized as medium and large
        return self._main_picture['large'] or self._main_picture['medium']


class Related:
    """Represents related anime or manga.

    Printing it returns a string with all the pairs relation: title.
    Can return prequel, sequel and access to all the entries.
    """

    def __init__(self, data: Sequence[RelationPayload]) -> None:
        self._related: Dict[str, List[BaseResult]] = {}
        for entry in data:
            key = entry['relation_type_formatted']
            if key not in self._related:
                self._related[key] = [BaseResult(entry['node'])]
            else:
                self._related[key].append(BaseResult(entry['node']))

    # __iter__ is not present because the results are divided in different categories

    def __len__(self) -> int:
        return sum([len(self._related[key]) for key in self._related])

    def __str__(self) -> str:
        s = f''
        for entry in self._related:
            values = ', '.join(str(r) for r in self._related[entry])
            s += f'{entry}: {values}\n'
        return s

    @property
    def prequel(self) -> Optional[BaseResult]:
        """Prequel for this title. If there isn't any returns None."""
        if 'Prequel' in self._related:
            return self._related['Prequel'][0]
        return None

    @property
    def sequel(self) -> Optional[BaseResult]:
        """Sequel for this title. If there isn't any returns None."""
        if 'Sequel' in self._related:
            return self._related['Sequel'][0]
        return None

    @property
    def all(self) -> Dict[str, List[BaseResult]]:
        """All the available data returned as a dictionary."""
        return self._related


class Recommendation(ReadOnlyIterable[Tuple[int, BaseResult]]):
    """Recommendation data. Directly iterate over this
    object to retrieve the entries. Each element is a tuple with the number of
    recommending users and the title that is recommended

    Attributes:
        recommendations: list of recommendations
    """

    def __init__(self, data: Sequence[RecommendationPayload]) -> None:
        self.recommendations: List[Tuple[int, BaseResult]] = []
        # satisfy the ReadOnlyProtocol structure
        self._list = self.recommendations
        for entry in data:
            self.recommendations.append(
                (entry['num_recommendations'], BaseResult(entry['node'])))
        # sort by the number of people who recommended a specific title
        self.recommendations.sort(key=lambda x: x[0], reverse=True)

    def __str__(self) -> str:
        s = f''
        for entry in self.recommendations:
            s += f'{entry[1]} - recommended by {entry[0]} people.\n'
        return s

    @property
    def top_recommendation(self) -> Optional[str]:
        """Recommendation with the highest number of users. Returns None if there aren't any."""
        if self.recommendations:
            top = self.recommendations[0]
            return f'{top[1]} - recommended by {top[0]} people.\n'
        return None


class Result(BaseResult):
    """Represents the base for search results objects.
    Both Anime and Manga inherits from this as it contains the common fields
    between the two.

    Attributes:
        titles: all the alternative titles, including both english and japanese ones
        synopsis: synopsis available on the MAL page
        mean: average score given by user rating
        rank: position in the ranking by score
        popularity: position in the ranking by users who have this title in their list
        num_list_users: number of users who have this title in their list
        num_scoring_users: number of users who gave a score to this title
        nsfw: the level of nsfw, can be white, gray or black
        genres: the different genres that this title falls under
        background: some background information of the title
        related_anime: all the anime related to this title
        related_manga: all the manga related to this title
        recommendations: similar titles that users have recommended if you liked this one
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, payload: ResultPayload) -> None:
        super().__init__(payload)
        self.titles: Titles = Titles(
            payload['title'], payload.get('alternative_titles', MISSING))
        self.synopsis: str = payload.get(
            'synopsis', 'synopsis not requested or missing')
        self.mean: float = payload.get('mean', 0.0)
        self.rank: int = payload.get('rank', 0)
        self.popularity: int = payload.get('popularity', 0)
        self.num_list_users: int = payload.get('num_list_users', 0)
        self.num_scoring_users: int = payload.get('num_scoring_users', 0)
        self.num_favorites: int = payload.get('num_favorites', 0)
        self.background: str = payload.get(
            'background', 'background not requested or missing')
        self.nsfw: NSFWlevel = NSFWlevel(payload.get('nsfw', 'white'))
        self.genres: List[Genre] = []
        _genres = payload.get('genres', [])
        for genre in _genres:
            self.genres.append(Genre(genre))
        self.related_anime: Related = Related(payload.get('related_anime', []))
        self.related_manga: Related = Related(payload.get('related_manga', []))
        self.recommendations: Recommendation = Recommendation(
            payload.get('recommendations', []))
        self._pictures: List[PicturePayload] = []
        _pictures = payload.get('pictures', [])
        for pic in _pictures:
            self._pictures.append(pic)
        self._start: str = payload.get('start_date', MISSING)
        self._end: str = payload.get('end_date', MISSING)
        self._created_at: str = payload.get('created_at', MISSING)
        self._updated_at: str = payload.get('updated_at', MISSING)
        self.raw: Any = payload

    def __str__(self) -> str:
        return super().__str__()

    @property
    def start_date(self) -> Optional[Union[date, int]]:
        """Returns the starting date as a datetime.date."""
        if self._start is not MISSING:
            try:
                start_date = datetime.date(
                    datetime.strptime(self._start, '%Y-%m-%d'))
            except ValueError:
                try:
                    start_date = datetime.date(
                        datetime.strptime(self._start, '%Y-%m'))
                except ValueError:
                    start_date = datetime.strptime(self._start, '%Y')
                    start_date = start_date.year
                finally:
                    return start_date  # type: ignore
            finally:
                return start_date  # type: ignore
        return None

    @property
    def end_date(self) -> Optional[date]:
        """Returns the ending date as a datetime.date."""
        if self._end is not MISSING:
            return datetime.strptime(self._end, '%Y-%m-%d')
        return None

    @property
    def created_at(self) -> Optional[datetime]:
        """ISO 8061 datetime of when the entry was created in the MAL database."""
        if self._created_at is not MISSING:
            return datetime.fromisoformat(self._created_at)
        return None

    @property
    def updated_at(self) -> Optional[datetime]:
        """ISO 8061 datetime of when the entry was last updated in the MAL database."""
        if self._updated_at is not MISSING:
            return datetime.fromisoformat(self._updated_at)
        return None

    @property
    def pictures(self) -> Optional[List[str]]:
        """List of urls of the available pictures."""
        if self._pictures:
            pics: List[str] = []
            for pic in self._pictures:
                if pic['large'] is not None:
                    pics.append(pic['large'])
                else:
                    pics.append(pic['medium'])
            return pics
        return None

    @property
    def url(self) -> str:
        """Placeholder for the url of the entry."""
        return 'URL placeholder'

    @property
    def api_url(self) -> str:
        """Placeholder for the url to request this title from the API."""
        return 'API URL placeholder'


class ListStatus:
    """Information that is associated to an entry in a user list.

    Attributes:
        score: the score that the user gave to this title
        priority: numeric value of the priority given to this title
        tags: list of tags that the user categorized this title as
    """

    def __init__(self, data: ListStatusPayload) -> None:
        self.score: int = data.get('score', 0)
        self._start: str = data.get('start_date', MISSING)
        self._end: str = data.get('end_date', MISSING)
        self.priority: int = data.get('priority', 0)
        self.tags: List[str] = []
        _tags = data.get('tags', MISSING)
        if _tags is not MISSING:
            self.tags = [tag for tag in _tags]
        self._updated_at: str = data.get('updated_at', MISSING)

    # __str__ implemented in subclasses

    @property
    def start_date(self) -> Optional[date]:
        """The ending date as a datetime.date."""
        if self._start is not MISSING:
            return datetime.strptime(self._start, '%Y-%m-%d')
        return None

    @property
    def end_date(self) -> Optional[date]:
        """The ending date as a datetime.date."""
        if self._end is not MISSING:
            return datetime.strptime(self._end, '%Y-%m-%d')
        return None

    @property
    def created_at(self) -> Optional[datetime]:
        """ISO 8061 datetime of when the user updated the entry."""
        if self._updated_at is not MISSING:
            return datetime.fromisoformat(self._updated_at)
        return None


class UserListEntry:
    """Represents an entry in a user list."""

    def __init__(self, data: ListEntryPayload) -> None:
        # do not initialize the values because they are overridden in the subclasses
        self.entry: Any
        self.list_status: Any
        self.api_call_manager: APICallManager

    def __str__(self) -> str:
        return f'{self.entry.title}'

    @property
    def score(self) -> int:
        """Returns the score for this entry."""
        return self.list_status.score


class UserList(PaginatedObject):
    """Base for representing a user list.

    Attributes:
        average_score: The averege score of all rated titles. It's 0.0f if not computable.
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, data: Union[AnimeListPayload, MangaListPayload]) -> None:
        super().__init__(data)
        # initialized in subclass to avoid doing it twice
        self._list: Any
        self.average_score: float  # computed in subclasses where i have data
        self.raw: Any

    # __iter__ implemented in subclasses

    def __len__(self) -> int:
        return len(self._list)

    def __str__(self) -> str:
        return '\n'.join([str(item) for item in self._list])

    def _compute_average_score(self) -> float:
        total = 0
        count = 0
        for item in self._list:
            if item.score:
                total += item.score
                count += 1
        if count != 0:
            return total / count
        return 0.0


class Ranking(PaginatedObject):
    """Base for representing ranking results."""

    def __init__(self, data: RankingPayload) -> None:
        super().__init__(data)
        # initialized in subclasses
        self._ranking: Any
        self.raw: Any
        url: Optional[str] = None
        # extract type from the url
        if self.prev_page is not None:
            url = self.prev_page
        elif self.next_page is not None:
            url = self.next_page
        if url is not None:
            parameters = url.split('&')
            for param in parameters:
                if param.startswith('ranking_type'):
                    self._type = param.split('=')[1]
        # if url is missing leave empty
        else:
            self._type = MISSING

    def __iter__(self) -> Iterator[int]:
        return iter(self._ranking)

    def __len__(self) -> int:
        return len(self._ranking)

    def __str__(self) -> str:
        s = f'Ranking by {self._type}\n'
        s += '\n'.join([f'{rank} - {self._ranking[rank]}' for rank in self._ranking])
        return s
