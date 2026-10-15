# ==================================================================================================
from asyncio import CancelledError, set_event_loop
from asyncio import Event as asyncEvent

# ==================================================================================================
from qasync import QEventLoop
from rich import inspect, print

# ==================================================================================================
from ..application import ApplicationInformation, Shell, eNutsApplication
from ..configuration import eNutsConfiguration
from ..types.interface.configuration import iENUTSConfiguration


# ==================================================================================================
async def main(app: eNutsApplication, *args, **kwargs):    
    try:
        shutdownEvent: asyncEvent = asyncEvent()
        cfg: iENUTSConfiguration = eNutsConfiguration()        
        await app.asyncSetStyeSheet(cfg.theme)        

        win: Shell = Shell(shutdownEvent, cfg) 
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
