# ==================================================================================================
from asyncio import CancelledError, Event, set_event_loop
from ctypes import windll
from sys import platform
from typing import List

# ==================================================================================================
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

# ==================================================================================================
from jAGFx.types.interface.configuration import iApplicationConfiguration

# ==================================================================================================
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration
from ..UI.windows import MainWindow
from ..utilities import (
    applyDarkBootstrapPalette,
    applyStyleSheet,
    enableWinDarkTitleBar,
    loadStyleSheet,
)


# ==================================================================================================
async def initializeWindow(shutdownEvent: Event, *args, **kwargs):
    win: MainWindow = MainWindow(shutdownEvent, *args, **kwargs)
    win.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    win.setAutoFillBackground(True)

    if platform == "win32":
        win.winId()
        enableWinDarkTitleBar(int(win.winId()))

    return win

# ==================================================================================================
async def main(app: QApplication, *args, **kwargs):
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()
    
    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        shutdownEvent: Event = Event()
        applyDarkBootstrapPalette(app)
        
        styleSheets: List[str] = loadStyleSheet(cfg.themePath, cfg.style)
        applyStyleSheet(app, styleSheets)

        win: MainWindow = await initializeWindow(shutdownEvent, *args, **kwargs)
        win.show()        

        app.setQuitOnLastWindowClosed(True)
        await shutdownEvent.wait()

    except CancelledError:
        pass

    except Exception as ex:
        error(f"[main] Error occur {str(ex)}", ex)

    finally:
        if not shutdownEvent.is_set(): shutdownEvent.set()

    app.quit()


# ==================================================================================================
def program(*args):
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    app: QApplication = QApplication()
    loop: QEventLoop = QEventLoop(app)

    loop.set_debug(False)
    set_event_loop(loop)
    
    with loop:
        loop.run_until_complete(main(app))


# ==================================================================================================
if __name__ == "__main__":
    program()
