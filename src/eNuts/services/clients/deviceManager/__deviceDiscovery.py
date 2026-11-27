# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import sleep as asyncSleep
from collections.abc import Awaitable, Callable
from multiprocessing import Queue
from multiprocessing.synchronize import Event as syncEvent

# ==================================================================================
from adbutils import AdbDevice

# ==================================================================================
from fluxCore.device import SCRCPYDevice
from fluxCore.types.interface.device import iDevice
from jAGFx.IPC.client import beat, ownDispatch
from jAGFx.IPC.message import Handshake
from jAGFx.types.interface.communication import iMessage
from utilities.asyncADB import ADBDevices

# ==================================================================================
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
async def _discovery(shutdownEvent: syncEvent, queue: Queue) -> None:
    def isShuttingDown() -> bool: ...

    isShuttingDown = shutdownEvent.is_set

    async def _getDevices() -> dict[str, iDevice]:
        found: dict[str, AdbDevice] = await ADBDevices()
        devices: dict[str, iDevice] = {}
        for serial in found:
            devices[serial] = SCRCPYDevice(ident=serial)

        return devices

    try:
        msgStarted: DeviceDiscoveryStarted = DeviceDiscoveryStarted()
        verbose("Device discovery started; requesting initial ADB device list")
        await ownDispatch(queue, msgStarted)

        connectedDevices: dict[str, iDevice] = await _getDevices()
        verbose(
            f"initial discovery count={len(connectedDevices)} ids={list(connectedDevices.keys())}"
        )

        msgIDL: DeviceListInitialized = DeviceListInitialized(devices=connectedDevices)
        await ownDispatch(queue, msgIDL)

        devices: dict[str, iDevice] = connectedDevices

        while not isShuttingDown():
            connectedDevices: dict[str, iDevice] = await _getDevices()
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
                    verbose(f"New device found id={deviceId}")
                    await ownDispatch(queue, deviceAdded)

            for deviceId in removedIds:
                device: iDevice = devices.pop(deviceId, None)
                if device is not None:
                    deviceRemoved: DeviceRemoved = DeviceRemoved(device=device)
                    verbose(f"Device removed id={deviceId}")
                    await ownDispatch(queue, deviceRemoved)

            if not isShuttingDown():
                await asyncSleep(POLL_INTERVAL)

    finally:
        msgEnded: DeviceDiscoveryEnded = DeviceDiscoveryEnded()
        verbose("Device discovery ended; dispatching DeviceDiscoveryEnded")
        await ownDispatch(queue, msgEnded)

# ==================================================================================
async def messageHandler(msg: iMessage, shutdownEvent: syncEvent, outQueue: Queue):
    if isinstance(msg, Handshake):
        verbose(f"Acknowleged [{msg.ownerId}]")
        createTask(_discovery, shutdownEvent, outQueue)
        createTask(beat, shutdownEvent, outQueue)

