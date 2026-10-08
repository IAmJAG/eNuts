# ==================================================================================
from typing import Any, Protocol, runtime_checkable

# ==================================================================================
from ..sockets import iControlSocket
from .__actionMetadata import iActionMetadata


# ==================================================================================
@runtime_checkable
class iAndroidAction(iActionMetadata, Protocol):
    # commandType is eCommandType at runtime; typed as Any here to avoid importing
    # fluxCore.action (which would re-enter this package during init).
    def __init__(self, name: str = None, commandType: Any = None): ...

    def execute(self, control: iControlSocket, payload: bytes): ...
