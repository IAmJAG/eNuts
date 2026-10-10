# ==================================================================================
from jAGQt.window import MainWindowBase

# ==================================================================================
from ...configuration import ApplicationInformation


# ==================================================================================
class MainWindow(MainWindowBase, ApplicationInformation):
    """Layer 0 — bare window. No workflow chain, no Shell chrome, no devices.

    Build-up order (re-add only after the previous layer is flicker-free):
      L0  this class + main show
      L1  settings / geometry (sync, same thread)
      L2  central layout + one placeholder widget
      L3  SideBar
      L4  Workspace / pages
      L5  streamer view
      L6  device discovery + StreamPipeline (post-show, non-UI)
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__("ENUTS_WINDOW", *args, **kwargs)
        self.setWindowTitle("eNuts")
        self.resize(1280, 720)

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
