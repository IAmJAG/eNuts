# Dashboard

Cell grid for mixed-size cards. The host fills the page content area. Cards sit on a fixed **64×64 px** unit. Column count follows the host width. Rows grow with the cards.

Reference commit on `base`: `1cafaac0` (behavior below matches that tree).

## What you interact with

| Action | Result |
|--------|--------|
| Drag the card body | Card floats under the cursor. Other cards push out of the way. Drop snaps to a cell. |
| Drop onto a card of the **same** `colSpan` × `rowSpan` | The two cards exchange places. |
| Drag an edge or corner (8 px hit zone) | Resize. Growing may shrink or relocate neighbors down to their minimum span. Shrinking affects only the card being resized. |
| Resize the window | Column count is recomputed. Cards that no longer fit are clamped into the new width. |

Cells are not stretched to eat leftover pixels. Anything short of one full cell stays empty on the right.

## Layout

```
columns = max(minColumns, (width - 2*margins + gap) // (cellSize + gap))
card pixels = span * cellSize + (span - 1) * gap
```

Defaults (`dashboardConfig`):

| Field | Default | Meaning |
|-------|---------|---------|
| `cellSize` | `64` | One cell, width and height, in pixels. `cellMinHeight` is an alias. |
| `gap` | `8` | Pixels between cells. |
| `margins` | `8` | Pixels inside the host. |
| `columns` | `12` | Seed only, until the first layout pass. |
| `minColumns` | `1` | Floor when the host is very narrow. |

Rows are unbounded. `RowCount()` is the lowest row index not used by any card, at least 1.

## Pieces

Contracts live in `jAGQt.types.interface.widgets.dashboard`. Implementations live in `jAGQt.widgets.dashboard`. Type against the contract. Construct the class.

| Contract | Class | Role |
|----------|-------|------|
| `iCard` | `Card` | Styleable shell. Subclass this for real cards. |
| `iCardPlacement` | `CardPlacement` | Cell rect: `Col`, `Row`, `ColSpan`, `RowSpan`. No pixels. |
| `iOccupancyMap` | `OccupancyMap` | Which cells are taken. |
| `iGridModel` | `GridModel` | Placements and metrics. No input. |
| `iLayoutResolver` | `LayoutResolver` | Move, grow, shrink. |
| `iDashboardGrid` | `DashboardGrid` | Host. Owns model, resolver, drag, resize. |
| `iDragController` | `DragController` | Pointer move. Wired by the host. |
| `iResizeController` | `ResizeController` | Edge resize. Wired by the host. |
| — | `dashboardConfig` | Metrics bag. Not a contract. |

`Card` is a `QFrame`. It has a title and a body. It does not know the grid. Put domain UI in the body.

QSS hooks on the card: object name `Card`, properties `variant`, `dragging` (`"true"` / `"false"`), `resizing` (`"true"` / `"false"`). Host object name is `DashboardGrid`.

`DashboardGrid._C_DEBUG_EDGE` is still `True`. That paints a temporary cyan border so the host bounds are visible. Turn it off when the edge check is done.

## Rules the resolver enforces

**Move** (`ResolveMove` / `TryMove`)

- Target must stay inside the current column count and at row ≥ 0.
- One overlapping card with the same span swaps with the mover’s origin.
- Other overlaps are relocated to the nearest free rect of the same size. Prefer the mover’s old cell.
- If a blocker cannot be placed, the move is rejected and nothing changes.

**Grow** (`ResolveGrow` / `TryResize` when either span increases)

- Anchor stays the top-left cell.
- Free space is taken as-is.
- Blockers are relocated if a free slot exists; otherwise they are shrunk toward `MinColSpan` / `MinRowSpan`.
- If space still cannot be freed, the grow is rejected.

**Shrink** (`ResolveShrink` / `TryResize` when both spans stay the same or decrease)

- Only that card changes. Neighbors do not grow into the freed cells.

## Shell

`Shell._wInitializeShell` builds a `Page` (`page.dashboard`) and adds one `DashboardGrid` with stretch so it fills `W_PAGE_CONTENT`. `_seedDashboard` places Status, Live, Stats, Quick Actions, and Activity. The Recorder page is the default page; open Dashboard from the side bar.

## Usage

### Host on a page

```python
from PySide6.QtWidgets import QLabel

from jAGQt.widgets.dashboard import Card, DashboardGrid, dashboardConfig
from jAGQt.widgets.page import Page


page = Page("Dashboard", "Overview", id="page.dashboard")
grid = DashboardGrid(
    config=dashboardConfig(
        cellSize=64,
        gap=8,
        margins=8,
        minColumns=1,
    )
)

status = Card(
    title="Status",
    minColSpan=2,
    minRowSpan=2,
    preferredColSpan=4,
    preferredRowSpan=2,
    variant="status",
)
status.SetBodyWidget(QLabel("System overview"))

grid.AddCard(status, col=0, row=0, colSpan=4, rowSpan=2)
page.addWidget(grid)  # stretch=1, fills the content area
```

`AddCard` returns the `CardPlacement`, or `None` if the rect does not fit. Omit `col` / `row` to take the nearest free slot from `FindAutoSlot`. Omit spans to use the card’s preferred spans, never below the minimum.

### Subclass a card

```python
from PySide6.QtWidgets import QLabel

from jAGQt.widgets.dashboard import Card


class StatusCard(Card):
    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Status",
            minColSpan=2,
            minRowSpan=2,
            preferredColSpan=4,
            preferredRowSpan=2,
            variant="status",
            parent=parent,
        )
        self.SetBodyWidget(QLabel("System overview"))
```

The grid only needs `iCard`. Keep device or stream logic out of `DashboardGrid`.

### Move, resize, remove

```python
grid.TryMove(status, col=2, row=1)
grid.TryResize(status, colSpan=6, rowSpan=2)
grid.RemoveCard(status)
grid.Clear()
```

`TryMove` / `TryResize` return `False` when the resolver rejects the change. On success the model is updated and `ApplyLayout` runs.

During a pointer drag the host calls `TryMove(..., floatCard=True)` so the dragged card is not snapped back under the cursor. That flag is on the class, not on `iDashboardGrid`.

### Read the layout

```python
model = grid.Model
for placement in model.Placements:
    col, row, colSpan, rowSpan = placement.Rect()
    # placement.Card is the iCard

snapshot = model.ExportLayout()
# [{"id", "col", "row", "colSpan", "rowSpan"}, ...]
```

`ColumnsForWidth(width)` and `SyncColumns()` recompute the live column count. `ApplyLayout` already calls `SyncColumns` when the host width is known.

## Not in this pass

- Persisting `ExportLayout` (no QSettings key yet).
- Ghost cell outline while dragging.
- Animated push.
- A streamer card. `imageStreamer` is still the Recorder viewer, not a `Card`.
