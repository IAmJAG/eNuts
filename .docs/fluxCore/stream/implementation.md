# Implementation Details

## 1. Architecture Overview

```text
Emitter.ON_FRAME(packet)
  → LocalDeviceStream._onFrame
       ring.publish(packet, codec)   # decode via createTask + to_thread inside ring
       raiseEvent(ON_FRAME, packet)  # optional stream subscribers

FrameRing.latest() / next()
  → Presenter (default iFrameConsumer) / other consumers
       Presenter.work → view.present(tensor)
```

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/stream/__deviceStream.py` | `.docs/fluxCore/stream/deviceStream.md` | Stream + consumer registry |
| `src/fluxCore/stream/__presenter.py` | `.docs/fluxCore/stream/presenter/` | Display consumer |
| `src/fluxCore/stream/frameRing/__frameRing.py` | `.docs/fluxCore/stream/frameRing/` | Publish / latest / next |

## 3. Core Workflows & Data Flow
1. `switchDevice` attaches emitter and `start`s stream + consumers.
2. Each `ON_FRAME` publishes the packet; ring owns decode.
3. Presenter throttles `latest()` → `GLCanvas.present` (Tensor→QImage transitional).
