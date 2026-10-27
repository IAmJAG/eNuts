# ==================================================================================
"""Smoke: Message fields serialize; IOQueue transports a Message in-process."""
# ==================================================================================
from __future__ import annotations

# ==================================================================================
import json
from pathlib import Path
import sys
from uuid import UUID

# ==================================================================================
from jAGFx.IPC import IOQueue, Message
from jAGFx.serializer import jsonDecode

# ==================================================================================
_TEST_ROOT = Path(__file__).resolve().parents[2]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))

from fixtures.ipc.payloads import SmokePayload  # noqa: E402


# ==================================================================================
def test_message_roundtrip() -> None:
    original = Message(
        payload=SmokePayload(text="hello", kind="ping"),
        isTerminal=False,
    )
    correlationId = original.correlationId
    messageId = original.messageId
    timestamp = original.timestamp

    payload = json.loads(json.dumps(original.encode()))
    restored = jsonDecode(payload)

    assert isinstance(restored, Message)
    assert isinstance(restored.payload, SmokePayload)
    assert restored.payload.text == "hello"
    assert restored.payload.kind == "ping"
    assert restored.correlationId == correlationId
    assert restored.messageId == messageId
    assert abs(restored.timestamp - timestamp) < 1e-9
    assert restored.isTerminal is False


def test_message_terminal_roundtrip() -> None:
    original = Message(
        payload=SmokePayload(text="bye", kind="done"),
        isTerminal=True,
    )
    payload = json.loads(json.dumps(original.encode()))
    restored = jsonDecode(payload)

    assert isinstance(restored, Message)
    assert restored.isTerminal is True
    assert restored.payload.text == "bye"


def test_ioqueue_send_receive() -> None:
    left, right = IOQueue.createPair()
    sender = IOQueue(outboundQueue=left, inboundQueue=right)
    receiver = IOQueue(outboundQueue=right, inboundQueue=left)

    correlationId = UUID("12345678-1234-5678-1234-567812345678")
    message = Message(
        payload=SmokePayload(text="queue", kind="ping"),
        correlationId=correlationId,
    )
    sender.send(message)

    received = receiver.receive(timeout=1.0)
    assert isinstance(received, Message)
    assert received.payload.text == "queue"
    assert received.payload.kind == "ping"
    assert received.correlationId == correlationId
    assert received.isTerminal is False
