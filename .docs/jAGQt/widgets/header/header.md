## Overview & Design Context
`Header` renders title, optional description, and optional icon for a Page (or any host).

* **Design Decision / Deviation Notes:** Constructor accepts only title, description, and optional icon. Icon position, size, background, and foreground are settable properties so call sites stay small.

---

## Classes

### `Header`
- **Purpose:** Styled title row / column with optional icon.
- **Methods:**
  - Internal `_rebuildLayout()` rearranges title, description, and icon according to `IconPosition`.

---

## Properties

| Property | Type | Default | Notes |
| :--- | :--- | :--- | :--- |
| `Title` / `title` | `str` | `""` | |
| `Description` / `description` | `str` | `""` | |
| `Icon` / `icon` | `QIcon \| QPixmap \| str \| None` | `None` | Accepts path string |
| `IconPosition` / `iconPosition` | `IconPosition` | `TitleRow` | Top / Bottom / Left / Right / TitleRow |
| `IconSize` / `iconSize` | `int` | `24` | Base size; layout may grow to match text |
| `IconBackground` | `QColor` | transparent | |
| `IconForeground` | `QColor` | darkGray | Used for tinting |

## Sample Usage

```python
from jAGQt.widgets.header import Header, HeaderIconPosition

h = Header(title="Dashboard", description="Overview", icon="assets/icons/dashboard.png")
h.IconPosition = HeaderIconPosition.Left
h.IconSize = 32
```
