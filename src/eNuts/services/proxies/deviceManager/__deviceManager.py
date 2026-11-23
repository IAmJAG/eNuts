# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Task
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from typing import Dict, Optional, Union
from uuid import uuid4

# ==================================================================================
from adbutils import AdbDevice, adb

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from jAGFx.IPC.message import Handshake, Terminated
from jAGFx.types.interface.communication import iMessage

# ==================================================================================
from ....utilities.asyncADB import Devices
from ..__manager import ownDispatch, watcher
from .message import InitializeDeviceList


# ==================================================================================
async def deviceWatcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    err: Optional[Union[Exception, BaseException]] = None

    try:
        watcherTask: Task = createTask(
            watcher, shutdownEvent, _messageHandler, inQueue
        )
        discoveryTask: Task = createTask(
            _discovery, shutdownEvent, outQueue
        )        

        handShake: Handshake = Handshake(correlationId=uuid4(), messageId=uuid4())
        await ownDispatch(outQueue, handShake)
        await discoveryTask

    except Exception as ex:
        err = ex
        raise ex

    except BaseException as bex:
        err = bex
        raise bex
    
    finally:
        terminated: Terminated = Terminated(error=err)
        await ownDispatch(outQueue, terminated)

# ==================================================================================
async def _messageHandler(msg: iMessage):
    if isinstance(msg, Handshake):
        trace(f"Acknowleged {msg.ownerId}")

async def _discovery(shutdownEvent: syncEvent, queue: Queue) -> None:
    def isShuttingDown() -> bool: ...
    isShuttingDown = shutdownEvent.is_set

    async def _getDevices() -> Dict[str, iDevice]:
        found: Dict[str, iDevice] = {}
        found.update(await Devices())
        return found

    connDevices: Dict[str, iDevice] = await _getDevices()
    verbose(f"initial discovery count={len(connDevices)} ids={list(connDevices.keys())}")
    
    msgIDL: InitializeDeviceList = InitializeDeviceList(deviceList=connDevices)
    await ownDispatch(queue, msgIDL)

def runDiscovery(self) -> None:
    async def _discoveryRunner() -> None:
        try:
            await self._discovery()

        except Exception as ex:
            error("discovery FAIL", ex)

    createTask(_discoveryRunner)
    verbose("runDiscovery scheduled")