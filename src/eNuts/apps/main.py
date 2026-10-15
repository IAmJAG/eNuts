# ==================================================================================================
from asyncio import CancelledError, set_event_loop
from asyncio import Event as asyncEvent
from ctypes import windll
from sys import platform

# ==================================================================================================
from qasync import QEventLoop
from rich import inspect, print

# ==================================================================================================
from ..application import eNutsApplication
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration
from ..UI.windows import ENUTSWindow


# ==================================================================================================
async def main(app: eNutsApplication, *args, **kwargs):    
    try:
        cfg: iENUTSConfiguration = eNutsConfiguration()
        if platform == "win32":
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(cfg.applicationId)

        await app.asyncSetStyeSheet(cfg.theme)

        shutdownEvent: asyncEvent = asyncEvent()
        win: ENUTSWindow = ENUTSWindow(shutdownEvent, cfg) 
        win.show()

        await shutdownEvent.wait()
        
    
    except CancelledError:
        pass
 
    except Exception as ex:
        error(f"[{__name__}] Error occur {str(ex)}", ex)

    app.quit()

# ==================================================================================================
def program(*args):    
    app: eNutsApplication = eNutsApplication()
    loop: QEventLoop = QEventLoop(app)

    set_event_loop(loop)
    args, kwargs = ProcessArguments(args)
    
    with loop:
        loop.run_until_complete(main(app, *args, **kwargs))


# ==================================================================================================
if __name__ == "__main__":
    program()
