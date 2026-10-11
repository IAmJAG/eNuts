# ==================================================================================================
from asyncio import CancelledError, Event, set_event_loop
from ctypes import windll
from logging import DEBUG
from sys import platform
from typing import List

# ==================================================================================================
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

# ==================================================================================================
from jAGFx.logging import setNamespaceLevel
from jAGFx.types.interface.configuration import iApplicationConfiguration

# ==================================================================================================
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration
from ..UI.windows import MainWindow
from ..utilities import applyStyleSheet, loadStyleSheet


# ==================================================================================================
async def main(app: QApplication, *args, **kwargs):
    """Layer 0 bootstrap: app + style + one window + show. Nothing else."""
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()

    
    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        styleSheets: List[str] = loadStyleSheet(cfg.themePath, cfg.style)
        applyStyleSheet(app, styleSheets)
        shutdownEvent: Event = Event()
        lWin: MainWindow = MainWindow(shutdownEvent)
        lWin.show()

        app.setQuitOnLastWindowClosed(True)
        await shutdownEvent.wait()

    except CancelledError:
        pass

    except Exception as ex:
        error(f"[main] Error occur {str(ex)}", ex)

    finally:
        if not shutdownEvent.is_set():
            shutdownEvent.set()

    app.quit()


# ==================================================================================================
def program(*args):
    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)

    loop.set_debug(False)
    set_event_loop(loop)
    
    with loop:
        loop.run_until_complete(main(app))


# ==================================================================================================
if __name__ == "__main__":
    program()
