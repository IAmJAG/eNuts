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
from ..application import eNutsApplication
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration
from ..UI.windows import MainWindow


# ==================================================================================================
async def main(app: eNutsApplication, *args, **kwargs):
    cfg: iENUTSConfiguration | iApplicationConfiguration = eNutsConfiguration()

    shutdownEvent: Event = Event()

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        app.setStyleSheet(cfg.theme)

        lWin: MainWindow = MainWindow(shutdownEvent, *args, **kwargs)        
        lWin.show()

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
    app: eNutsApplication = eNutsApplication()
    loop: QEventLoop = QEventLoop(app)
    set_event_loop(loop)
    
    with loop:
        loop.run_until_complete(main(app))


# ==================================================================================================
if __name__ == "__main__":
    program()
