#!/usr/bin/env python3
"""
Pre-commit hook: warn (non-blocking) if STATUS.md hasn't been updated in > 7 days.
Iron Rule 6: git commit mandatory after every session — if STATUS.md is stale,
it means sessions are happening without proper close-out.
"""
import os
import sys
from datetime import datetime, timezone

STALENESS_THRESHOLD_DAYS = 7
STATUS_FILE = "STATUS.md"
WARNING_ONLY = True  # Warn but don't block (exit 0)


def main():
    if not os.path.exists(STATUS_FILE):
        # No STATUS.md yet — project not started, fine
        sys.exit(0)

    mtime = os.path.getmtime(STATUS_FILE)
    last_modified = datetime.fromtimestamp(mtime, tz=timezone.utc)
    age_days = (datetime.now(tz=timezone.utc) - last_modified).days

    if age_days > STALENESS_THRESHOLD_DAYS:
        print(f"⚠️  STATUS.md hasn't been updated in {age_days} days")
        print(f"   Last modified: {last_modified.strftime('%Y-%m-%d')}")
        print("   Iron Rule 6: update STATUS.md at session end.")
        print("   (This is a warning only — commit is not blocked)")
        print()

    # Always exit 0 — this is a warning, not a blocker
    sys.exit(0)


if __name__ == "__main__":
    main()
