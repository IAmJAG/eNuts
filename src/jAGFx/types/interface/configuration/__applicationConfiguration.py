# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from .__configuration import iConfiguration


# ==================================================================================
@runtime_checkable
class iApplicationConfiguration(iConfiguration, Protocol):
    def __init__(
        self, title: str = "", company: str = "",
        applicationId: str = "", logo: str = ""
    ) -> None: ...
    
    @property
    def updatedAttributes(self) -> set: ...
    @property
    def isDirty(self) -> bool: ...
    
    @property
    def title(self) -> str: ...
    @property
    def company(self) -> str: ...
    @property
    def applicationId(self) -> str: ...
    @property
    def logo(self) -> str: ...
