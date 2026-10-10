# ==================================================================================================
from asyncio import CancelledError, Event, set_event_loop
from ctypes import byref, c_int, sizeof, windll
from logging import CRITICAL, WARNING, Filter, LogRecord, getLogger, root
from os import environ
from sys import platform
from typing import List

# ==================================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
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
def _applyDarkBootstrapPalette(app: QApplication) -> None:
    """Fill the gap between HWND map and first QSS paint (white flash on Windows)."""
    lBg = QColor("#1e1e1e")
    lFg = QColor("#e0e0e0")
    lPal = QPalette()
    lPal.setColor(QPalette.ColorRole.Window, lBg)
    lPal.setColor(QPalette.ColorRole.WindowText, lFg)
    lPal.setColor(QPalette.ColorRole.Base, lBg)
    lPal.setColor(QPalette.ColorRole.Text, lFg)
    lPal.setColor(QPalette.ColorRole.Button, lBg)
    lPal.setColor(QPalette.ColorRole.ButtonText, lFg)
    app.setPalette(lPal)
    app.setStyle("Fusion")


def _enableWinDarkTitleBar(hwnd: int) -> None:
    """Prefer dark immersive title bar so the chrome matches the body on first map."""
    if platform != "win32" or not hwnd:
        return
    try:
        lAttr = c_int(20)
        lValue = c_int(1)
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd, lAttr, byref(lValue), sizeof(lValue)
        )
    except Exception:
        try:
            lAttr = c_int(19)
            lValue = c_int(1)
            windll.dwmapi.DwmSetWindowAttribute(
                hwnd, lAttr, byref(lValue), sizeof(lValue)
            )
        except Exception:
            pass


# ==================================================================================================
async def main(app: QApplication, *args, **kwargs):
    """Layer 0b: bare window + anti-flash bootstrap (palette / dark title bar)."""
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()

    lShutdownEvent: Event = Event()

    def _onAboutToQuit() -> None:
        lShutdownEvent.set()

    app.aboutToQuit.connect(_onAboutToQuit)
    app.setQuitOnLastWindowClosed(False)

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        _applyDarkBootstrapPalette(app)

        styleSheets: List[str] = loadStyleSheet(cfg.themePath, cfg.style)
        applyStyleSheet(app, styleSheets)

        lWin: MainWindow = MainWindow(*args, **kwargs)
        lWin.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lWin.setAutoFillBackground(True)

        if platform == "win32":
            lWin.winId()
            _enableWinDarkTitleBar(int(lWin.winId()))

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
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)

    loop.set_debug(False)
    _silenceAsyncioLogs()

    set_event_loop(loop)
    _silenceAsyncioLogs()

    with loop:
        loop.run_until_complete(main(app))


# ==================================================================================================
if __name__ == "__main__":
    program()
