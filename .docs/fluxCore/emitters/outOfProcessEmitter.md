# outOfProcessEmitter — MOVED

This type has been renamed and relocated.

| Old | New |
|-----|-----|
| `fluxCore.emitters.outOfProcessEmitter` | `jAGFx.IPC.ProcessHost` |
| `src/fluxCore/emitters/__outProcessEmitter.py` | `src/jAGFx/IPC/__processHost.py` |
| `.docs/fluxCore/emitters/outOfProcessEmitter.md` | `.docs/jAGFx/IPC/processHost.md` |
| smoke `TEST.smoke.emitters.outOfProcessEmitter` | `TEST.smoke.ipc.processHost` |

Device / SCRCPY coupling was removed. Supply domain workers via `worker=` (e.g. `SCRCPYWorker`).
