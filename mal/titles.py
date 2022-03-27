from .utils import MISSING
from .typed import TitlesPayload

from typing import List, Optional


class Titles:
    """Contains the information about the alternative titles for an anime
    or a manga, including different languages.

    Attributes:
        title: The title of the work.
        synonyms: A list of alternative titles.
        en_title: Official english title.
        ja_title: Official japanese title.
    """

    def __init__(self, title: str, payload: TitlesPayload):
        self.title: str = title
        if payload is not MISSING:
            self.synonyms: Optional[List[str]] = payload.get('synonyms', [])
            self.en_title: Optional[str] = payload.get(
                'en', 'english title not present.')
            self.ja_title: Optional[str] = payload.get(
                'ja', 'japanese title not present.')
        else:
            self.synonyms = None
            self.en_title = None
            self.ja_title = None
