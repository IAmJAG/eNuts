# ==================================================================================
from asyncio import to_thread
from multiprocessing import Queue
from queue import Empty
from typing import Optional


# ==================================================================================
def drainQueue(queue: Queue) -> None:
    while True:
        try:
            queue.get_nowait()

        except Empty:
            break

# ==================================================================================
async def asyncDrainQueue(queue: Queue) -> None:
    await to_thread(drainQueue, queue)

# ==================================================================================
def closeQueue(queue: Optional[Queue]) -> None:
    if queue is None: return

    try:
        queue.close()
        queue.cancel_join_thread()

    except Exception:
        raise

# ==================================================================================
async def asyncCloseQueue(queue: Optional[Queue]) -> None:
    await to_thread(closeQueue, queue)