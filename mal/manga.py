from typing import List, Iterator, Optional

from .enums import MangaStatus, MangaMediaType
from .base import Result
from .typed import AuthorPayload, GenericPayload, MangaPayload, MangaSearchPayload


class Author:
    """Represents an author for a manga.

    Attributes:
        id: the id in the MAL database
        first_name: the first name of the author
        last_name: the last name of the author
        full_name: concatenation of first_name and last_name
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
        status: current publication status, None if not requested
        media_type: the type of manga, None if not requested
        authors: list of authors that created the manga
        num_chapters: the number of chapters in total, 0 if not completed
        num_volumes: the number of volumes in total, 0 if not completed
        serialization: magazines or other formats where the series is published
    """

    def __init__(self, payload: MangaPayload) -> None:
        """Creates an Manga object from the received json data."""
        super().__init__(payload)
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

    @property
    def serialization(self):
        """Magazines or other formats where the series is published."""
        return ', '.join(mag['name'] for mag in self._serialization)


class MangaSearchResults:
    """Container for manga search results."""

    def __init__(self, data: MangaSearchPayload) -> None:
        self._results: List[Manga] = []
        for el in data['data']:
            self._results.append(Manga(el['node']))

    def __iter__(self) -> Iterator[Manga]:
        return iter(self._results)

    def __str__(self) -> str:
        return '\n'.join([str(result) for result in self._results])
