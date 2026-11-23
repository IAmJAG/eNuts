# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iSourceInformation(Protocol):
    def __init__(self) -> None: ...

    @property
    def fullyQualifiedName(self): ...

    @property
    def module(self) -> str: ...

    @property
    def klass(self) -> str: ...

    @property
    def member(self) -> str: ...

    @property
    def package(self) -> str: ...

    @property
    def file(self) -> str: ...