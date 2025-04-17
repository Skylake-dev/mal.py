from __future__ import annotations
from typing import List, Optional

from .base import PaginatedObject, ReadOnlyIterable
from .enums import CharacterRole
from .typed import CharacterNodePayload, CharactersPayload, PicturePayload


class AnimeCharacter:
    """Represents a character from an anime.

    Attributes:
        id: the id of the result
            NOTE: this is not unique for each object only between objects of the same category
            for example, all anime have different id but an anime and a manga can have same id
        first_name: first name for the character, empty string if not present
        last_name: last name for the character, empty string if not present
        alternative_name: alternative name for the character, empty string if not present
        main_picture: url to the character picture, None if not present
        biography: short biography of the character, empty string if not present
        num_favorites: number of users who put this character in their favorites
        role: role of the character, either main or supporting
    """

    def __init__(self, data: CharacterNodePayload) -> None:
        _node = data['node']
        self.id: int = _node['id']   # this is mandatory
        self.first_name: str = _node.get('first_name', '')
        self.last_name: str = _node.get('last_name', '')
        self.alternative_name: str = _node.get('alternative_name', '')
        self.main_picture: Optional[str] = None
        _pic: Optional[PicturePayload] = _node.get('main_picture', None)
        if _pic:
            if 'large' in _pic:
                self.main_picture = _pic['large']
            self.main_picture = _pic['medium']
        self.biography: str = _node.get('biography', '')
        self.num_favorites: int = _node.get('num_favorites', 0)
        self.role: CharacterRole = CharacterRole(data['role'])

    def __str__(self) -> str:
        name = ''
        if len(self.first_name) > 0:
            name += self.first_name
        if len(self.last_name) > 0:
            name += ' ' + self.last_name
        if len(self.alternative_name) > 0:
            name += f' ({self.alternative_name})'
        return name

    def __repr__(self) -> str:
        return self.__str__()


class AnimeCharactersList(PaginatedObject, ReadOnlyIterable[AnimeCharacter]):
    """Iterable object containing the characters from the specified anime.

    Attributes:
        raw: The raw json data for this object as returned by the API.
    """

    def __init__(self, data: CharactersPayload) -> None:
        super().__init__(data)
        self._list: List[AnimeCharacter] = []
        for item in data['data']:
            self._list.append(AnimeCharacter(item))
        self.raw: CharactersPayload = data

    def __str__(self) -> str:
        return '\n'.join(str(c) for c in self._list)

    def __repr__(self) -> str:
        return self.__str__()
