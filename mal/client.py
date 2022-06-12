"""Module in charge of making requests to the API and managing possible errors."""
import requests
import logging
from typing import Any, List, Dict, Optional, Sequence, Union

from .endpoints import Endpoint
from .anime import Anime, AnimeSearchResults, AnimeList, AnimeRanking, Seasonal
from .manga import Manga, MangaSearchResults, MangaList, MangaRanking
from .forum import BoardCategory, ForumTopics, Discussion
from .enums import (Field, AnimeListStatus, MangaListStatus, Season,
                    AnimeRankingType, MangaRankingType, AnimeListSort, MangaListSort)
from .utils import MISSING

_log = logging.getLogger(__name__)

class Client:
    """Offers the interface to make requests."""

    def __init__(self, client_id: str):
        self.__client_id: str = client_id
        self._session: requests.Session = requests.Session()
        self._session.headers.update({'X-MAL-CLIENT-ID': self.__client_id})
        self._search_limit: int = 10  # between 1 and 100
        self._anime_fields: List[Field] = Field.default_anime()
        self._manga_fields: List[Field] = Field.default_manga()
        self._include_nsfw: bool = False

    @property
    def search_limit(self) -> int:
        """Maximum number of results per page. Defaults to 10. Can be changed
        with any integer between 1 and 100. If a number outside of this range
        is given then the value is set to the closest value inside the range.
        """
        return self._search_limit

    @search_limit.setter
    def search_limit(self, value: int) -> None:
        self._search_limit = value if 0 < value < 100 else 100
        _log.info(f'parameter "search_limit" default value set to {self._search_limit}')

    @property
    def anime_fields(self) -> List[Field]:
        """Current fields that are requested in a anime query. Change this to change the
        fields that are requested.
        To change fields only for one request you should pass them to the search instead.
        """
        return self._anime_fields

    @anime_fields.setter
    def anime_fields(self, new_fields: Sequence[Union[Field, str]]) -> None:
        self._anime_fields = Field.from_list(new_fields)
        _log.info(f'parameter "anime_fields" default value set to {self.anime_fields}')

    @property
    def manga_fields(self) -> List[Field]:
        """Current fields that are requested in a manga query. Change this to change the
        fields that are requested.
        To change fields only for one request you should pass them to the search instead.
        """
        return self._manga_fields

    @manga_fields.setter
    def manga_fields(self, new_fields: Sequence[Union[Field, str]]) -> None:
        self._manga_fields = Field.from_list(new_fields)
        _log.info(f'parameter "manga_fields" default value set to {self.manga_fields}')

    @property
    def include_nsfw(self) -> bool:
        """Whether searches and lists include titles marked as nsfw. Defaults to False.
        Can be also specified for each query using the corresponding keyword, overriding
        this setting.
        """
        return self._include_nsfw

    @include_nsfw.setter
    def include_nsfw(self, value: bool) -> None:
        self._include_nsfw = value
        _log.info(f'parameter "nsfw" default value set to {value}')

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
            query: string used to search titles, minimum length 3 characters

        Keyword args:
            limit: maximum number of results, needs to be between 1 and 100
            offset: get results at a certain offset from the start, defaults to 0
            fields: the fields that are going to be requested, for a complete list see Field enum
            include_nsfw: include results marked as nsfw

        Returns:
            AnimeSearchResults: iterable object containing the results
        """
        parameters = self._build_search_parameters(
            Endpoint.ANIME, limit=limit, offset=offset, fields=fields, nsfw=include_nsfw)
        parameters['q'] = query
        url: str = Endpoint.ANIME.url
        response = self._request(url, params=parameters)
        data = response.json()
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
            query: string used to search titles, minimum length 3 characters

        Keyword args:
            limit: maximum number of results, needs to be between 1 and 100
            offset: get results at a certain offset from the start, defaults to 0
            fields: the fields that are going to be requested, for a complete list see Field enum
            include_nsfw: include results marked as nsfw

        Returns:
            MangaSearchResults: iterable object containing the results
        """
        parameters = self._build_search_parameters(
            Endpoint.MANGA, limit=limit, offset=offset, fields=fields, nsfw=include_nsfw)
        parameters['q'] = query
        url: str = Endpoint.MANGA.url
        response = self._request(url, params=parameters)
        data = response.json()
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
        parameters = self._build_search_parameters(
            Endpoint.ANIME, fields=fields)
        url: str = Endpoint.ANIME.url + '/' + self._get_as_id(id)
        response = self._request(url, params=parameters)
        data = response.json()
        return Anime(data)

    def get_manga(self, id: Union[int, str], *, fields: Sequence[Union[Field, str]] = MISSING) -> Manga:
        """Get the details for a specific manga given the id.

        Args:
            id: the id of the manga or the url of its MAL page

        Keyword args:
            fields: list of fields to retrieve for this request

        Returns:
            Manga: the anime object with all the details
        """
        parameters = self._build_search_parameters(
            Endpoint.ANIME, fields=fields)
        url: str = Endpoint.MANGA.url + '/' + self._get_as_id(id)
        response = self._request(url, params=parameters)
        data = response.json()
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
        parameters = self._build_list_paramenters(
            Endpoint.USER_ANIMELIST, limit=limit, offset=offset, fields=fields, status=status, nsfw=include_nsfw, sort=sort)
        url = Endpoint.USER_ANIMELIST.url.replace('{username}', username)
        response = self._request(url, params=parameters)
        data = response.json()
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
        parameters = self._build_list_paramenters(
            Endpoint.USER_MANGALIST, limit=limit, offset=offset, fields=fields, status=status, nsfw=include_nsfw, sort=sort)
        url = Endpoint.USER_MANGALIST.url.replace('{username}', username)
        response = self._request(url, params=parameters)
        data = response.json()
        return MangaList(data)

    def get_seasonal_anime(
        self,
        year: int,
        season: Union[str, Season],
        *,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        include_nsfw: bool = MISSING
    ) -> Seasonal:
        """Returns the list of anime aired during a specific season.

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
            include_nsfw: include results marked as nsfw

        Returns:
            Seasonal: container for the results, sorted by score
        """
        parameters = self._build_search_parameters(
            Endpoint.ANIME_SEASONAL, limit=limit, offset=offset, fields=fields, nsfw=include_nsfw)
        parameters['sort'] = 'anime_score'  # TODO: make it customizable
        url = f'{Endpoint.ANIME_SEASONAL}/{year}/{season}'
        response = self._request(url, params=parameters)
        data = response.json()
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
        parameters = self._build_search_parameters(
            Endpoint.ANIME_RANKING, limit=limit, offset=offset, fields=fields)
        if isinstance(ranking_type, str):
            ranking_type = AnimeRankingType(ranking_type)
        parameters['ranking_type'] = f'{ranking_type}'
        url: str = Endpoint.ANIME_RANKING.url
        response = self._request(url, params=parameters)
        data = response.json()
        return AnimeRanking(data, ranking_type)

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
        parameters = self._build_search_parameters(
            Endpoint.MANGA_RANKING, limit=limit, offset=offset, fields=fields)
        if isinstance(ranking_type, str):
            ranking_type = MangaRankingType(ranking_type)
        parameters['ranking_type'] = f'{ranking_type}'
        url: str = Endpoint.MANGA_RANKING.url
        response = self._request(url, params=parameters)
        data = response.json()
        return MangaRanking(data, ranking_type)

    def get_boards(self) -> Sequence[BoardCategory]:
        """Returns a list of the forum boards divided by category."""
        url: str = Endpoint.FORUM_BOARDS.url
        response = self._request(url)
        data = response.json()
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
        parameters = self._build_topic_parameters(Endpoint.FORUM_TOPICS, query=query, board_id=board_id,
                                                  subboard_id=subboard_id, limit=limit, offset=offset,
                                                  topic_user_name=topic_user_name, user_name=user_name)
        url: str = Endpoint.FORUM_TOPICS.url
        response = self._request(url, params=parameters)
        data = response.json()
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
        response = self._request(url, params=parameters)
        data = response.json()
        return Discussion(data['data'])

    def get_url(self, url: Optional[str]) -> Any:
        """Get the raw json data from the given url. Mostly for internal use."""
        if url is None:
            return None
        response = self._session.get(url)
        _log.info(f'Fetching url: {url}')
        if response.status_code != requests.codes.ok:
            _log.error(f'Request to {url} errored with code {response.status_code}')
            response.raise_for_status()
        return response.json()

    def _request(self, url: str, params: Dict[str, str] = MISSING) -> requests.Response:
        """Handles all the requests that are made and checks the status code of the response.
        If a requests raises an exception it is propagated.
        """
        if params is not MISSING:
            response = self._session.get(url, params=params)
        else:
            response = self._session.get(url)
        if response.status_code != requests.codes.ok:
            _log.error(f'Request to {url} with parameters {params} errored with code {response.status_code}')
            response.raise_for_status()  # TODO: handle error and possible retries
        return response

    def _build_search_parameters(
        self,
        endpoint: Endpoint,
        *,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        nsfw: bool = MISSING
    ) -> Dict[str, str]:
        parameters: Dict[str, str] = {}
        if limit is not MISSING:
            parameters['limit'] = str(self._get_limit(endpoint, limit))
        else:
            parameters['limit'] = str(self._search_limit)
        if offset is not MISSING:
            parameters['offset'] = str(offset)
        if fields is not MISSING:
            parsed_fields = Field.from_list(fields)
            if endpoint.is_anime:
                parameters['fields'] = ','.join(
                    [f.value for f in parsed_fields if f.is_anime])
            else:
                parameters['fields'] = ','.join(
                    [f.value for f in parsed_fields if f.is_manga])
        else:
            if endpoint.is_anime:
                parameters['fields'] = ','.join(
                    [f.value for f in self._anime_fields])
            else:
                parameters['fields'] = ','.join(
                    [f.value for f in self._manga_fields])
        # nsfw overrides the value stored in self.include_nsfw
        if nsfw is MISSING:
            if self.include_nsfw:
                parameters['nsfw'] = 'true'
        elif nsfw:
            parameters['nsfw'] = 'true'
        return parameters

    def _build_list_paramenters(
        self,
        endpoint: Endpoint,
        *,
        limit: int = MISSING,
        offset: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        status: Union[AnimeListStatus, MangaListStatus, str] = MISSING,
        sort: Union[AnimeListSort, MangaListSort, str] = MISSING,
        nsfw: bool = MISSING
    ) -> Dict[str, str]:
        parameters: Dict[str, str] = {}
        if limit is not MISSING:
            parameters['limit'] = str(self._get_limit(endpoint, limit))
        if offset is not MISSING:
            parameters['offset'] = str(offset)
        if fields is not MISSING:
            parsed_fields = Field.from_list(fields)
            if endpoint.is_anime:
                parameters['fields'] = ','.join(
                    [f.value for f in parsed_fields if f.is_anime])
            else:
                parameters['fields'] = ','.join(
                    [f.value for f in parsed_fields if f.is_manga])
            parameters['fields'] += ',list_status'
        else:
            parameters['fields'] = 'list_status'
        if status is not MISSING:
            if isinstance(status, str):
                value = status
            else:
                value = status.value
            parameters['status'] = value
        if sort is not MISSING:
            if isinstance(sort, str):
                value = sort   # NOTE: default sort is by title
            else:
                value = sort.value
            parameters['sort'] = value
        # nsfw overrides the value stored in self.include_nsfw
        if nsfw is MISSING:
            if self.include_nsfw:
                parameters['nsfw'] = 'true'
        elif nsfw:
            parameters['nsfw'] = 'true'
        return parameters

    def _build_topic_parameters(
        self,
        endpoint: Endpoint,
        *,
        query: str = MISSING,
        board_id: int = MISSING,
        subboard_id: int = MISSING,
        limit: int = MISSING,
        offset: int = MISSING,
        topic_user_name: str = MISSING,
        user_name: str = MISSING
    ) -> Dict[str, str]:
        parameters: Dict[str, str] = {}
        if query is not MISSING:
            parameters['q'] = query
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
        if not parameters:
            raise ValueError(
                'At least one parameter must be specified to search topics.')
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
