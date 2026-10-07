# ==================================================================================================
# src/eNuts/apps/main.py
# ==================================================================================================
from asyncio import CancelledError, Event, set_event_loop
from ctypes import windll
from os import path
from sys import platform
from typing import List

# ==================================================================================================
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

# ==================================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration

# ==================================================================================================
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration
from ..UI.windows import MainWindow
from ..utilities import applyStyleSheet, loadStyleSheet


# ==================================================================================================
async def main(app: QApplication, *args, **kwargs):
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()
    
    lShutdownEvent: Event = Event()

    def _onAboutToQuit() -> None: lShutdownEvent.set()
    app.aboutToQuit.connect(_onAboutToQuit)
    app.setQuitOnLastWindowClosed(False)

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        styleSheets: List[str] = loadStyleSheet(cfg.themePath, cfg.style)
        applyStyleSheet(app, styleSheets)

        lWin: MainWindow = MainWindow(*args, **kwargs)        
        lWin.show()

        app.setQuitOnLastWindowClosed(True)

        await lShutdownEvent.wait()

    except CancelledError:
        pass

    except Exception as ex:
        error(f"[main] Error occur {str(ex)}", ex)

    finally:
        if not lShutdownEvent.is_set():
            lShutdownEvent.set()

    app.quit()

# ==================================================================================================
def program(*args):
    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)

    set_event_loop(loop)
    with loop:
        loop.run_until_complete(main(app))


# ==================================================================================================
if __name__ == "__main__":
    program()
