from typing import Any


class _Missing:
    def __eq__(self, other: object) -> bool:
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 0

    def __str__(self) -> str:
        return 'MISSING'


MISSING: Any = _Missing()
