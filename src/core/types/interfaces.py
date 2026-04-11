from typing import Any, Protocol


class Identifiable(Protocol):
    @property
    def identifier(self) -> str: ...


class ValidatorFn[T](Protocol):
    def __call__(self, val: T, *args: Any, **kwds: Any) -> bool: ...
