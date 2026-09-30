# ==================================================================================================
# src/utilities/__asyncio.py
# ==================================================================================================
from asyncio import AbstractEventLoop, Task, get_event_loop, get_running_loop
from typing import Awaitable, Callable


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
        loop: AbstractEventLoop = get_event_loop()
        if loop is None: raise Exception("No event loop")
        return loop

    except RuntimeError:
        return None

    except Exception as ex:
        raise ex

# ==================================================================================================
def createTask(asyncFunc: Callable[[...], Awaitable], *args, **kwargs) -> Task:
    try:
        loop: AbstractEventLoop = getRunningLoop()
        if loop is None: raise Exception("No running loop")
        return loop.create_task(asyncFunc(*args, **kwargs))

    except Exception as ex:
        raise ex