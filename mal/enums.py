from __future__ import annotations

import logging

from enum import Enum, EnumMeta
from typing import Any, List, Sequence, Union

logger = logging.getLogger(__name__)

class BaseEnumMeta(EnumMeta):
    def __contains__(cls: type[Any], obj: object) -> bool:
        try:
            cls(obj)
        except ValueError:
            return False
        else:
            return True


class BaseEnum(Enum, metaclass=BaseEnumMeta):
    """Base class for all the constants used to represent the possible different
    values some fields. Can be printed directly and can be compared with a string if needed.

    Example:
        print(Field.id) ---> id
        Field.id == 'id' ---> True
    """

    def __str__(self):
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BaseEnum):
            return super().__eq__(other)
        elif isinstance(other, str):
            return self.value == other
        else:
            return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class AnimeStatus(BaseEnum):
    airing = 'currently_airing'
    finished = 'finished_airing'
    not_aired = 'not_yet_aired'


class AnimeMediaType(BaseEnum):
    movie = 'movie'
    music = 'music'
    ona = 'ona'
    ova = 'ova'
    special = 'special'
    tv = 'tv'
    unknown = 'unknown'


class MangaStatus(BaseEnum):
    finished = 'finished'
    not_published = 'not_yet_published'
    publishing = 'currently_publishing'
    on_hiatus = 'on_hiatus'
    discontinued = 'discontinued'


class MangaMediaType(BaseEnum):
    doujinshi = 'doujinshi'
    light_novel = 'light_novel'
    manga = 'manga'
    manhua = 'manhua'
    manhwa = 'manhwa'
    novel = 'novel'
    oel = 'oel'
    one_shot = 'one_shot'
    unknown = 'unknown'


class NSFWlevel(BaseEnum):
    black = 'black'
    gray = 'gray'
    white = 'white'


class AdaptationFrom(BaseEnum):
    game = 'game'
    light_novel = 'light_novel'
    manga = 'manga'
    novel = 'novel'
    original = 'original'
    visual_novel = 'visual_novel'
    other = 'other'
    koma_manga = '4_koma_manga'
    web_manga = 'web_manga'
    digital_manga = 'digital_manga'
    card_game = 'card_game'
    book = 'book'
    picture_book = 'picture_book'
    radio = 'radio'
    music = 'music'
    web_novel = 'web_novel'
    mixed_media = 'mixed_media'


class AnimeListStatus(BaseEnum):
    completed = 'completed'
    dropped = 'dropped'
    on_hold = 'on_hold'
    plan_to_watch = 'plan_to_watch'
    watching = 'watching'


class MangaListStatus(BaseEnum):
    completed = 'completed'
    dropped = 'dropped'
    on_hold = 'on_hold'
    plan_to_read = 'plan_to_read'
    reading = 'reading'


class AnimeListSort(BaseEnum):
    score = 'list_score'
    updated_at = 'list_updated_at'
    title = 'anime_title'
    start_date = 'anime_start_date'
    id = 'anime_id'


class MangaListSort(BaseEnum):
    score = 'list_score'
    updated_at = 'list_updated_at'
    title = 'manga_title'
    start_date = 'manga_start_date'
    id = 'manga_id'


class Season(BaseEnum):
    winter = 'winter'
    spring = 'spring'
    summer = 'summer'
    fall = 'fall'


class AnimeRankingType(BaseEnum):
    all = 'all'
    airing = 'airing'
    upcoming = 'upcoming'
    tv = 'tv'
    ova = 'ova'
    movie = 'movie'
    special = 'special'
    by_popularity = 'bypopularity'
    favorite = 'favorite'


class MangaRankingType(BaseEnum):
    all = 'all'
    manga = 'manga'
    novels = 'novels'
    oneshots = 'oneshots'
    douhin = 'doujin'
    manhwa = 'manhwa'
    manhua = 'manhua'
    by_popularity = 'bypopularity'
    favorite = 'favorite'


