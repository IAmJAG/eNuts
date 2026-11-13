# OPEmitter message-path patch

Target branch: `development`

Replace `.test/fixtures/emitters/echoWorker.py` with the file at the same path in this patch.

The change moves the child-to-parent `multiprocessing.Queue.put` off the child's asyncio event loop, matching the contract's rule that blocking queue operations run outside the event loop. It preserves the shared client-to-parent queue and the per-client parent-to-client queues.

After applying, run:

```powershell
python .test/smoke/emitters/test_opemitter_message_path.py
```

If the same assertion persists, capture the `FLOW` lines immediately after `start b` and the child process exit codes; that would indicate the second worker is failing before its outbound write, rather than a parent receiver routing issue.
