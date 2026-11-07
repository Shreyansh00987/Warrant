"""
Warrant Switch Agent Protocol Client.
Connects Clerk to the Switch Agent Bridge via HTTP + SSE stream.
Dispatches incoming room messages directly into Clerk's deterministic state machine.
"""

from __future__ import annotations
import json
import os
import time
import urllib.request
import urllib.error
from typing import Any, Callable, Dict, Optional

from clerk.service import process_room_event


class SwitchClient:
    def __init__(
        self,
        server_url: Optional[str] = None,
        room_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        db_path: Optional[str] = None,
    ):
        self.server_url = (server_url or os.getenv("SWITCH_SERVER_URL", "http://localhost:8080")).rstrip("/")
        self.room_id = room_id or os.getenv("SWITCH_ROOM_ID", "warrant-room")
        self.agent_id = agent_id or os.getenv("SWITCH_AGENT_ID", "warrant-clerk")
        self.db_path = db_path
        self.running = False

    def post_message(self, content: str) -> bool:
        """Posts an outbound message from Clerk into the Switch room."""
        url = f"{self.server_url}/gateway/rooms/{self.room_id}/messages"
        payload = {
            "sender": self.agent_id,
            "content": content,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                return resp.getcode() in (200, 201)
        except Exception:
            return False

    def handle_incoming_frame(self, frame_json: str) -> Optional[Dict[str, Any]]:
        """Parses an incoming SSE data frame and invokes Clerk processing."""
        try:
            data = json.loads(frame_json)
            result = process_room_event(data, db_path=self.db_path)
            return result
        except Exception as exc:
            return {"error": str(exc)}

    def listen_sse(self, on_event: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
        """
        Listens to Server-Sent Events (SSE) stream from Switch Agent Bridge.
        Re-establishes connection on disconnection.
        """
        url = f"{self.server_url}/api/v1/events?room_id={self.room_id}&agent_id={self.agent_id}"
        self.running = True

        while self.running:
            try:
                req = urllib.request.Request(
                    url,
                    headers={"Accept": "text/event-stream"},
                )
                with urllib.request.urlopen(req, timeout=60.0) as resp:
                    for line_bytes in resp:
                        if not self.running:
                            break
                        line = line_bytes.decode("utf-8").strip()
                        if line.startswith("data:"):
                            payload_str = line[5:].strip()
                            res = self.handle_incoming_frame(payload_str)
                            if on_event and res:
                                on_event(res)
            except Exception:
                # Backoff before reconnecting
                time.sleep(3.0)


if __name__ == "__main__":
    client = SwitchClient()
    print(f"Connecting Warrant Clerk to Switch bridge at {client.server_url} for room {client.room_id}...")
    client.listen_sse(lambda r: print("Handled Switch event:", r))
