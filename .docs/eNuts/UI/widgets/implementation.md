# Implementation Details

## 1. Architecture Overview
UI widgets under `src/eNuts/UI/widgets/` are page-facing surfaces. Capture hosts forward input via Qt signals; application controllers inject/log.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/UI/widgets/__captureImage.py` | `.docs/eNuts/UI/widgets/captureImage.md` | Software Image + input signals |
| `src/eNuts/UI/widgets/__captureGLImage.py` | `.docs/eNuts/UI/widgets/captureGLImage.md` | GLImage + input signals |

## 3. Core Workflows & Data Flow
1. Page constructs `CaptureGLImage` as `_streamView`.
2. `application.recorder.KGRecorder.bindPage` connects signals to inject/log slots.
3. `LocalDeviceStream` pushes frames via `presentExternal` independently of input.
