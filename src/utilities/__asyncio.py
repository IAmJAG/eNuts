# ==================================================================================================
# src/utilities/__asyncio.py
# ==================================================================================================
from asyncio import AbstractEventLoop, Task, get_event_loop, get_running_loop
from asyncio import run as runAsync


# ==================================================================================================
def getRunningLoop() -> AbstractEventLoop:
    try:
        return get_running_loop()

    except RuntimeError:
        return None

    except Exception as ex:
        raise ex

# ==================================================================================================
def getEventLoop() -> AbstractEventLoop:
    try:
        return get_event_loop()

    except RuntimeError:
        return None

    except Exception as ex:
        raise ex

# ==================================================================================================
def createTask(func: callable, *args, **kwargs) -> Task:
    try:
        loop: AbstractEventLoop = getRunningLoop()
        if loop is None: raise Exception("No running loop")  
        
        return loop.create_task(func(*args, **kwargs))

    except Exception as ex:
        raise ex