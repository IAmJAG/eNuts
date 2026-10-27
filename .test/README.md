# Test pipeline (`.test/`)

All automated checks live here — **not** under `src/` and **not** under `.scripts/`.

Production types do not own seed data or fixtures. Tests supply them.

## Layout

```text
.test/
  README.md
  conftest.py
  fixtures/
    policy/
      seeds.py
      builders.py
    ipc/
      payloads.py
  smoke/
    policy/
      test_policy_forward_predict.py
      test_policy_options_roundtrip.py
      test_policy_persist.py
    ipc/
      test_message_roundtrip.py
      test_endpoint_bridge.py
  unit/            (reserved)
  integration/     (reserved)
```

## Categories

| Folder | Purpose |
|--------|---------|
| `smoke/` | Construct, shapes, serialize round-trip, predict / IPC contract |
| `unit/` | Isolated class behavior (future) |
| `integration/` | Policy + stream/emitter (future) |

## How to run

```bash
PYTHONPATH=src python -m pytest .test/smoke -q
PYTHONPATH=src python -m pytest .test/smoke/policy -q
PYTHONPATH=src python -m pytest .test/smoke/ipc -q
PYTHONPATH=src python -m pytest .test -q
```

## Responsibility split

| Concern | Owner |
|---------|--------|
| Labels, vocabularies, options, model | `src/fluxCore/policy/` |
| IPC transport, endpoint, bridge | `src/jAGFx/IPC/` |
| Seed maps, builders, smoke payloads | `.test/fixtures/` |
| Smoke / unit / integration cases | `.test/<category>/` |
