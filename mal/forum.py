from typing import List

from .typed import SubBoardPayload, BoardPayload, BoardCategoryPayload


class SubBoard:
    """Represent a subboard of a forum board.

    Attributes:
        id: the id of the subboard
        title: the title of the subboard
    """

    def __init__(self, data: SubBoardPayload) -> None:
        self.id: int = data['id']
        self.title: str = data['title']


class Board:
    """Represents a forum board.

    Attributes:
        id: the id of the board
        title: the title of the board
        description: the description of the board
        subboards: list of all the subboards of the current board
    """

    def __init__(self, data: BoardPayload) -> None:
        self.id: int = data['id']
        self.title: str = data['title']
        self.description: str = data['description']
        self.subboards: List[SubBoard] = []
        for subboard in data['subboards']:
            self.subboards.append(SubBoard(subboard))


class BoardCategory:
    """Boards grouped by category.

    Attributes:
        title: the name of this cateogry
        boards: list of boards belonging to this category
    """

    def __init__(self, data: BoardCategoryPayload) -> None:
        self.title: str = data['title']
        self.boards: List[Board] = []
        for board in data['boards']:
            self.boards.append(Board(board))
