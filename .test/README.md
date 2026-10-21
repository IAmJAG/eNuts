# Test pipeline (`.test/`)

All automated checks live here — **not** under `src/` and **not** under `.scripts/`.

Production types (`Policy`, `Vocabulary`, `PolicyOptions`) do not own seed data or fixtures. Tests supply them.

## Layout

```text
.test/
  README.md
  conftest.py
  fixtures/
    policy/
      seeds.py
      builders.py
  smoke/
    policy/
      test_policy_forward_predict.py
      test_policy_options_roundtrip.py
  unit/            (reserved)
  integration/     (reserved)
```

## Categories

| Folder | Purpose |
|--------|---------|
| `smoke/` | Construct, shapes, serialize round-trip, predict contract |
| `unit/` | Isolated class behavior (future) |
| `integration/` | Policy + stream/emitter (future) |

## How to run

```bash
PYTHONPATH=src python -m pytest .test/smoke -q
PYTHONPATH=src python -m pytest .test/smoke/policy -q
PYTHONPATH=src python -m pytest .test -q
```

## Responsibility split

| Concern | Owner |
|---------|--------|
| Labels, vocabularies, options, model | `src/fluxCore/policy/` |
| Seed maps, builders, fake tensors | `.test/fixtures/` |
| Smoke / unit / integration cases | `.test/<category>/` |
