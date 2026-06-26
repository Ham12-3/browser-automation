import json
import struct
import sys
from typing import Any

import httpx


AGENT_URL = "http://127.0.0.1:8765/extension/message"


def read_message() -> dict[str, Any] | None:
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return None
    message_length = struct.unpack("@I", raw_length)[0]
    return json.loads(sys.stdin.buffer.read(message_length).decode("utf-8"))


def write_message(message: dict[str, Any]) -> None:
    encoded = json.dumps(message).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("@I", len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def main() -> None:
    while True:
        message = read_message()
        if message is None:
            return
        try:
            response = httpx.post(AGENT_URL, json=message, timeout=10)
            write_message(response.json())
        except Exception as exc:
            write_message({"accepted": False, "error": str(exc)})


if __name__ == "__main__":
    main()

