# ==================================================================================
from asyncio import Event as asyncEvent

# ==================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration
from jAGFx.workflow import workflow

# ==================================================================================
from ...application import Shell
from ...configuration import eNutsConfiguration
from ...types.interface.configuration import iENUTSConfiguration
from ...types.interface.UI.windows import iENUTSWindow


# ==================================================================================
@workflow(
    "InitializeSettings",
    "InitializeInfo",
    "InitializeUI",
    "RestoreWindowsState",
)
class ENUTSWindow(Shell, iENUTSWindow):
    OBJECT_NAME = "W_ENUTS_WINDOW"

    def __init__(
        self,
        shutdownEvent: asyncEvent,
        cfg: iApplicationConfiguration = eNutsConfiguration(),
        *args,
        **kwargs,
    ) -> None:
        super().__init__(shutdownEvent, cfg, *args, **kwargs)
