# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Task
from asyncio import sleep as asyncSleep
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent
from typing import Dict, Optional, Union

# ==================================================================================
from adbutils import AdbDevice

# ==================================================================================
from fluxCore.device import SCRCPYDevice
from fluxCore.types.interface.device import iDevice
from jAGFx.IPC.message import Handshake, Heartbeat, Terminated
from jAGFx.types.interface.communication import iMessage
from utilities.asyncADB import ADBDevices

# ==================================================================================
from ..__manager import ownDispatch, watcher
from .message import (
    DeviceAdded,
    DeviceDiscoveryEnded,
    DeviceDiscoveryStarted,
    DeviceListInitialized,
    DeviceRemoved,
)

# ==================================================================================
POLL_INTERVAL: float = 0.1
# ==================================================================================

# ==================================================================================
async def deviceWatcher(shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    err: Optional[Union[Exception, BaseException]] = None

    try:
        watcherTask: Task = createTask(watcher, shutdownEvent, _messageHandler, inQueue, outQueue)        

        handShake: Handshake = Handshake()
        await ownDispatch(outQueue, handShake)
        await watcherTask

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
async def _messageHandler(msg: iMessage, shutdownEvent: syncEvent, inQueue: Queue, outQueue: Queue):
    if isinstance(msg, Handshake):
        trace(f"Acknowleged [{msg.ownerId}]", color="cyan")
        createTask(_discovery, shutdownEvent, outQueue)
        createTask(_beat, shutdownEvent, outQueue)

# ==================================================================================
async def _beat(shutdownEvent: syncEvent, queue: Queue):
    def isShuttingDown() -> bool: ...
    isShuttingDown = shutdownEvent.is_set
    BEAT: float = 2.0  # expiry window reported to parent (seconds)
    # Fixed margin so changing BEAT does not significantly alter the interval.
    # Always leave a small constant gap for queue latency.
    MARGIN: float = 0.2
    INTERVAL: float = max(0.05, BEAT - MARGIN)
    while not isShuttingDown():
        heartbeat: Heartbeat = Heartbeat(BEAT)
        trace(f"Sending Heartbeat beat={BEAT}", color="cyan")
        await ownDispatch(queue, heartbeat)
        await asyncSleep(INTERVAL)

# ==================================================================================
async def _discovery(shutdownEvent: syncEvent, queue: Queue) -> None:
    def isShuttingDown() -> bool: ...
    isShuttingDown = shutdownEvent.is_set

    async def _getDevices() -> Dict[str, iDevice]:
        found: Dict[str, AdbDevice] = await ADBDevices()
        devices: Dict[str, iDevice] = {}
        for serial in found.keys():
            devices[serial] = SCRCPYDevice(ident=serial)

        return devices

    try:
        msgStarted: DeviceDiscoveryStarted = DeviceDiscoveryStarted()
        await ownDispatch(queue, msgStarted)

        connectedDevices: Dict[str, iDevice] = await _getDevices()
        verbose(f"initial discovery count={len(connectedDevices)} ids={list(connectedDevices.keys())}")

        msgIDL: DeviceListInitialized = DeviceListInitialized(devices=connectedDevices)
        await ownDispatch(queue, msgIDL)

        devices: Dict[str, iDevice] = connectedDevices

        while not isShuttingDown():
            connectedDevices: Dict[str, iDevice] = await _getDevices()
            curIds = set(connectedDevices.keys())
            oldIds = set(devices.keys())

            for deviceId in curIds - oldIds:
                device: iDevice = connectedDevices.get(deviceId, None)
                if device is not None:
                    devices[deviceId] = device
                    deviceAdded: DeviceAdded = DeviceAdded(device=device)
                    await ownDispatch(queue, deviceAdded)

            for deviceId in oldIds - curIds:
                device: iDevice = devices.pop(deviceId, None)
                if device is not None:
                    deviceAdded: DeviceRemoved = DeviceRemoved(device=device)
                    await ownDispatch(queue, deviceAdded)

            if not isShuttingDown():
                await asyncSleep(POLL_INTERVAL)

    except BaseException:
        raise 

    finally: 
        msgEnded: DeviceDiscoveryEnded = DeviceDiscoveryEnded()
        await ownDispatch(queue, msgEnded)
