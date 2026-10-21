# Test pipeline (`.test/`)

All automated checks live here — **not** under `src/` and **not** under `.scripts/`.

Production types (`Policy`, `Vocabulary`, `PolicyOptions`) do not own seed data or fixtures. Tests supply them.

## Layout

```text
.test/
  README.md                 ← this file
  conftest.py               ← shared path/bootstrap (optional)
  fixtures/                 ← reusable test-only data
    policy/
      seeds.py              ← action / argument-kind seed maps for tests
  smoke/                    ← fast shape/wiring checks (no training)
    policy/
      test_policy_forward_predict.py
  unit/                     ← pure unit tests (future)
  integration/              ← multi-module / emitter (future)
```

## Categories

| Folder | Purpose | Speed | Network |
|--------|---------|-------|---------|
| `smoke/` | Construct + forward + predict; shapes and contracts | Fast | May download torchvision weights once |
| `unit/` | Isolated class behavior (Vocabulary encode/decode, etc.) | Fast | No |
| `integration/` | Policy + stream/emitter/wrapper | Slower | Maybe |

## How to run

From repo root (package root must resolve `fluxCore`):

```bash
# all smoke
python -m pytest .test/smoke -q

# one module
python -m pytest .test/smoke/policy -q

# everything under .test
python -m pytest .test -q
```

`PYTHONPATH` should include `src` if the project is not installed editable:

```bash
PYTHONPATH=src python -m pytest .test/smoke -q
```

## Responsibility split

| Concern | Owner |
|---------|--------|
| Labels, vocabularies, options, model | `src/fluxCore/policy/` |
| Seed maps, fake tensors, assert helpers | `.test/fixtures/` |
| Smoke / unit / integration cases | `.test/<category>/` |
