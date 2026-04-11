from typing import Any, Protocol


class Identifiable(Protocol):
    @property
    def identifier(self) -> str: ...


class PredicateFn[TVal](Protocol):
    def __call__(self, val: TVal, *args: Any, **kwds: Any) -> bool: ...


class ValidatorFn[TVal](Protocol):
    def __call__(self, val: TVal) -> TVal: ...
