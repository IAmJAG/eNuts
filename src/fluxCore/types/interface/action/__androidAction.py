# ==================================================================================
from typing import Any, Protocol, runtime_checkable

# ==================================================================================
from ....action.android.enums import eCommandType
from ..sockets import iControlSocket
from .__actionMetadata import iActionMetadata


# ==================================================================================
class iAndroidAction(iActionMetadata, Protocol):
    def __init__(self, name: str = None, commandType: eCommandType = eCommandType.UNKNOWN): ...
    def execute(self, control: iControlSocket, payload: bytes): ...
