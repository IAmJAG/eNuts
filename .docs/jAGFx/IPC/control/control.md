## Overview & Design Context

Control plane for peer readiness using existing `bridgeId` / `ownerId` only.
No ClientSession or secondary registry.

* **Design Decision:** Alive state is `Endpoint._bridgeAlive[peerBridgeId] → expiry`.

---

## Classes

### `HelloMessage` / `HelloAckMessage` / `HeartbeatMessage`
- Client originates Hello and Heartbeat with `ownerId = client.bridgeId`.
- Main ControlBridge marks alive and replies HelloAck.

### `ControlBridge`
- **Purpose:** Wire control messages to `Endpoint.markBridgeAlive`.
- **Methods:** handlers `_onHello`, `_onHelloAck`, `_onHeartbeat`.
- **Client:** wait on `helloAcked` after sending Hello.

## Sample Usage

```python
# Main
ep.registerBridge(ControlBridge(), asDefault=True)

# Client
ctrl = ControlBridge()
ep.registerBridge(ctrl, asDefault=True)
await ep.start()
await ctrl.send(HelloMessage())
await asyncio.wait_for(ctrl.helloAcked.wait(), timeout=5.0)
# then periodic HeartbeatMessage
```
