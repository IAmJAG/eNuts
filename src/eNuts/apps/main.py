# ==================================================================================================
from asyncio import CancelledError, Event, set_event_loop
from ctypes import windll
from logging import CRITICAL, WARNING, Filter, LogRecord, getLogger, root
from os import environ
from sys import platform
from time import sleep
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
class _AsyncioProactorNoiseFilter(Filter):
    _C_NOISE = (
        "Got events from poll",
        "Invoking event callback",
        "Using proactor",
        "is running after closing",
    )

    def filter(self, record: LogRecord) -> bool:
        if record.name.startswith("asyncio"):
            return record.levelno >= WARNING
        try:
            lMsg = record.getMessage()
        except Exception:
            return True
        for lNoise in self._C_NOISE:
            if lNoise in lMsg:
                return False
        return True


# ==================================================================================================
def _silenceAsyncioLogs() -> None:
    environ["PYTHONASYNCIODEBUG"] = "0"
    lFilter = _AsyncioProactorNoiseFilter()
    for lName in ("asyncio", "asyncio.proactor", "asyncio.windows_events"):
        lLogger = getLogger(lName)
        lLogger.setLevel(CRITICAL)
        lLogger.propagate = False
        for lHandler in list(lLogger.handlers):
            lLogger.removeHandler(lHandler)
        lLogger.addFilter(lFilter)
    root.addFilter(lFilter)
    for lHandler in list(root.handlers):
        lHandler.addFilter(lFilter)


# ==================================================================================================
async def main(app: QApplication, *args, **kwargs):
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()

    lShutdownEvent: Event = Event()

    def _onAboutToQuit() -> None:
        lShutdownEvent.set()

    app.aboutToQuit.connect(_onAboutToQuit)
    app.setQuitOnLastWindowClosed(False)

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        styleSheets: List[str] = loadStyleSheet(cfg.themePath, cfg.style)
        applyStyleSheet(app, styleSheets)

        lWin: MainWindow = MainWindow(*args, **kwargs)
        lWin.show()
        sleep(0.1)
        await lWin.initializeInstance()

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

    loop.set_debug(False)
    _silenceAsyncioLogs()

    set_event_loop(loop)
    _silenceAsyncioLogs()  # again after loop is installed

    with loop:
        loop.run_until_complete(main(app))


# ==================================================================================================
if __name__ == "__main__":
    program()
