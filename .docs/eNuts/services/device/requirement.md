# Requirements & Design Specifications

## 1. Project Overview
**LEGACY.** Former central device registry. Superseded by the out-of-process client under `services/clients/deviceManager`.

## 2. Functional Requirements
- (Historical) Poll ADB, raise events, ensureRunning emitters.
- Current: none — component is disconnected.

## 3. Non-Functional Requirements
- N/A (disconnected).

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Migration to out-of-process client
- **Affected Modules:** old DeviceManager, Shell, KGRecorder
- **Divergence:** In-process service removed from instantiation and exports.
- **Design Decision & Justification:** Align with ProcessHost model; keep UI process light.
- **Code Doc Cross-Reference:** See `.docs/eNuts/services/clients/deviceManager/`.
