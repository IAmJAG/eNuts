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
        verbose(f"Acknowleged [{msg.ownerId}]")
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
        verbose(f"Sending Heartbeat beat={BEAT}")
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
        verbose("Device discovery started; requesting initial ADB device list")
        await ownDispatch(queue, msgStarted)

        connectedDevices: Dict[str, iDevice] = await _getDevices()
        verbose(f"initial discovery count={len(connectedDevices)} ids={list(connectedDevices.keys())}")

        msgIDL: DeviceListInitialized = DeviceListInitialized(devices=connectedDevices)
        verbose(
            "Dispatching DeviceListInitialized "
            f"count={len(connectedDevices)} ids={sorted(connectedDevices.keys())}"
        )
        await ownDispatch(queue, msgIDL)

        devices: Dict[str, iDevice] = connectedDevices

        while not isShuttingDown():
            connectedDevices: Dict[str, iDevice] = await _getDevices()
            curIds = set(connectedDevices.keys())
            oldIds = set(devices.keys())
            addedIds = curIds - oldIds
            removedIds = oldIds - curIds

            verbose(
                "Device poll: "
                f"current={sorted(curIds)} previous={sorted(oldIds)} "
                f"added={sorted(addedIds)} removed={sorted(removedIds)}"
            )

            for deviceId in addedIds:
                device: iDevice = connectedDevices.get(deviceId, None)
                if device is not None:
                    devices[deviceId] = device
                    deviceAdded: DeviceAdded = DeviceAdded(device=device)
                    verbose(f"Dispatching DeviceAdded id={deviceId}")
                    await ownDispatch(queue, deviceAdded)
                    verbose(f"Dispatched DeviceAdded id={deviceId}")

            for deviceId in removedIds:
                device: iDevice = devices.pop(deviceId, None)
                if device is not None:
                    deviceRemoved: DeviceRemoved = DeviceRemoved(device=device)
                    verbose(f"Dispatching DeviceRemoved id={deviceId}")
                    await ownDispatch(queue, deviceRemoved)
                    verbose(f"Dispatched DeviceRemoved id={deviceId}")

            if not isShuttingDown():
                await asyncSleep(POLL_INTERVAL)

    except BaseException:
        raise

    finally:
        msgEnded: DeviceDiscoveryEnded = DeviceDiscoveryEnded()
        verbose("Device discovery ended; dispatching DeviceDiscoveryEnded")
        await ownDispatch(queue, msgEnded)
