# ==================================================================================================
from asyncio import AbstractEventLoop, Task, get_event_loop, get_running_loop
from inspect import iscoroutinefunction
from typing import Any, Awaitable, Callable


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
def _getCoroutine(func: Callable) -> Callable[..., Any]:    
    async def _task(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
            
        except Exception as ex:
            raise ex

    return _task

# ==================================================================================================
def createTask(func: Callable[[...], Awaitable], *args, **kwargs) -> Task:
    try:
        loop: AbstractEventLoop = getRunningLoop()
        if loop is None: raise Exception("No running loop")

        asyncFunc: Callable[[...], Awaitable] = func
        if not iscoroutinefunction(func):
            asyncFunc = _getCoroutine(asyncFunc)
            
        return loop.create_task(asyncFunc, *args, **kwargs)

    except Exception as ex:
        raise ex