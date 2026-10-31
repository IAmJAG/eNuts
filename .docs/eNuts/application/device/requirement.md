# Requirements & Design Specifications

## 1. Project Overview
Central device registry for ENUTS: discover SCRCPY-capable devices and expose emitters to Shell/KGRecorder.

## 2. Functional Requirements
- **FR-1:** Poll ADB devices and raise initialized/added/removed events.
- **FR-2:** Support ensureRunning (initialize + start) for a selected serial.
- **FR-3:** Stop all emitters on shutdown; stop all but one when recording starts.

## 3. Non-Functional Requirements
- **NFR-1:** Discovery loop respects shutdown event and stops emitters on exit.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Ownership on Shell
- **Affected Modules:** `deviceManager`, `Shell`
- **Divergence:** Registry is application-scoped, not page-scoped.
- **Design Decision & Justification:** Device presence must update regardless of active page.
