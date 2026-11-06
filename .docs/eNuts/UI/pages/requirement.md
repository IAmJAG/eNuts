# Requirements & Design Specifications

## 1. Project Overview
Key & Gesture Recorder page for capturing continuous device stream video and aligned keyboard/mouse events for Policy training datasets.

## 2. Functional Requirements
- **FR-1:** Page hosts UI (device combo, CaptureGLImage, command bar) and the recording controller.
- **FR-2:** Left/main area hosts CaptureGLImage (display + event emission).
- **FR-3:** Side strip hosts device selector (and later status / event list).
- **FR-4:** CommandBar groups: Recording (Start, Stop), Session (Clear), Persistence (Save, Open). Clear sits on the right before Save/Open with spacing.
- **FR-5:** Recording produces continuous video only (no pause/resume) so Policy series have no artificial edges.
- **FR-6:** Each saved session yields two paired artefacts: MP4 of the stream and a corresponding event file. Event format must complement Policy action parameters (schema deferred).
- **FR-7:** Recording logic lives **inside** the Page (`KGRecorder` page class / helpers it owns).
- **FR-8:** CaptureGLImage has no recording state; it only emits keyboard and mouse events.
- **FR-9:** Device selector reflects `deviceManager` list changes (already wired).

## 3. Non-Functional Requirements
- **NFR-1:** Follow CodingStyle, NamingConventions, and Documentation path-mirroring rules.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Continuous recording only
- **Affected Modules:** `KGRecorder` page, CommandBar
- **Description of Standard / Best Practice:** Many recorders offer pause/resume.
- **Divergence:** Pause/Resume removed.
- **Design Decision & Justification:** Policy datasets require continuous video; pause edges confuse training series.
- **Code Doc Cross-Reference:** requirement FR-5; CommandBar has Start/Stop only in Recording group.

### Issue / Item 2: Controller inside Page
- **Affected Modules:** `src/eNuts/UI/pages/__kgRecorder.py`, Shell
- **Description of Standard / Best Practice:** Some designs keep long-lived controllers on the shell/window.
- **Divergence:** Controller lives inside the Page; application-level `KGRecorder` and Shell binding removed.
- **Design Decision & Justification:** Page already owns stream + device combo and works without Shell wiring. Recording session is page-scoped.
- **Code Doc Cross-Reference:** `kgRecorderPage.md`, `shell.md`.
