"""Support classes for type hinting."""
from typing import List, TypedDict


class TitlesPayload(TypedDict, total=False):
    synonyms: List[str]
    en: str
    ja: str


class PicturePayload(TypedDict):
    medium: str
    large: str


class GenericPayload(TypedDict):
    # a lot of things use the format id + name, like genres, studios, magazines
    # but these are not very useful since the API doesn't offer a way to look up more
    # information on those
    id: int
    name: str


class SeasonPayload(TypedDict):
    year: int
    season: str


class BroadcastPayload(TypedDict):
    day_of_the_week: str
    start_time: str


class BaseResultPayload(TypedDict):
    id: int
    title: str
    main_picture: PicturePayload


class RelationPayload(TypedDict):
    node: BaseResultPayload
    relation_type: str
    relation_type_formatted: str


class RecommendationPayload(TypedDict):
    node: BaseResultPayload
    num_recommendations: int


class AnimeStatusPayload(TypedDict):
    # this should all be int but the json parser of requests gets them as str
    # need to convert them to int before using
    watching: str
    completed: str
    on_hold: str
    dropped: str
    plan_to_watch: str


class StatisticsPayload(TypedDict):
    # for some reason the statistics are returned only for animes
    status: AnimeStatusPayload
    num_list_users: int


class PersonPayload(TypedDict, total=False):
    id: int
    first_name: str
    last_name: str


class AuthorPayload(TypedDict):
    node: PersonPayload
    role: str


class SerializationPayload(TypedDict):
    # for some reason the magazines are not put in a list like genres but are put in a dictionary
    # made of only one key.
    node: GenericPayload


class ResultPayload(BaseResultPayload, total=False):
    alternative_titles: TitlesPayload
    start_date: str
    end_date: str
    synopsis: str
    mean: float
    rank: int
    popularity: int
    num_list_users: int
    num_scoring_users: int
    nsfw: str
    created_at: str
    updated_at: str
    media_type: str
    status: str
    genres: List[GenericPayload]
    pictures: List[PicturePayload]
    background: str
    related_anime: List[RelationPayload]
    related_manga: List[RelationPayload]
    recommendations: List[RecommendationPayload]


class AnimePayload(ResultPayload, total=False):
    num_episodes: int
    start_season: SeasonPayload
    broadcast: BroadcastPayload
    source: str
    average_episode_duration: int
    rating: str
    studios: List[GenericPayload]
    statistics: StatisticsPayload


class MangaPayload(ResultPayload, total=False):
    authors: List[AuthorPayload]
    num_chapters: int
    num_volumes: int
    serialization: List[SerializationPayload]


class AnimeNodePayload(TypedDict):
    node: AnimePayload


class MangaNodePayload(TypedDict):
    node: MangaPayload


class PagingPayload(TypedDict, total=False):
    previous: str
    next: str


class AnimeSearchPayload(TypedDict):
    data: List[AnimeNodePayload]
    paging: PagingPayload


class MangaSearchPayload(TypedDict):
    data: List[MangaNodePayload]
    paging: PagingPayload
