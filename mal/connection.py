"""Module that handles requests to the API and errors."""
import time
import requests
import logging

from typing import Any, Dict
from .utils import MISSING

_log = logging.getLogger(__name__)


class APICallManager:
    """Performs the API calls managing error states and delay between requests. This should not be
    instantiated directly, it is created by the Client and managed through it."""

    def __init__(self, client_id: str):
        self.__client_id: str = client_id
        self._session: requests.Session = requests.Session()
        self._session.headers.update({'X-MAL-CLIENT-ID': self.__client_id})
        self.delay: float = 1.0
        self._next_request_at: float = time.time()
        _log.info(f'Created APICallManager')

    def api_call(self, url: str, params: Dict[str, str] = MISSING) -> Any:
        """Handles all the requests that are made and checks the status code of the response.
        If a requests raises an exception it is propagated. Automatically inserts the configured delay
        in between requests.

        Args:
            url: the url to be requested
            params: dictionary containing the url parameters

        Returns:
            Any: json data returned by the API

        Raises:
            HTTPError: raised if an error occurred in the request
        """
        # checks if delay has passed, if not waits until the end
        wait_time = self._next_request_at - time.time()
        if wait_time > 0:
            time.sleep(wait_time)
        if params is not MISSING:
            response = self._session.get(url, params=params)
        else:
            response = self._session.get(url)
        # updates time for next request
        self._next_request_at += self.delay
        # checks response and returns the json
        if response.status_code != requests.codes.ok:
            _log.error(
                f'Request to {url} with parameters {params} errored with code {response.status_code}')
            response.raise_for_status()  # TODO: handle error and possible retries
        return response.json()
