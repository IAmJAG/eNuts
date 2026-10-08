# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
# Import enum submodule only (not action.android package __init__)
from ....action.android.enums.__eCommands import eCommandType
from ..sockets import iControlSocket
from .__actionMetadata import iActionMetadata


# ==================================================================================
@runtime_checkable
class iAndroidAction(iActionMetadata, Protocol):
    def __init__(
        self, name: str = None, commandType: eCommandType = eCommandType.UNKNOWN
    ): ...

    def execute(self, control: iControlSocket, payload: bytes): ...
