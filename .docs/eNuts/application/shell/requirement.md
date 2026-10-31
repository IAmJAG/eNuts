# Requirements & Design Specifications

## 1. Project Overview
Shell hosts the live device registry and the K&G Recorder controller so UI pages remain presentation-only.

## 2. Functional Requirements
- **FR-1:** Shell creates a single `deviceManager` bound to the window shutdown event and starts discovery.
- **FR-2:** Shell creates a single application `KGRecorder` and calls `setDeviceManager` before page bind.
- **FR-3:** After WorkSpace builds navigation pages, Shell binds the KG recorder page to the controller.
- **FR-4:** On close, Shell stops all device emitters then signals shutdown.

## 3. Non-Functional Requirements
- **NFR-1:** Managers are created at most once per Shell lifetime.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Controllers outside Pages
- **Affected Modules:** `src/eNuts/application/__shell.py`, `src/eNuts/application/recorder/__kgRecorder.py`
- **Description of Standard / Best Practice:** UI frameworks often place controllers inside views.
- **Divergence:** Application `KGRecorder` and `deviceManager` live on Shell.
- **Design Decision & Justification:** Pages are swapped by WorkSpace; device discovery and recording sessions must outlive individual page instances.
- **Code Doc Cross-Reference:** `shell.md`, `kgRecorder.md`.
