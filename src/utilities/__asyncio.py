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
def createTask(func: Callable[..., Any], *args, **kwargs) -> Task:
    """Schedule ``func`` on the running loop.

    ``loop.create_task`` requires a **coroutine object**, not a coroutine function
    or a plain callable. This helper:

    - coroutine function → ``create_task(func(*args, **kwargs))``
    - plain callable     → wrap in a one-shot coroutine, then schedule
    """
    try:
        loop: AbstractEventLoop = getRunningLoop()
        if loop is None:
            raise Exception("No running loop")

        if iscoroutinefunction(func):
            return loop.create_task(func(*args, **kwargs))

        async def _runner() -> Any:
            return func(*args, **kwargs)

        return loop.create_task(_runner())

    except Exception as ex:
        raise ex
