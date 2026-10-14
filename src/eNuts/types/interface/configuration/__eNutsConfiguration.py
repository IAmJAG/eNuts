# ==================================================================================
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iENUTSConfiguration[T: iENUTSConfiguration](Protocol): 
    @property
    def theme(self) -> str: ...
    @property
    def assetFolder(self) -> str: ...

    def save(self, path=None) -> T: ...
    def load(self, path=None) -> T: ...
