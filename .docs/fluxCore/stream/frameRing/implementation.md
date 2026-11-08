# FrameRing Implementation

## Architecture

```text
LocalDeviceStream._onFrame(packet)
  await FrameRing.publish(packet, codec)
    bounded asyncio.Queue(maxsize=64)
      one _decodeLoop task
        await to_thread(packet.decode, codec)
        _publishFrame(decodedTensor)
          fixed-capacity RingSlot collection
          evict oldest 20% under pressure
          completeWrite -> FILLED

Presenter._present()
  slot = ring.latest()  # acquire reader lease
  view.present(slot.payload)
  ring.release(slot)  # release lease in finally
```

## Ownership and presentation

- `latest()` returns the newest filled `iRingSlot` and increments its reader count.
- The caller must call `release(slot)` exactly once, preferably in `finally`.
- A slot with active readers cannot be reused, freed, or cleared.
- `next()` remains an alias for `latest()` and returns a leased slot, not a cloned tensor.
- `Canvas.present()` and `GLCanvas.present()` synchronously convert the tensor into an owned `QImage` copy. They do not retain the input tensor after returning, so Presenter can release the lease when `present()` returns.
- Any future view that retains the tensor asynchronously must provide its own ownership mechanism.

## Fixed-capacity eviction guard

- Capacity is fixed at the validated constructor size; automatic growth is disabled.
- At or above 80% filled-slot occupancy, the ring invalidates the oldest 20% of filled slots, rounded up.
- If no writable slot exists, it performs the same eviction pass as a fallback.
- The newest filled slot and all slots with active readers are protected.
- If no slot can be made writable, the newly decoded display frame is dropped and counted. The ring never grows.
- Eviction happens after decoding. Encoded packets remain in the bounded FIFO queue and are not arbitrarily discarded.

## Measurements

- `ring.stats`: capacity, filled slots, active leases, current/maximum queue depth, decoded/published/evicted/dropped frame counts, decode errors, and cumulative/maximum decode duration.
- `presenter.stats`: presented/skipped/error counts and cumulative/maximum synchronous `view.present()` duration.
- The current Canvas and GLCanvas `present()` duration includes CUDA-to-CPU transfer and tensor-to-QImage conversion/copy.
- Rising `maxPending` indicates packet arrival is outpacing decoding. High `maxDecodeTimeNs` indicates decode/conversion latency. High `maxPresentTimeNs` indicates view conversion/presentation cost.
- Rising `droppedFrames` indicates no slot could safely be reused because candidate slots were leased or unavailable.

## Usage

```python
await ring.publish(packet, decoder)

slot = ring.latest()
if slot is not None:
    try:
        tensor = slot.payload
        if tensor is not None:
            view.present(tensor)
    finally:
        ring.release(slot)

print(ring.stats)
print(presenter.stats)
```
