"""Module in charge of making requests to the API and managing possible errors."""
import logging
from typing import List, Dict, Optional, Sequence, Union

from .connection import APICallManager
from .endpoints import Endpoint
from .base import PaginatedObject
from .anime import Anime, AnimeSearchResults, AnimeList, AnimeRanking, Seasonal
from .characters import AnimeCharactersList
from .manga import Manga, MangaSearchResults, MangaList, MangaRanking
from .forum import BoardCategory, ForumTopics, Discussion
from .enums import (Field, AnimeListStatus, MangaListStatus, Season,
                    AnimeRankingType, MangaRankingType, AnimeListSort, MangaListSort,
                    SeasonalAnimeSort)
from .utils import MISSING
from .typed import PaginatedPayload

_log = logging.getLogger(__name__)


class Client:
    """Offers the interface to make requests."""

    def __init__(self, client_id: str):
        self._api_call_manager: APICallManager = APICallManager(
            client_id=client_id)
        self._limit: int = 10
        self._anime_fields: List[Field] = Field.default_anime()
        self._manga_fields: List[Field] = Field.default_manga()
        self._character_fields: List[Field] = Field.default_character()
        self._include_nsfw: bool = False
        self._auto_truncate: bool = False

    @property
    def limit(self) -> int:
        """Maximum number of results per page. Defaults to 10. Can be changed
        to any positive integer, it will be automatically adjusted to fit within
        the API limits.

        Raises:
            ValueError: if a negative value is passed
        """
        return self._limit

    @limit.setter
    def limit(self, value: int) -> None:
        # make sure this is an int
        value = int(value)
        if value <= 0:
            raise ValueError('limit must be a positive integer')
        self._limit = value
        _log.info(
            f'parameter "search_limit" default value set to {self._limit}')

    @property
    def anime_fields(self) -> List[Field]:
        """Fields that are requested in a anime query. This value is used in the following
        methods:
         - anime_search
         - get_anime
         - get_anime_list
         - get_seasonal_anime
         - get_anime_ranking

        Changes to this value are applied to all subsequent requests. Invalid fields
        are automatically ignored.
        It is possible to override this value per request by specifying the `fields` parameter.
        """
        return self._anime_fields

    @anime_fields.setter
    def anime_fields(self, new_fields: Sequence[Union[Field, str]]) -> None:
        fields = Field.from_list(new_fields)
        self._anime_fields = [f for f in fields if f.is_anime]
        _log.info(
            f'parameter "anime_fields" default value set to {self._anime_fields}')

    @property
    def manga_fields(self) -> List[Field]:
        """Fields that are requested in a manga query. This value is used in the following
        methods:
         - manga_search
         - get_manga
         - get_manga_list
         - get_manga_ranking

        Changes to this value are applied to all subsequent requests. Invalid fields
        are automatically ignored.
        It is possible to override this value per request by specifying the `fields` parameter.
        """
        return self._manga_fields

    @manga_fields.setter
    def manga_fields(self, new_fields: Sequence[Union[Field, str]]) -> None:
        fields = Field.from_list(new_fields)
        self._manga_fields = [f for f in fields if f.is_manga]
        _log.info(
            f'parameter "manga_fields" default value set to {self._manga_fields}')

    @property
    def character_fields(self) -> List[Field]:
        """Fields that are requested in a anime characters query. This value is used in
        the following methods:
         - get_anime_characters

        Changes to this value are applied to all subsequent requests. Invalid fields
        are automatically ignored.
        It is possible to override this value per request by specifying the `fields` parameter.
        """
        return self._character_fields

    @character_fields.setter
    def character_fields(self, new_fields: Sequence[Union[Field, str]]) -> None:
        fields = Field.from_list(new_fields)
        self._character_fields = [f for f in fields if f.is_character]
        _log.info(
            f'parameter "character_fields" default value set to {self._character_fields}')

    @property
    def include_nsfw(self) -> bool:
        """Specifies whether to include results marked as nsfw. Defaults to False.

        Changes to this value are applied to all subsequent requests.
        It is possible to override this value per request by specifying the `nsfw` parameter.
        """
        return self._include_nsfw

    @include_nsfw.setter
    def include_nsfw(self, value: bool) -> None:
        self._include_nsfw = value
        _log.info(f'parameter "nsfw" default value set to {value}')

    @property
    def auto_truncate(self) -> bool:
        """Specifies whether to truncate automatically queries that are too long. Defaults to False.

        If this parameter is False, a query longer than the maximum allowed by the API will
        result in a ValueError, otherwise it will be truncated to the maximum length, producing
        a log message.
        """
        return self._auto_truncate

    @auto_truncate.setter
    def auto_truncate(self, value: bool) -> None:
        self._auto_truncate = value
        _log.info(f'parameter "auto_truncate" default value set to {value}')

    @property
    def delay(self) -> float:
        """Returns the current delay. This is the amount of time in seconds that
        each request will be delayed. The default value is 1 second.
        Useful to avoid being ratelimited or banned when doing bulk requests.

        Anything above 1 second is safe for continuous requests. You can set it lower if you are only
        doing a few requests at a time. Unfortunately MAL doens't specify exact ratelitis, if you start getting
        403s then you are being blocked.
        """
        return self._api_call_manager.delay

    @delay.setter
    def delay(self, delay: float) -> None:
        if delay < 0:
            raise ValueError('delay cannot be negative')
        if delay < 1.0:
            _log.warning(
                'Attention: using delays shorter than 1s for bulk request may result in temporary or permanent blocking')
        _log.info(f'parameter "delay" value set to {delay:.2f}s')
        self._api_call_manager.delay = delay

    def anime_search(
        self,
        query: str,
        *,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        include_nsfw: bool = MISSING
    ) -> AnimeSearchResults:
        """Search anime matching the given query. By default it uses the default parameters
        or the ones that have been set in limit and fields. If you pass limit and fields to this
        method they are used for this query only.

        Args:
            query: string used to search titles, betwneen 3 and 64 characters

        Keyword args:
            limit: maximum number of results, needs to be between 1 and 100
            offset: get results at a certain offset from the start, defaults to 0
            fields: the fields that are going to be requested, for a complete list see Field enum
            include_nsfw: include results marked as nsfw

        Returns:
            AnimeSearchResults: iterable object containing the results

        Raises:
            ValueError: when the query is not between 3 and 64 characters
        """
        parameters = self._build_parameters(
            Endpoint.ANIME, query=query, limit=limit, offset=offset, fields=fields, nsfw=include_nsfw)
        url: str = Endpoint.ANIME.url
        data = self._api_call_manager.api_call(url, params=parameters)
        results = AnimeSearchResults(data)
        return results

    def manga_search(
        self,
        query: str,
        *,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        include_nsfw: bool = MISSING
    ) -> MangaSearchResults:
        """Search manga matching the given query. By default it uses the default parameters
        or the ones that have been set in limit and fields. If you pass limit and fields to this
        method they are used for this query only.

        Args:
            query: string used to search titles, betwneen 3 and 64 characters

        Keyword args:
            limit: maximum number of results, needs to be between 1 and 100
            offset: get results at a certain offset from the start, defaults to 0
            fields: the fields that are going to be requested, for a complete list see Field enum
            include_nsfw: include results marked as nsfw

        Returns:
            MangaSearchResults: iterable object containing the results

        Raises:
            ValueError: when the query is not between 3 and 64 characters
        """
        parameters = self._build_parameters(
            Endpoint.MANGA, query=query, limit=limit, offset=offset, fields=fields, nsfw=include_nsfw)
        url: str = Endpoint.MANGA.url
        data = self._api_call_manager.api_call(url, params=parameters)
        results = MangaSearchResults(data)
        return results

    def get_anime(self, id: Union[int, str], *, fields: Sequence[Union[Field, str]] = MISSING) -> Anime:
        """Get the details for a specific anime given the id.

        Args:
            id: the id of the anime or the url of its MAL page

        Keyword args:
            fields: list of fields to retrieve for this request

        Returns:
            Anime: the anime object with all the details
        """
        parameters = self._build_parameters(
            Endpoint.ANIME, fields=fields)
        url: str = Endpoint.ANIME.url + '/' + self._get_as_id(id)
        data = self._api_call_manager.api_call(url, params=parameters)
        return Anime(data)

    def get_anime_characters(
        self,
        id: Union[int, str],
        *,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING
    ) -> AnimeCharactersList:
        """Get the details for the characters of a specific anime. Note that this method relies
        on undocumented endpoints so it can stop working unexpectedly or change behaviour.

        Args:
            id: the id of the anime or the url of its MAL page

        Keyword args:
            limit: set the number of entries to retrieve, defaults to 10
            offset: get results at a certain offset from the start, defaults to 0
            fields: set which fields to get for each entry

        Returns:
            AnimeCharactersList: iterable with all the characters, possibly paginated
        """
        parameters = self._build_parameters(
            Endpoint.ANIME_CHARACTERS, fields=fields, limit=limit, offset=offset)
        url: str = Endpoint.ANIME_CHARACTERS.url.replace(
            '{anime_id}', self._get_as_id(id))
        data = self._api_call_manager.api_call(url, params=parameters)
        return AnimeCharactersList(data)

    def get_manga(self, id: Union[int, str], *, fields: Sequence[Union[Field, str]] = MISSING) -> Manga:
        """Get the details for a specific manga given the id.

        Args:
            id: the id of the manga or the url of its MAL page

        Keyword args:
            fields: list of fields to retrieve for this request

        Returns:
            Manga: the manga object with all the details
        """
        parameters = self._build_parameters(
            Endpoint.MANGA, fields=fields)
        url: str = Endpoint.MANGA.url + '/' + self._get_as_id(id)
        data = self._api_call_manager.api_call(url, params=parameters)
        return Manga(data)

    def get_anime_list(
        self,
        username: str,
        *,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        status: Union[AnimeListStatus, str] = MISSING,
        sort: Union[AnimeListSort, str] = MISSING,
        include_nsfw: bool = MISSING
    ) -> AnimeList:
        """Returns the anime list of a specific user, if public.

        Args:
            username: the MAL username of the user, case insensitive

        Keyword args:
            limit: set the number of entries to retrieve, defaults to 10
            offset: get results at a certain offset from the start, defaults to 0
            fields: set which fields to get for each entry
            status: return only a specific category. will return all if omitted
            sort: specify the sorting of the list
            include_nsfw: include results marked as nsfw

        Returns:
            AnimeList: iterable with all the entries of the list
        """
        parameters = self._build_parameters(
            Endpoint.USER_ANIMELIST, limit=limit, offset=offset, fields=fields, status=status, nsfw=include_nsfw, sort=sort)
        url = Endpoint.USER_ANIMELIST.url.replace('{username}', username)
        data = self._api_call_manager.api_call(url, params=parameters)
        return AnimeList(data)

    def get_manga_list(
        self,
        username: str,
        *,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        status: Union[MangaListStatus, str] = MISSING,
        sort: Union[MangaListSort, str] = MISSING,
        include_nsfw: bool = MISSING
    ) -> MangaList:
        """Returns the manga list of a specific user, if public.

        Args:
            username: the MAL username of the user, case insensitive

        Keyword args:
            limit: set the number of entries to retrieve, defaults to 10
            offset: get results at a certain offset from the start, defaults to 0
            fields: set which fields to get for each entry
            status: return only a specific category. will return all if omitted
            sort: specify the sorting of the list
            include_nsfw: include results marked as nsfw

        Returns:
            MangaList: iterable with all the entries of the list
        """
        parameters = self._build_parameters(
            Endpoint.USER_MANGALIST, limit=limit, offset=offset, fields=fields, status=status, nsfw=include_nsfw, sort=sort)
        url = Endpoint.USER_MANGALIST.url.replace('{username}', username)
        data = self._api_call_manager.api_call(url, params=parameters)
        return MangaList(data)

    def get_seasonal_anime(
        self,
        year: int,
        season: Union[str, Season],
        *,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        sort: Union[SeasonalAnimeSort, str] = MISSING,
        include_nsfw: bool = MISSING
    ) -> Seasonal:
        """Returns the list of anime aired during a specific season.
        Note that the field `start_season`, if included, is not necessarily the
        season that was requested. This is because the API does not return only
        the anime that started in ththe requested season but all the ones that were airing
        during that season. In particular also titles that started before the
        requested season (that maybe finished or still ongoing) are included in
        the response. To get only the ones started in this season the user needs
        to filter the results by looking at the `start_season` attribute.

        Args:
            year: the desired year
            season: the desired season, can be winter, spring, summer or fall.
                | In particular they correspond to specific months
                | winter -> January, February, March
                | spring -> April, May, June
                | summer -> July, August, September
                | fall -> October, November, December

        Keyword args:
            limit: set the number of entries to retrieve, defaults to 10
            offset: get results at a certain offset from the start, defaults to 0
            fields: set which fields to get for each entry
            sort: how to sort the results
            include_nsfw: include results marked as nsfw

        Returns:
            Seasonal: container for the results, sorted by score
        """
        parameters = self._build_parameters(
            Endpoint.ANIME_SEASONAL, limit=limit, offset=offset, fields=fields, sort=sort, nsfw=include_nsfw)
        season = Season(season)  # this validates season or raises ValueError
        url = f'{Endpoint.ANIME_SEASONAL}/{year}/{season.value}'
        data = self._api_call_manager.api_call(url, params=parameters)
        results: Seasonal = Seasonal(data)
        return results

    def get_anime_ranking(
        self,
        *,
        ranking_type: Union[str, AnimeRankingType] = AnimeRankingType.all,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING
    ) -> AnimeRanking:
        """Returns the top anime in the rankings.

        Keyword args:
            ranking_type: the type of ranking to request, defaults to all.
                For all possible values see enums.AnimeRanking
            limit: numbers of entries to request
            offset: get results at a certain offset from the start, defaults to 0
            fields: set which fields to get for each entry

        Returns:
            AnimeRanking: the results

        Raises:
            ValueError: ranking_type is invalid, check AnimeRankingType for all options
        """
        parameters = self._build_parameters(
            Endpoint.ANIME_RANKING, limit=limit, offset=offset, fields=fields)
        if isinstance(ranking_type, str):
            ranking_type = AnimeRankingType(ranking_type)
        parameters['ranking_type'] = f'{ranking_type}'
        url: str = Endpoint.ANIME_RANKING.url
        data = self._api_call_manager.api_call(url, params=parameters)
        ranking = AnimeRanking(data)
        ranking.type = ranking_type
        return ranking

    def get_manga_ranking(
        self,
        *,
        ranking_type: Union[str, MangaRankingType] = MangaRankingType.all,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING
    ) -> MangaRanking:
        """Returns the top manga in the rankings.

        Keyword args:
            ranking_type: the type of ranking to request, defaults to all.
                For all possible values see enums.MangaRanking
            limit: numbers of entries to request
            offset: get results at a certain offset from the start, defaults to 0
            fields: set which fields to get for each entry

        Returns:
            MangaRanking: the results

        Raises:
            ValueError: ranking_type is invalid, check MangaRankingType for all options
        """
        parameters = self._build_parameters(
            Endpoint.MANGA_RANKING, limit=limit, offset=offset, fields=fields)
        if isinstance(ranking_type, str):
            ranking_type = MangaRankingType(ranking_type)
        parameters['ranking_type'] = f'{ranking_type}'
        url: str = Endpoint.MANGA_RANKING.url
        data = self._api_call_manager.api_call(url, params=parameters)
        ranking = MangaRanking(data)
        ranking.type = ranking_type
        return ranking

    def get_boards(self) -> Sequence[BoardCategory]:
        """Returns a list of the forum boards divided by category."""
        url: str = Endpoint.FORUM_BOARDS.url
        data = self._api_call_manager.api_call(url)
        categories: List[BoardCategory] = []
        for category in data['categories']:
            categories.append(BoardCategory(category))
        return categories

    def get_topics(
        self,
        *,
        query: str = MISSING,
        board_id: int = MISSING,
        subboard_id: int = MISSING,
        limit: int = MISSING,
        offset: int = MISSING,
        topic_user_name: str = MISSING,
        user_name: str = MISSING
    ) -> ForumTopics:
        """Returns all the topics matching the given parameters. At least one of the arguments
        must be specified.

        Keyword Args:
            query: query used to search topics, minimum length 3 characters
            board_id: limit the search to a specific board
            subboard_id: limit the search to a specific subboard
            limit: maximum number of results, between 1 and 100
            offset: get results at a certain offset from the start, defaults to 0
            topic_user_name: return only topics started by a specific user
            user_name: return topics where the user has partecipated
                NOTE: the difference between topic_user_name and user_name is not clear
                to get all posts by a user use only topic_user_name

        Raises:
            ValueError: no argument was specified
        """
        parameters = self._build_parameters(Endpoint.FORUM_TOPICS, query=query, board_id=board_id,
                                            subboard_id=subboard_id, limit=limit, offset=offset,
                                            topic_user_name=topic_user_name, user_name=user_name)
        url: str = Endpoint.FORUM_TOPICS.url
        data = self._api_call_manager.api_call(url, params=parameters)
        return ForumTopics(data, query)

    def get_topic_details(
        self,
        topic_id: int,
        *,
        limit: int = MISSING,
        offset: int = MISSING
    ) -> Discussion:
        """Returns all the details on a given topic.

        Args:
            topic_id: required, the id of the topic to request

        Keyword Args:
            limit: the number of posts to retrieve, defaults to 100
            offset: get results at a certain offset from the start, defaults to 0
        """
        parameters: Dict[str, str] = {}
        if limit is not MISSING:
            parameters['limit'] = str(self._get_limit(
                Endpoint.FORUM_TOPIC_DETAIL, limit))
        if offset is not MISSING:
            parameters['offset'] = str(offset)
        url: str = f'{Endpoint.FORUM_TOPIC_DETAIL}/{topic_id}'
        data = self._api_call_manager.api_call(url, params=parameters)
        return Discussion(data['data'])

    def previous_page(self, paginated: PaginatedObject) -> Optional[PaginatedObject]:
        """Returns a new object with the previous page of results.
        If not present returns None.

        Args:
            paginated: an object that supports pagination

        .. note::

            If you don't want to deal with paginated results consider
            increasing the 'limit' parameter in your queries
        """
        if paginated.prev_page is None:
            _log.info('No previous page available')
            return None
        _log.info(f'Requesting previous page at {paginated.prev_page}')
        data: PaginatedPayload = self._api_call_manager.api_call(
            paginated.prev_page)
        if data:
            return paginated.__class__(data)
        else:
            return None

    def next_page(self, paginated: PaginatedObject) -> Optional[PaginatedObject]:
        """Returns a new object with the next page of results.
        If not present returns None.

        Args:
            paginated: an object that supports pagination

        .. note::

            If you don't want to deal with paginated results consider
            increasing the 'limit' parameter in your queries
        """
        if paginated.next_page is None:
            _log.info('No nextious page available')
            return None
        _log.info(f'Requesting nextious page at {paginated.next_page}')
        data: PaginatedPayload = self._api_call_manager.api_call(
            paginated.next_page)
        if data:
            return paginated.__class__(data)
        else:
            return None

    def _handle_query(self, q: str, endpoint: Endpoint) -> str:
        # query parameter needs to be at least 3 chars
        # and up to 64 chars for anime/manga search
        # 344 chars for forum topics
        if endpoint is Endpoint.ANIME or endpoint is Endpoint.MANGA:
            max_len = 64
        elif endpoint is Endpoint.FORUM_TOPICS:
            max_len = 344
        else:
            # no need to do anythihng
            return q
        if len(q) < 3:
            raise ValueError(
                f'query parameter for endpoint {endpoint} needs to be between 3 and {max_len} characters long')
        elif len(q) > max_len:
            if self.auto_truncate:
                _log.info(
                    f'cutting query "{q}" to {max_len} chars due to auto_truncate being set')
                return q[:max_len]
            else:
                raise ValueError(
                    f'query parameter for endpoint {endpoint} needs to be between 3 and {max_len} characters long')
        return q

    def _build_parameters(
        self,
        endpoint: Endpoint,
        *,
        query: str = MISSING,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        nsfw: bool = MISSING,
        status: Union[AnimeListStatus, MangaListStatus, str] = MISSING,
        sort: Union[AnimeListSort, MangaListSort,
                    SeasonalAnimeSort, str] = MISSING,
        board_id: int = MISSING,
        subboard_id: int = MISSING,
        topic_user_name: str = MISSING,
        user_name: str = MISSING
    ) -> Dict[str, str]:
        """Interal function to build the parameter dictionary with some sanity checks."""
        parameters: Dict[str, str] = {}
        if query is not MISSING:
            parameters['q'] = self._handle_query(query, endpoint)
        if limit is not MISSING:
            parameters['limit'] = str(self._get_limit(endpoint, limit))
        else:
            parameters['limit'] = str(self._limit)
        if offset is not MISSING:
            parameters['offset'] = str(offset)
        if fields is not MISSING:
            parsed_fields = Field.from_list(fields)
            if endpoint.is_anime:
                parameters['fields'] = ','.join(
                    [f.value for f in parsed_fields if f.is_anime])
            elif endpoint.is_manga:
                parameters['fields'] = ','.join(
                    [f.value for f in parsed_fields if f.is_manga])
            elif endpoint.is_character:
                parameters['fields'] = ','.join(
                    [f.value for f in parsed_fields if f.is_character])
            if endpoint.is_list:
                parameters['fields'] += ',list_status'
        else:
            if endpoint.is_anime:
                parameters['fields'] = ','.join(
                    [f.value for f in self._anime_fields])
            elif endpoint.is_manga:
                parameters['fields'] = ','.join(
                    [f.value for f in self._manga_fields])
            elif endpoint.is_character:
                parameters['fields'] = ','.join(
                    [f.value for f in self._character_fields])
            if endpoint.is_list:
                parameters['fields'] += ',list_status'
        if status is not MISSING:
            if isinstance(status, str):
                if endpoint.is_anime:
                    status = AnimeListStatus(status)
                elif endpoint.is_manga:
                    status = MangaListStatus(status)
                else:
                    raise ValueError(
                        f'status parameter {status} should not be passed to endpoint {endpoint}')
            value = status.value
            parameters['status'] = value
        if sort is not MISSING:
            if isinstance(sort, str):
                if endpoint.is_anime:
                    # can be seasonal or list
                    try:
                        sort = AnimeListSort(sort)
                    except ValueError:
                        sort = SeasonalAnimeSort(sort)
                elif endpoint.is_manga:
                    sort = MangaListSort(sort)
                else:
                    raise ValueError(
                        f'sort parameter {status} should not be passed to endpoint {endpoint}')
            value = sort.value
            parameters['sort'] = value
        # nsfw overrides the value stored in self.include_nsfw
        if nsfw is not MISSING:
            if nsfw:
                parameters['nsfw'] = 'true'
        else:
            if self.include_nsfw:
                parameters['nsfw'] = 'true'
        if board_id is not MISSING:
            parameters['board_id'] = str(board_id)
        if subboard_id is not MISSING:
            parameters['subboard_id'] = str(subboard_id)
        if limit is not MISSING:
            parameters['limit'] = str(self._get_limit(endpoint, limit))
        if offset is not MISSING:
            parameters['offset'] = str(offset)
        if topic_user_name is not MISSING:
            parameters['topic_user_name'] = topic_user_name
        if user_name is not MISSING:
            parameters['user_name'] = user_name
        return parameters

    def _get_limit(self, endpoint: Endpoint, value: int) -> int:
        """Check that the value of the parameter limit is within
        the correct interval for the given endpoint. If the value is outside
        the closest value inside the interval is returned.
        """
        limit = 1
        if value < 1:
            limit = 1
        elif value > endpoint.limit:
            limit = endpoint.limit
        else:
            limit = value
        return limit

    def _get_as_id(self, value: Union[int, str]) -> str:
        """Returns the string representing the id that can be used
        to build the url to request. Accepts both int or an url of the
        MAL page.
        """
        if isinstance(value, int):
            return str(value)
        # extract the id from the url
        # need to extract the value between the last two slashes
        # example https://myanimelist.net/anime/16498/Shingeki_no_Kyojin -> 16498
        _ = value.split('/')
        return _[-2]
