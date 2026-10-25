# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import TYPE_CHECKING

# ==================================================================================
from ..sockets import iControlSocket
from .__actionMetadata import iActionMetadata

# ==================================================================================
if TYPE_CHECKING:
    # Import under TYPE_CHECKING only — runtime import of action.android.enums
    # pulls fluxCore.action.__init__ → Action → this package while it is still
    # loading (circular ImportError).
    from ....action.android.enums import eCommandType


# ==================================================================================
class iAndroidAction(iActionMetadata):
    def __init__(
        self,
        name: str | None = None,
        commandType: eCommandType | None = None,
    ) -> None: ...

    def execute(self, control: iControlSocket, payload: bytes) -> None: ...
