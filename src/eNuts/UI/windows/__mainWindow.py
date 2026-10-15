# ==================================================================================
from asyncio import Event as asyncEvent

# ==================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration
from jAGQt.window import WindowBase

# ==================================================================================
from ...configuration import eNutsConfiguration
from ...types.interface.configuration import iENUTSConfiguration
from ...types.interface.UI.windows import iENUTSWindow


# ==================================================================================
class ENUTSWindow(WindowBase, iENUTSWindow):
    OBJECT_NAME = "W_ENUTS_WINDOW"
    def __init__(self, shutdownEvent: asyncEvent,
        cfg: iApplicationConfiguration = eNutsConfiguration(),
        *args, **kwargs
    ) -> None:        
        super().__init__(*args, **kwargs)
        self._shutdownEvent: asyncEvent = shutdownEvent
        self._config: iENUTSConfiguration = cfg

    def closeEvent(self, event) -> None:
        self._shutdownEvent.set()
        super().closeEvent(event)

    @property
    def config(self) -> iENUTSConfiguration:
        return self._config
