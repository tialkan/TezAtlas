#!/usr/bin/env python3
"""
scripts/session_end.py — TezAtlas Session End Helper

Updates STATUS.md with session outcomes, generates DASHBOARD.md,
and prints a session summary for the user.

Usage:
    python3 scripts/session_end.py [options]

Options:
    --project-dir PATH       Project root (default: current dir)
    --summary TEXT           Short session summary (what was done)
    --sources-read N         Number of sources read this session (default: 0)
    --words-written N        Words written this session (default: 0)
    --next-actions TEXT ...  Upcoming action items (repeatable)
    --blockers TEXT ...      Active blockers (repeatable)
    --goals-met              Flag: mark session goals as met

Called by /tezatlas at session end (Iron Rule 6 enforcer).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from core.session import TezAtlasSession


def main() -> None:
    parser = argparse.ArgumentParser(description="TezAtlas session end helper")
    parser.add_argument("--project-dir", type=Path, default=Path("."))
    parser.add_argument("--summary", type=str, default="Session completed.")
    parser.add_argument("--sources-read", type=int, default=0, dest="sources_read")
    parser.add_argument("--words-written", type=int, default=0, dest="words_written")
    parser.add_argument(
        "--next-actions", nargs="*", default=[], dest="next_actions",
        metavar="ACTION",
    )
    parser.add_argument(
        "--blockers", nargs="*", default=[], metavar="BLOCKER",
    )
    parser.add_argument("--goals-met", action="store_true", dest="goals_met")
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    status_path = project_dir / "STATUS.md"

    if not status_path.exists():
        print("STATUS.md not found. Cannot update session.", file=sys.stderr)
        sys.exit(1)

    sess = TezAtlasSession(project_dir)

    # Run end_session → updates STATUS.md + generates DASHBOARD.md
    state = sess.end_session(
        summary=args.summary,
        sources_read_delta=args.sources_read,
        words_written=args.words_written,
        next_actions=args.next_actions,
        blockers=args.blockers,
        goals_met=args.goals_met,
    )

    # Print confirmation
    streak = int((state.get("writing_schedule") or {}).get("current_streak", 0))
    total_sessions = int((state.get("writing_schedule") or {}).get("total_sessions", 0))
    phase = int(state.get("current_phase", 0))
    phase_name = state.get("_phase_name", f"Phase {phase}")

    print("✅ Session saved to STATUS.md")
    print("📊 DASHBOARD.md updated")
    print()
    print(f"  Phase        : {phase} — {phase_name}")
    print(f"  Streak       : {streak} days")
    print(f"  Sessions     : {total_sessions} total")
    if args.sources_read:
        print(f"  Sources read : +{args.sources_read} this session")
    if args.words_written:
        print(f"  Words written: +{args.words_written} this session")
    print()
    print("💾 Don't forget Iron Rule 6: git add . && git commit -m 'chore(session): ...'")


if __name__ == "__main__":
    main()
