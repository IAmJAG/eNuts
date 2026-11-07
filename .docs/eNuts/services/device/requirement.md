# Requirements & Design Specifications

## 1. Project Overview
Central device registry for ENUTS: discover SCRCPY-capable devices and expose emitters to Shell and pages (including KG Recorder).

## 2. Functional Requirements
- **FR-1:** Poll ADB devices and raise initialized/added/removed events.
- **FR-2:** Support `ensureRunning` (initialize + start) for a selected serial.
- **FR-3:** Stop all emitters on shutdown; support stop-all-but-one helpers for recording.

## 3. Non-Functional Requirements
- **NFR-1:** Discovery loop respects shutdown event and stops emitters on exit.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Ownership on Shell, package under services
- **Affected Modules:** `DeviceManager`, `Shell`
- **Divergence:** Registry is application-scoped (Shell), implemented under `services/device` not `application/device`.
- **Design Decision & Justification:** Device presence must update regardless of active page; services layer is the correct home for shared runtime services.
- **Code Doc Cross-Reference:** `deviceManager.md`, `shell.md`.
