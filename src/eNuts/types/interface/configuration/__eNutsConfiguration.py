# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration


# ==================================================================================
@runtime_checkable
class iENUTSConfiguration(iApplicationConfiguration, Protocol): 
    @property
    def theme(self) -> str: ...
    @property
    def assetFolder(self) -> str: ...
