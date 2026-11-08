# Presenter Implementation

## Workflow

```text
_present()
  validate ring and view
  slot = ring.latest()  # leased RingSlot
  skip if slot.sequence == _lastSequence
  view.present(slot.payload)
  remember slot.sequence on success
  ring.release(slot) in finally
```

Presenter compares the stable frame sequence rather than the tensor's `data_ptr()`. It holds the slot lease only while synchronously invoking the view, and it does not clone the tensor.
