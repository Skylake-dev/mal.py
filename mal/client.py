"""Module in charge of making requests to the API and managing possible errors."""
import requests
from typing import List, Dict, Sequence, Union

from .endpoints import Endpoint
from .anime import Anime, AnimeSearchResults, AnimeList, AnimeRanking, Seasonal
from .manga import Manga, MangaSearchResults, MangaList, MangaRanking
from .enums import Field, AnimeListStatus, MangaListStatus, Season, AnimeRankingType, MangaRankingType
from .utils import MISSING


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

    def anime_search(
        self,
        query: str,
        *,
        limit: int = MISSING,
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
            fields: the fields that are going to be requested, for a complete list see Field enum
            include_nsfw: include results marked as nsfw

        Returns:
            AnimeSearchResults: iterable object containing the results
        """
        parameters = self._build_search_parameters(
            Endpoint.ANIME, limit=limit, fields=fields, nsfw=include_nsfw)
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
            fields: the fields that are going to be requested, for a complete list see Field enum
            include_nsfw: include results marked as nsfw

        Returns:
            MangaSearchResults: iterable object containing the results
        """
        parameters = self._build_search_parameters(
            Endpoint.MANGA, limit=limit, fields=fields, nsfw=include_nsfw)
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
        fields: Sequence[Union[Field, str]] = MISSING,
        status: Union[AnimeListStatus, str] = MISSING,
        include_nsfw: bool = MISSING
    ) -> AnimeList:
        """Returns the anime list of a specific user, if public.

        Args:
            username: the MAL username of the user, case insensitive

        Keyword args:
            limit: set the number of entries to retrieve, defaults to 10
            fields: set which fields to get for each entry
            status: return only a specific category. will return all if omitted
            include_nsfw: include results marked as nsfw

        Returns:
            AnimeList: iterable with all the entries of the list
        """
        parameters = self._build_list_paramenters(
            Endpoint.USER_ANIMELIST, limit=limit, fields=fields, status=status, nsfw=include_nsfw)
        url = Endpoint.USER_ANIMELIST.url.replace('{username}', username)
        response = self._request(url, params=parameters)
        data = response.json()
        return AnimeList(data)

    def get_manga_list(
        self,
        username: str,
        *,
        limit: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        status: Union[MangaListStatus, str] = MISSING,
        include_nsfw: bool = MISSING
    ) -> MangaList:
        """Returns the manga list of a specific user, if public.

        Args:
            username: the MAL username of the user, case insensitive

        Keyword args:
            limit: set the number of entries to retrieve, defaults to 10
            fields: set which fields to get for each entry
            status: return only a specific category. will return all if omitted
            include_nsfw: include results marked as nsfw

        Returns:
            MangaList: iterable with all the entries of the list
        """
        parameters = self._build_list_paramenters(
            Endpoint.USER_MANGALIST, limit=limit, fields=fields, status=status, nsfw=include_nsfw)
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
            fields: set which fields to get for each entry
            include_nsfw: include results marked as nsfw

        Returns:
            Seasonal: container for the results, sorted by score
        """
        parameters = self._build_search_parameters(
            Endpoint.ANIME_SEASONAL, limit=limit, fields=fields, nsfw=include_nsfw)
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
        fields: Sequence[Union[Field, str]] = MISSING
    ) -> AnimeRanking:
        """Returns the top anime in the rankings.

        Keyword args:
            ranking_type: the type of ranking to request, defaults to all.
                For all possible values see enums.AnimeRanking
            limit: numbers of entries to request
            fields: set which fields to get for each entry

        Returns:
            AnimeRanking: the results

        Raises:
            ValueError: ranking_type is invalid, check AnimeRankingType for all options
        """
        parameters = self._build_search_parameters(
            Endpoint.ANIME_RANKING, limit=limit, fields=fields)
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
        fields: Sequence[Union[Field, str]] = MISSING
    ) -> MangaRanking:
        """Returns the top manga in the rankings.

        Keyword args:
            ranking_type: the type of ranking to request, defaults to all.
                For all possible values see enums.MangaRanking
            limit: numbers of entries to request
            fields: set which fields to get for each entry

        Returns:
            MangaRanking: the results

        Raises:
            ValueError: ranking_type is invalid, check MangaRankingType for all options
        """
        parameters = self._build_search_parameters(
            Endpoint.MANGA_RANKING, limit=limit, fields=fields)
        if isinstance(ranking_type, str):
            ranking_type = MangaRankingType(ranking_type)
        parameters['ranking_type'] = f'{ranking_type}'
        url: str = Endpoint.MANGA_RANKING.url
        response = self._request(url, params=parameters)
        data = response.json()
        return MangaRanking(data, ranking_type)

    def _request(self, url: str, params: Dict[str, str] = MISSING) -> requests.Response:
        """Handles all the requests that are made and checks the status code of the response.
        If a requests raises an exception it is propagated.
        """
        if params is not MISSING:
            response = self._session.get(url, params=params)
        else:
            response = self._session.get(url)
        response.raise_for_status()  # TODO: handle error and possible retries
        return response

    def _build_search_parameters(
        self,
        endpoint: Endpoint,
        *,
        limit: int = MISSING,
        fields: Sequence[Union[Field, str]] = MISSING,
        nsfw: bool = MISSING
    ) -> Dict[str, str]:
        parameters: Dict[str, str] = {}
        if limit is not MISSING:
            parameters['limit'] = str(self._get_limit(endpoint, limit))
        else:
            parameters['limit'] = str(self._search_limit)
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
        fields: Sequence[Union[Field, str]] = MISSING,
        status: Union[AnimeListStatus, MangaListStatus, str] = MISSING,
        nsfw: bool = MISSING
    ) -> Dict[str, str]:
        parameters: Dict[str, str] = {}
        if limit is not MISSING:
            parameters['limit'] = str(self._get_limit(endpoint, limit))
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
        # nsfw overrides the value stored in self.include_nsfw
        if nsfw is MISSING:
            if self.include_nsfw:
                parameters['nsfw'] = 'true'
        elif nsfw:
            parameters['nsfw'] = 'true'
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
