from typing import Protocol


class Identifiable(Protocol):
    @property
    def identifier(self) -> str: ...
