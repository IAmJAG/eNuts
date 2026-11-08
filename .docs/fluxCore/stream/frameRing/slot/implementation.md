# Implementation Details

## 1. Architecture Overview
`RingSlot` is a plain data cell. `FrameRing` owns transitions.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/stream/frameRing/slot/__ringSlot.py` | `.docs/fluxCore/stream/frameRing/slot/ringSlot.md` | Cell |
| `src/fluxCore/stream/frameRing/slot/__slotFlag.py` | `.docs/fluxCore/stream/frameRing/slot/slotFlag.md` | Flags |

## 3. Core Workflows & Data Flow
`beginWrite` → `completeWrite` | `markFree` (abandon) → optional `release`/`markFree` after sequential read.
