## Overview & Design Context
Protocol `iKGRecorder` and enum `eKGRecorderState` define the recorder controller surface used by Shell and the page view.

---

## Classes

### `eKGRecorderState`
- **Purpose:** Idle | Recording.

### `iKGRecorder`
- **Purpose:** Contract for start/stop/clear/save/open, device binding, and page bind/unbind.

## Sample Usage

```python
from eNuts.types.interface.recorder import iKGRecorder, eKGRecorderState
```
