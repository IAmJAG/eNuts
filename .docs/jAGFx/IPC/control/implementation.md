# Implementation Details

## Module map

| Source | Role |
|--------|------|
| `control/__messages.py` | Hello, HelloAck, Heartbeat |
| `control/__bridge.py` | ControlBridge handlers |

## Flow

Hello → markBridgeAlive → HelloAck  
Heartbeat → markBridgeAlive  
Main domain send: gate on `isBridgeAlive(peerBridgeId)`
