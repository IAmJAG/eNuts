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
from jAGQt.types import ShowAnimation

# ==================================================================================================
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration
from ..UI.windows import MainWindow


# ==================================================================================================
async def _training(app: QApplication, *args, **kwargs):
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()

    lShutdownEvent: Event = Event()

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    lWin: MainWindow = MainWindow(*args, **kwargs)
    app.setStyleSheet(cfg.styleSheet)
    lWin.show()

    try:
        await lShutdownEvent.wait()

    except CancelledError:
        raise

    except Exception as ex:
        raise ex

    finally:
        if not lShutdownEvent.is_set(): lShutdownEvent.set()

    app.quit()


# ==================================================================================================
def program(*args):
    try:
        app: QApplication = QApplication()
        loop: QEventLoop = QEventLoop(app)
        set_event_loop(loop)
        with loop:
            loop.run_until_complete(_training(app, *args))

    except Exception as ex:
        raise ex


# ==================================================================================================
if __name__ == "__main__":
    program()
