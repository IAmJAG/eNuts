# ==================================================================================================
# src/eNuts/apps/main.py
# ==================================================================================================
from asyncio import FIRST_COMPLETED, CancelledError, Event, create_task, set_event_loop
from ctypes import windll
from sys import argv, platform

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

    shutdownEvent: Event = Event()
    shutdownTask = create_task(shutdownEvent.wait(), name="ApplicationShutdown")
    app.setQuitOnLastWindowClosed(False)

    if platform == "win32":
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

    try:
        win: MainWindow = MainWindow(*args, **kwargs)
        app.setStyleSheet(cfg.styleSheet)
        win.show()

        await wait((shutdownTask,), return_when=FIRST_COMPLETED)

    except CancelledError:
        raise

    except Exception as ex:
        error(f"Unhandled exception: {type(ex).__name__}: {ex}")

    finally:
        debug("entering finally")        
        if not shutdownTask.done():
            shutdownTask.cancel()
            try:
                await shutdownTask
                
            except CancelledError: pass

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