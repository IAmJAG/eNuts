# Requirements — OPEmitter

## Functional

- Run heavy emitter work in a child process.
- Bidirectional message passing via `multiprocessing.Queue`.
- Cooperative shutdown that drains queues before exit.
- Parent and child both able to observe shutdown.

## Non-functional

- Must not block the parent event loop.
- Must not leave multiprocessing feeder threads alive after stop.
- Must tolerate forced termination.
- Must be usable as a base class for concrete emitters.

## Constraints

- Inherits the existing `AsyncProcess` contract.
- Must remain compatible with the `iSCRCPYEmitter` protocol.
