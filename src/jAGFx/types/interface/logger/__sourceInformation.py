# ==================================================================================
# src/jAGFx/contracts/logger/__sourceContext.py
# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iSourceInformation(Protocol):
    def __init__(self) -> None: ...

    @property
    def FullyQualifiedName(self): ...

    @property
    def Module(self) -> str: ...

    @property
    def Class(self) -> str: ...

    @property
    def Member(self) -> str: ...

    @property
    def Package(self) -> str: ...

    @property
    def File(self) -> str: ...