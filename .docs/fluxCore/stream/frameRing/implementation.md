# FrameRing Implementation

## Architecture

```text
LocalDeviceStream._onFrame(packet)
  await FrameRing.publish(packet, codec)
    bounded asyncio.Queue(maxsize=64)  # backpressure; no arbitrary packet drops
      one _decodeLoop task
        await to_thread(packet.decode, codec)  # one codec call at a time
        _publishFrame(decodedTensor)
          choose an unleased RingSlot
          completeWrite -> FILLED

Presenter._present()
  slot = ring.latest()  # acquire reader lease
  view.present(slot.payload)  # original tensor; no clone
  ring.release(slot)  # release lease in finally
```

The recorder remains independent: `KGRecorderService` subscribes to the emitter's raw `ON_FRAME` packets and writes encoded payloads directly. It does not consume decoded ring slots.

## Ownership and API

- `latest()` returns the newest filled `iRingSlot` and increments its reader count.
- The caller must call `release(slot)` exactly once, preferably in `finally`.
- A slot with active readers cannot be reused, freed, or cleared.
- `next()` remains as a compatibility alias for `latest()`; it now returns a leased slot, not a cloned tensor.
- Read the tensor through `slot.payload`. `latest()` and `next()` no longer return tensors.
- The view must finish using the tensor before `present()` returns. A view that retains the tensor beyond that point must clone it itself or retain an explicit ownership mechanism.

## Decode ordering and backpressure

- `publish()` is asynchronous and awaits insertion into a bounded queue.
- A single worker decodes packets in submission order using the associated codec context. No per-packet decode tasks are created.
- When the queue is full, the emitter callback waits for capacity. Packets are not dropped, avoiding arbitrary H.264/H.265 inter-frame loss and broken reference chains.
- Queue capacity is `C_DECODE_QUEUE_SIZE` (64).
- Decode exceptions are logged and the worker continues with subsequent packets.
- `start()` starts the worker. `stop()` enqueues a sentinel and awaits the worker, allowing already queued packets to finish before shutdown.

## Ring capacity

The ring prefers EMPTY/FREE slots, then reuses the oldest FILLED slot with no active readers. If every slot is leased, it uses the existing guarded growth policy up to `C_GROW_MAX`. If growth is refused, the just-decoded display frame is skipped and a warning is logged; packet decoding itself remains ordered.

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
```

`LocalDeviceStream` starts and stops the ring worker with its emitter lifecycle. Do not call `publish()` as a synchronous method anymore.
