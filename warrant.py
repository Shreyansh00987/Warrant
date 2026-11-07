#!/usr/bin/env python3
"""
Warrant CLI Entrypoint.
Usage:
    python warrant.py verify <commit-sha> [--tamper]
    python warrant.py seed
    python warrant.py serve [--port 8000]
"""

from __future__ import annotations
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(prog="warrant")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # verify
    verify_p = subparsers.add_parser("verify", help="Verify commit SHA provenance and scope")
    verify_p.add_argument("commit_sha", help="Git commit SHA to verify")
    verify_p.add_argument("--db", default=None, help="Database path")
    verify_p.add_argument("--tamper", action="store_true", help="Simulate tampered record")

    # seed
    seed_p = subparsers.add_parser("seed", help="Seed database with W-014 and W-015")
    seed_p.add_argument("--db", default=None, help="Database path")

    # replay
    replay_p = subparsers.add_parser("replay", help="Replay Switch room event stream fixture")
    replay_p.add_argument("fixture", help="Path to JSON fixture file")
    replay_p.add_argument("--db", default=None, help="Database path")
    replay_p.add_argument("--delay", type=float, default=0.2, help="Delay between turns")

    # serve
    serve_p = subparsers.add_parser("serve", help="Run Clerk FastAPI server")
    serve_p.add_argument("--host", default="0.0.0.0", help="Host")
    serve_p.add_argument("--port", type=int, default=8000, help="Port")

    args = parser.parse_args()

    if args.command == "verify":
        from verify.warrant_verify import run_verify
        code = run_verify(args.commit_sha, db_path=args.db, simulate_tamper=args.tamper)
        sys.exit(code)

    elif args.command == "seed":
        from clerk.seed import seed_database
        seed_database(args.db)
        print("Successfully seeded W-014 (pass) and W-015 (drift/scope violation).")

    elif args.command == "replay":
        from switch.replay import replay_fixture
        code = replay_fixture(args.fixture, db_path=args.db, delay_sec=args.delay)
        sys.exit(code)

    elif args.command == "serve":
        import uvicorn
        uvicorn.run("clerk.main:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    main()
