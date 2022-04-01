from .typed import GenericPayload


class Genre():
    """Represents a specific genre. It has two read only properties that are the
    id and the name of the genre.

    Attributes:
        id: The id of the genre.
        name: The name of the genre.
    """

    def __init__(self, data: GenericPayload) -> None:
        self.id: int = data['id']
        self.name: str = data['name']

    def __str__(self) -> str:
        return self.name
