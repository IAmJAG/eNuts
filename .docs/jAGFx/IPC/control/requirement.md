# Requirements & Design Specifications

## 1. Overview

Handshake + heartbeat keep peer bridgeIds alive on the main Endpoint.

## 2. Functional Requirements

- **FR-1:** Client originates Hello and Heartbeat.
- **FR-2:** Hello accepted → `markBridgeAlive(ownerId, initialTtl)` + HelloAck.
- **FR-3:** Heartbeat → refresh `markBridgeAlive(ownerId, heartbeatTtl)`.
- **FR-4:** `isBridgeAlive` false after expiry; `sweepDeadBridges` reports transitions.
- **FR-5:** No identifiers other than `bridgeId` / `ownerId`.

## 3. Design Decisions

### No session registry
Endpoint bridge registry + `_bridgeAlive` are sufficient.
