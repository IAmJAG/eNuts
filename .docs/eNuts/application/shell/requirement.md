# Requirements & Design Specifications

## 1. Project Overview
Shell hosts the live device registry and shared window services. Recording logic lives inside the K&G Recorder page.

## 2. Functional Requirements
- **FR-1:** Shell creates a single `deviceManager` bound to the window shutdown event and starts discovery.
- **FR-2:** On close, Shell stops all device emitters then signals shutdown.
- **FR-3:** Shell exposes `settings` and `deviceManager` for pages to consume.

## 3. Non-Functional Requirements
- **NFR-1:** `deviceManager` is created at most once per Shell lifetime.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Recorder controller inside Page
- **Affected Modules:** `src/eNuts/application/__shell.py`, `src/eNuts/UI/pages/__kgRecorder.py`
- **Description of Standard / Best Practice:** Some designs keep long-lived controllers on the shell/window.
- **Divergence:** Application-level `KGRecorder` removed; controller lives inside the Page.
- **Design Decision & Justification:** Page already owns stream + device combo and works without Shell wiring. Recording session is page-scoped.
- **Code Doc Cross-Reference:** `shell.md`, `kgRecorderPage.md`.
