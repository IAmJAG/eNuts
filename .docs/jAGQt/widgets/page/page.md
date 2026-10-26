## Overview & Design Context
`Page` is the primary content host for application views. It owns a `Header`, a content slot, and an optional `CommandBar`.

* **Design Decision / Deviation Notes:** Icon data is optional at construction and is always settable afterward via the `Icon` property (forwards to `Header`). Header icon layout details (position, size, colors) are properties on `Header`, not constructor arguments.

---

## Classes

### `Page`
- **Purpose:** Full-page container with title/description/icon header, expandable content area, and optional command bar.
- **Methods:**
  - `addComponent(component, stretch=1)` -> Add a component into the content slot.
  - `addWidget(widget, stretch=1)` -> Add a widget into the content slot.
  - `addSpacer(...)` -> Insert a spacer into the content layout.
  - `addCommand(button, group=None)` -> Add a button to the command bar (no-op if command bar off).
  - `addCommandStretch(stretch=1)` / `addCommandGroup(name)` -> Command-bar helpers.

---

## Properties

| Property | Type | Notes |
| :--- | :--- | :--- |
| `Id` | `str \| UUID` | Page identity |
| `Title` | `str` | Forwards to header |
| `Description` | `str` | Forwards to header |
| `Icon` | `QIcon \| QPixmap \| str \| None` | Forwards to header; accepts path string |
| `IconPosition` | `HeaderIconPosition` | Forwards to header |
| `CommandBarState` | `bool` | Enable / disable command bar |

## Sample Usage

```python
from jAGQt.widgets.page import Page
from utilities.io import getICONPath

page = Page(
    title="Key & Gesture Recorder",
    description="Capture keys and gestures",
    icon=getICONPath("KGRecorder.png"),
    commandBarOn=True,
    id="kg-recorder",
)
page.IconPosition = HeaderIconPosition.TitleRow
```
