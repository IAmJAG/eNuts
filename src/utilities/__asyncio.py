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
        if loop is None:
            raise Exception("No event loop")
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

def logTaskException(done: Task) -> None:
    try:
        exc = done.exception()

    except Exception:
        raise
    
    if exc is not None:
        try:
            error(f"asyncio task unhandled exception name={done.get_name()!r}", exc)

        except Exception:
            raise

# ==================================================================================================
def createTask(func: Callable[..., Any], *args, **kwargs) -> Task:
    try:        
        loop: AbstractEventLoop = getRunningLoop()        
        if loop is None: raise Exception("No running loop")

        # for stub intellisense
        def runner(*args, **kwargs) -> Awaitable: ...
        runner: Callable[..., Awaitable] = func
        if not iscoroutinefunction(func): runner = _getCoroutine(func)

        task: Task = loop.create_task(runner(*args, **kwargs))
        task.add_done_callback(logTaskException)
        return task

    except Exception as ex:
        raise ex
