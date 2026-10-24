# Requirements & Design Specifications

## 1. Project Overview
Key & Gesture Recorder page for capturing continuous device stream video and aligned keyboard/mouse events for Policy training datasets.

## 2. Functional Requirements
- **FR-1:** Page is a pure view composed via factory function (no Page subclass for content).
- **FR-2:** Left pane hosts CaptureImage (display + event emission only).
- **FR-3:** Right pane hosts expandable configuration strip (device selector first), status, and event list.
- **FR-4:** CommandBar groups: Recording (Start, Stop), Session (Clear), Persistence (Save, Open). Clear sits on the right before Save/Open with spacing.
- **FR-5:** Recording produces continuous video only (no pause/resume) so Policy series have no artificial edges.
- **FR-6:** Each saved session yields two paired artefacts: MP4 of the stream and a corresponding event file. Event format must complement Policy action parameters (schema deferred).
- **FR-7:** Recording logic lives in dedicated `KGRecorder` controller (component of ENUTSWindow, wired from Shell).
- **FR-8:** CaptureImage has no recording state; it only emits keyboard and mouse events.
- **FR-9:** Device selector must eventually reflect WorkSpace / deviceManager list changes. Live subscription is deferred; control must remain rebindable without layout changes.

## 3. Non-Functional Requirements
- **NFR-1:** Follow CodingStyle, NamingConventions, and Documentation path-mirroring rules.
- **NFR-2:** Contracts (`iKGRecorder`) for the controller.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Continuous recording only
- **Affected Modules:** `KGRecorder`, page CommandBar
- **Description of Standard / Best Practice:** Many recorders offer pause/resume.
- **Divergence:** Pause/Resume removed.
- **Design Decision & Justification:** Policy datasets require continuous video; pause edges confuse training series.
- **Code Doc Cross-Reference:** requirement FR-5; CommandBar has Start/Stop only in Recording group.

### Issue / Item 2: Logic outside Page
- **Affected Modules:** `KGRecorder`, Shell, Page builder
- **Description of Standard / Best Practice:** Some UIs embed controllers in the page widget.
- **Divergence:** Controller is ENUTSWindow component, wired from Shell.
- **Design Decision & Justification:** Aligns with window-stack roles (ENUTSWindow holds logic; Shell initializes UI; Page is view).

### Issue / Item 3: Device list awareness deferred
- **Affected Modules:** device combo on kg-recorder page
- **Divergence:** Live subscription not implemented in this build.
- **Design Decision & Justification:** Layout and control are prepared; subscription is a later wiring task without layout redesign.
