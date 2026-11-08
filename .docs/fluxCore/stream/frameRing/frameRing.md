# FrameRing

`FrameRing` serializes packet decoding through one bounded asynchronous queue and stores decoded tensors in reusable `RingSlot` objects. It provides latest-frame access for display without cloning tensor storage.

## API

- `start() -> None`: start the decode worker.
- `publish(packet, decoder) -> Awaitable[None]`: enqueue a packet; awaits capacity when the queue is full.
- `latest() -> Optional[iRingSlot]`: acquire and return the newest filled slot.
- `next() -> Optional[iRingSlot]`: compatibility alias for `latest()`.
- `release(slot) -> None`: release a lease acquired through `latest()` or `next()`.
- `stop() -> Awaitable[None]`: stop accepting new work at the stream lifecycle level, drain queued packets, and await worker completion.
- `size`: current number of slots.
- `pending`: number of queued packets.

## Consumer contract

Always release a returned slot, even if presentation fails:

```python
slot = ring.latest()
if slot is not None:
    try:
        frame = slot.payload
        if frame is not None:
            view.present(frame)
    finally:
        ring.release(slot)
```

The payload is the original decoded tensor. Do not keep using it after releasing the slot unless the consumer has made its own copy.

## Lifecycle

`LocalDeviceStream.start()` starts the ring worker before subscribing to frame packets. `LocalDeviceStream.stop()` unsubscribes from the emitter and then drains/stops the worker. The raw encoded recorder path is separate from this ring.
