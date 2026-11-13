# OPEmitter message-path patch — visible TRACE output

Target branch: `development`

## Files

Replace these repository files with the corresponding files in this patch:

- `.test/fixtures/emitters/echoWorker.py`
- `.test/smoke/emitters/test_opemitter_message_path.py`

## Why this patch changes the test harness

The project's `trace()` helper calls Python's module-level `logging.log()`, which
logs through the root logger. `setupLogging("outOfProcessEmitter")` configures a
named logger; it does not lower the root logger's default threshold. As a result,
level-5 TRACE calls can be silently filtered even though the calls are present.

Both the parent test process and the spawned echo worker now explicitly configure
their root logger at level 5. The patch retains the existing trace calls and adds
worker-start/worker-exit markers. It does not alter the OPEmitter queue topology.

## Run

```powershell
python .test/smoke/emitters/test_opemitter_message_path.py
```

Expected output includes `PASS`, `FLOW`, and child-worker messages for both `a`
and `b`, including each worker's inbound receipt and outbound reply. If `b` still
fails, the trace should now show whether worker `b` started, received `only-b`,
and wrote its reply, or exited before reaching those steps.
