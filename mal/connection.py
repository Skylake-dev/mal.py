"""Module that handles requests to the API and errors."""
import requests
import logging

from typing import Any, Dict
from .utils import MISSING

_log = logging.getLogger(__name__)


class APICallManager:

    def __init__(self, client_id: str):
        self.__client_id: str = client_id
        self._session: requests.Session = requests.Session()
        self._session.headers.update({'X-MAL-CLIENT-ID': self.__client_id})
        _log.info(f'Created APICallManager')

    def api_call(self, url: str, params: Dict[str, str] = MISSING) -> Any:
        """Handles all the requests that are made and checks the status code of the response.
        If a requests raises an exception it is propagated.
        """
        if params is not MISSING:
            response = self._session.get(url, params=params)
        else:
            response = self._session.get(url)
        if response.status_code != requests.codes.ok:
            _log.error(
                f'Request to {url} with parameters {params} errored with code {response.status_code}')
            response.raise_for_status()  # TODO: handle error and possible retries
        return response.json()
