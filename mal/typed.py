"""Support classes for type hinting."""
from typing import Sequence, TypedDict


class TitlesPayload(TypedDict, total=False):
    synonyms: Sequence[str]
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
    # note to self:
    #    the parser gets these as str instead of int because they are returned
    #    as strings by the api, for example
    #    "watching": "12345"
    watching: str
    completed: str
    on_hold: str
    dropped: str
    plan_to_watch: str


class StatisticsPayload(TypedDict):
    # for some reason the statistics are returned only for animes
    status: AnimeStatusPayload
    num_list_users: int


class MusicPayload(TypedDict):
    id: int
    anime_id: int
    text: str


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
    genres: Sequence[GenericPayload]
    pictures: Sequence[PicturePayload]
    background: str
    related_anime: Sequence[RelationPayload]
    related_manga: Sequence[RelationPayload]
    recommendations: Sequence[RecommendationPayload]


class AnimePayload(ResultPayload, total=False):
    num_episodes: int
    start_season: SeasonPayload
    broadcast: BroadcastPayload
    source: str
    average_episode_duration: int
    rating: str
    studios: Sequence[GenericPayload]
    statistics: StatisticsPayload
    opening_themes: Sequence[MusicPayload]
    ending_themes: Sequence[MusicPayload]


class MangaPayload(ResultPayload, total=False):
    authors: Sequence[AuthorPayload]
    num_chapters: int
    num_volumes: int
    serialization: Sequence[SerializationPayload]


# Related to search results
class NodePayload(TypedDict):
    node: ResultPayload


class AnimeNodePayload(TypedDict):
    node: AnimePayload


class MangaNodePayload(TypedDict):
    node: MangaPayload


class PagingPayload(TypedDict, total=False):
    # for now this is not used
    previous: str
    next: str


class AnimeSearchPayload(TypedDict):
    data: Sequence[AnimeNodePayload]
    paging: PagingPayload


class MangaSearchPayload(TypedDict):
    data: Sequence[MangaNodePayload]
    paging: PagingPayload


# Related to user list

class ListStatusPayload(TypedDict, total=False):
    status: str
    score: int
    start_date: str
    finish_date: str
    priority: int
    tags: Sequence[str]
    comments: str
    updated_at: str


class AnimeListEntryStatusPayload(ListStatusPayload, total=False):
    num_episodes_watched: int
    is_rewatching: bool
    num_times_rewatched: int
    rewatch_value: int


class MangaListEntryStatusPayload(ListStatusPayload, total=False):
    num_volumes_read: int
    num_chapters_read: int
    is_rereading: bool
    num_times_reread: int
    reread_value: int


class ListEntryPayload(TypedDict):
    # total because the list_status field is always requested
    node: ResultPayload
    list_status: ListStatusPayload


class AnimeListEntryPayload(TypedDict):
    # total because the list_status field is always requested
    node: AnimePayload
    list_status: AnimeListEntryStatusPayload


class MangaListEntryPayload(TypedDict):
    # total because the list_status field is always requested
    node: MangaPayload
    list_status: MangaListEntryStatusPayload


class ListPayload(TypedDict):
    data: Sequence[ListEntryPayload]
    paging: PagingPayload


class AnimeListPayload(TypedDict):
    data: Sequence[AnimeListEntryPayload]
    paging: PagingPayload


class MangaListPayload(TypedDict):
    data: Sequence[MangaListEntryPayload]
    paging: PagingPayload


class SeasonalAnimePayload(TypedDict):
    data: Sequence[AnimeNodePayload]
    paging: PagingPayload
    season: SeasonPayload


class _RankPayload(TypedDict):
    rank: int


class RankPayload(_RankPayload, total=False):
    # specify that only previous_rank is optional
    previous_rank: int


class RankingNodePayload(TypedDict):
    node: ResultPayload
    ranking: RankPayload


class AnimeRankingNodePayload(TypedDict):
    node: AnimePayload
    ranking: RankPayload


class MangaRankingNodePayload(TypedDict):
    node: MangaPayload
    ranking: RankPayload


class RankingPayload(TypedDict):
    data: Sequence[RankingNodePayload]
    paging: PagingPayload


class AnimeRankingPayload(TypedDict):
    data: Sequence[AnimeRankingNodePayload]
    paging: PagingPayload


class MangaRankingPayload(TypedDict):
    data: Sequence[MangaRankingNodePayload]
    paging: PagingPayload


class SubBoardPayload(TypedDict):
    id: int
    title: str


class BoardPayload(TypedDict):
    id: int
    title: str
    description: str
    subboards: Sequence[SubBoardPayload]


class BoardCategoryPayload(TypedDict):
    title: str
    boards: Sequence[BoardPayload]
