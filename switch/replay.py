"""
Warrant Switch Room Event Replay Runner.
Replays captured Switch room fixtures through Clerk's deterministic state machine.
Usage:
    python -m switch.replay switch/fixtures/pass_run.json
    python -m switch.replay switch/fixtures/drift_run.json
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import time

from clerk.db import init_db
from clerk.service import process_room_event


def replay_fixture(
    fixture_path: str,
    db_path: str | None = None,
    delay_sec: float = 0.5,
) -> int:
    if not os.path.exists(fixture_path):
        print(f"[ERROR] Fixture file not found: {fixture_path}")
        return 1

    init_db(db_path)

    with open(fixture_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    print("\n" + "=" * 65)
    print(f" SWITCH ROOM REPLAY RUNNER: {os.path.basename(fixture_path)}")
    print(f" Total Events in Stream: {len(events)}")
    print("=" * 65)

    last_status = "UNKNOWN"

    for idx, evt in enumerate(events, start=1):
        sender = evt.get("sender", "unknown")
        content = evt.get("content", "")
        preview = content.split("\n")[0]
        if len(preview) > 60:
            preview = preview[:57] + "..."

        print(f"\n[Turn {idx}/{len(events)}] [{sender.upper()}]")
        print(f"  Content: \"{preview}\"")

        # Process through Clerk's deterministic gatekeeper
        result = process_room_event(evt, db_path=db_path)

        handled = result.get("handled", False)
        status = result.get("status", "NO_CHANGE")
        last_status = status

        if result.get("error"):
            print(f"  -> CLERK GATE: [REJECTED] {result.get('error')}")
        elif handled:
            print(f"  -> CLERK GATE: [STATE CHANGED] Status: {status}")
            if result.get("scope_result"):
                print(f"     Scope Check: {result['scope_result']}")
            if result.get("offending_files"):
                print(f"     Offending Files: {', '.join(result['offending_files'])}")
        else:
            print(f"  -> CLERK GATE: [OBSERVED] (no state change required)")

        if delay_sec > 0:
            time.sleep(delay_sec)

    print("\n" + "=" * 65)
    print(f" REPLAY COMPLETE. Final Warrant Status: {last_status}")
    print("=" * 65 + "\n")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Replay Switch Room event fixture through Warrant Clerk.")
    parser.add_argument("fixture", help="Path to JSON fixture file")
    parser.add_argument("--db", default=None, help="Database path")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between turns in seconds")
    args = parser.parse_args()

    sys.exit(replay_fixture(args.fixture, db_path=args.db, delay_sec=args.delay))


if __name__ == "__main__":
    main()
