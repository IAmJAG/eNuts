# ==================================================================================================
# src/eNuts/apps/main.py
# ==================================================================================================
from asyncio import CancelledError, Event, set_event_loop
from ctypes import windll
from sys import platform

# ==================================================================================================
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

# ==================================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration

# ==================================================================================================
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration
from ..UI.windows import MainWindow


# ==================================================================================================
async def _training(app: QApplication, *args, **kwargs):
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()

    lShutdownEvent: Event = Event()

    def _onAboutToQuit() -> None:
        lShutdownEvent.set()

    app.aboutToQuit.connect(_onAboutToQuit)
    app.setQuitOnLastWindowClosed(True)

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        lWin: MainWindow = MainWindow(*args, **kwargs)
        app.setStyleSheet(cfg.styleSheet)
        lWin.show()

        # Keep the event loop alive until the last window closes / aboutToQuit.
        # Note: builtins.wait is time.sleep (see __monkeyPatch); do not use it here.
        await lShutdownEvent.wait()

    except CancelledError:
        raise

    except Exception as ex:
        error(f"Unhandled exception: {type(ex).__name__}: {ex}")

    finally:
        debug("entering finally")
        if not lShutdownEvent.is_set():
            lShutdownEvent.set()
        debug("leaving finally")

    app.quit()

# ==================================================================================================
def program(*args):
    debug("App Main Started")
    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)

    set_event_loop(loop)
    with loop:
        loop.run_until_complete(_training(app))

# ==================================================================================================
if __name__ == "__main__":
    program()