class Field(BaseEnum):
    # Common fields for anime and manga
    id = 'id'
    title = 'title'
    main_picture = 'main_picture'
    alternative_titles = 'alternative_titles'
    start_date = 'start_date'     # can be only year for non aired/published
    end_date = 'end_date'         # missing if not aired/published
    synopsis = 'synopsis'
    mean = 'mean'                 # missing if not aired/published
    rank = 'rank'                 # missing if not aired/published
    popularity = 'popularity'
    num_list_users = 'num_list_users'
    num_scoring_users = 'num_scoring_users'  # 0 if not aired/published
    nsfw = 'nsfw'
    created_at = 'created_at'     # 01-01-1970 in some cases, probably a default value
    updated_at = 'updated_at'
    media_type = 'media_type'
    status = 'status'
    genres = 'genres'
    # my_list_status = 'my_list_status'  not implemented
    pictures = 'pictures'
    background = 'background'               # can be empty
    related_anime = 'related_anime'         # can be empty
    related_manga = 'related_manga'         # can be empty
    recommendations = 'recommendations'     # can be empty

    # Anime only fields
    num_episodes = 'num_episodes'    # 0 if not aired
    start_season = 'start_season'    # missing if not aired
    broadcast = 'broadcast'          # missing if not aired
    source = 'source'
    average_episode_duration = 'average_episode_duration'   # 0 if not aired
    rating = 'rating'
    studios = 'studios'                     # can be empty
    # can be inconsistent e.g. some users can mark it
    # as completed even if not aired
    statistics = 'statistics'
    opening_themes = 'opening_themes'
    ending_themes = 'ending_themes'
    # Manga only fields
    authors = 'authors'
    num_chapters = 'num_chapters'           # 0 if not completed
    num_volumes = 'num_volumes'             # 0 if not completed
    serialization = 'serialization'

    @property
    def anime_fields(self) -> List[Field]:
        """Returns all the fields that can be requested for an anime."""
        forbidden = [
            self.authors,
            self.num_chapters,
            self.num_volumes,
            self.serialization,
        ]
        return [field for field in Field if not field in forbidden]

    @property
    def is_anime(self) -> bool:
        return self in self.anime_fields

    @property
    def manga_fields(self) -> List[Field]:
        """Returns all the fields that can be requested for a manga."""
        forbidden = [
            self.num_episodes,
            self.start_season,
            self.broadcast,
            self.source,
            self.average_episode_duration,
            self.rating,
            self.studios,
            self.statistics,
            self.opening_themes,
            self.ending_themes
        ]
        return [field for field in Field if not field in forbidden]

    @property
    def is_manga(self) -> bool:
        return self in self.manga_fields

    @classmethod
    def from_list(cls, fields: Sequence[Union[str, Field]]) -> List[Field]:
        """Returns the list of fields from the corresponding string representation.

        Args:
            fields: list of fields

        Returns:
            List[Field]: converted fields

        Raises:
            ValueError: one or more strings are not a valid field
        """
        result: List[Field] = []
        for field in fields:
            # skip invalid fields
            if field not in Field:
                logger.warning(f'Invalid field: {field}')
                continue
            if isinstance(field, str):
                field = Field[field]
            result.append(field)
        return result

    @classmethod
    def base(cls) -> List[Field]:
        default = [         # note that id, title and main_picture are always returned by the API
            Field.status,
            Field.media_type,
            Field.genres,
            Field.mean,
            Field.status
        ]
        return default

    @classmethod
    def default_anime(cls) -> List[Field]:
        """Default fields that are requested for an anime."""
        fields = cls.base() + [
            Field.num_episodes,
            Field.start_season,
            Field.broadcast,
            Field.source
        ]
        return fields

    @classmethod
    def default_manga(cls) -> List[Field]:
        """Default fields that are requested for a manga."""
        fields = cls.base() + [
            Field.num_chapters,
            Field.authors,
            Field.serialization
        ]
        return fields

    @classmethod
    def all_anime(cls) -> List[Field]:
        """All the fields that can be requested for an anime."""
        return [field for field in Field if field.is_anime]

    @classmethod
    def all_manga(cls) -> List[Field]:
        """All the fields that can be requested for a manga."""
        return [field for field in Field if field.is_manga]

    # TODO: add more pre-made templates
