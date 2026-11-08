# Implementation Details

## 1. Architecture Overview

```text
Presenter(AsyncService)
  attachRing(iFrameRing) / detachRing()
  attachView(iFrameView) / detachView()   # Presenter-owned
  throttle = 1 / displayFps

  _serviceLoop:
    await pause gate
    await _present()
      if no ring or view: return
      if view C++ deleted: drop view
      frame = ring.latest()
      if frame is None: return
      if data_ptr == _lastDataPtr: return
      view.present(frame)
      remember data_ptr on success
    await throttle wait
```

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/stream/__presenter.py` | `.docs/fluxCore/stream/presenter/presenter.md` | Presenter consumer |
| `src/fluxCore/types/interface/stream/__frameConsumer.py` | (interface) | `iFrameConsumer` |
| `src/fluxCore/types/interface/stream/__frameView.py` | (interface) | `iFrameView` |

## 3. Core Workflows & Data Flow
Stream registers the Presenter and calls `attachRing`. Page/widget calls `attachView`. Stream `start`/`stop` drive `Presenter.start`/`stop`. Presenter never touches the emitter or codec.
