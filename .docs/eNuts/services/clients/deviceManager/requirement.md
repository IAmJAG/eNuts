# Requirements & Design Specifications

## 1. Project Overview
Out-of-process ADB device discovery client for eNuts. Reports SCRCPYDevice instances to the parent via IPC messages. Replaces the previous in-process DeviceManager.

## 2. Functional Requirements
- **FR-1:** On start, send Handshake then begin discovery and heartbeat.
- **FR-2:** Emit InitializeDeviceList with current ADB devices as SCRCPYDevice.
- **FR-3:** Poll and emit DeviceAdded / DeviceRemoved for changes.
- **FR-4:** Send Heartbeat at fixed margin before reported BEAT window.
- **FR-5:** Always emit DeviceDiscoveryEnded and Terminated on exit.

## 3. Non-Functional Requirements
- **NFR-1:** Respects shared shutdownEvent; no orphaned tasks.
- **NFR-2:** Heartbeat interval tracks BEAT with constant margin (not percentage).
- **NFR-3:** Discovery uses async ADB helpers.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Out-of-process discovery
- **Affected Modules:** deviceManager client, ProcessHost, Shell
- **Divergence:** Discovery no longer runs in the UI process; old in-process DeviceManager is disconnected.
- **Design Decision & Justification:** Keeps UI responsive; matches existing ProcessHost multi-client model.
- **Code Doc Cross-Reference:** deviceManager.md, .docs/jAGFx/IPC/processHost.md.
