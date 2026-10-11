#!/usr/bin/env python3
"""
scripts/session_start.py — TezAtlas Session Start Helper

Reads STATUS.md in the current (or specified) project directory,
outputs a formatted session summary for Claude Code to display.

Usage:
    python3 scripts/session_start.py [--project-dir PATH] [--json]

Output (default): human-readable markdown summary
Output (--json):  raw JSON state dict for machine consumption

Called automatically by the /tezatlas command during Resume Mode.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure project root is importable
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from core.session import TezAtlasSession


def _format_summary(state: dict) -> str:
    doc_type = state.get("document_type", "thesis")
    phase = int(state.get("current_phase", 0))
    phase_name = state.get("_phase_name", f"Phase {phase}")
    attrition_risk = state.get("_attrition_risk", "low")
    days_inactive = int(state.get("_days_inactive", 0))
    streak = int((state.get("writing_schedule") or {}).get("current_streak", 0))
    total_sources = int((state.get("sources") or {}).get("total_collected", 0))
    read_sources = int((state.get("sources") or {}).get("read", 0))
    saturation = (state.get("sources") or {}).get("saturation_reached", False)
    arg_count = int(state.get("_argumanlar_count", 0))
    savunma_exists = state.get("_savunma_zirhi_exists", False)
    next_actions = state.get("next_actions") or []
    blockers = state.get("blockers") or []

    risk_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(attrition_risk, "🟢")

    lines = [
        "## TezAtlas — Session State",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Document Type | `{doc_type}` |",
        f"| Current Phase | **Phase {phase}: {phase_name}** |",
        f"| Sources | {read_sources}/{total_sources} read {'✅' if saturation else '⏳'} |",
        f"| Arguments | {arg_count} {'✅' if arg_count >= 5 else ('⚠️' if arg_count >= 3 else '❌')} |",
        f"| Defense Armor | {'✅ Present' if savunma_exists else '❌ Missing'} |",
        f"| Writing Streak | {streak} days |",
        f"| Days Inactive | {days_inactive} days |",
        f"| Attrition Risk | {risk_icon} {attrition_risk.upper()} |",
    ]

    if blockers:
        lines += ["", "**Active Blockers:**"]
        for b in blockers:
            lines.append(f"- 🔴 {b}")

    if next_actions:
        lines += ["", "**Next Actions:**"]
        for a in next_actions[:3]:
            lines.append(f"- [ ] {a}")

    if attrition_risk == "high":
        lines += [
            "",
            "> ⚠️ **High attrition risk!** {days_inactive}+ days without a session.",
            "> Start with a small step — even 15 minutes counts.",
        ]
    elif attrition_risk == "medium":
        lines += [
            "",
            "> 💛 {days_inactive} days since last session. A short session today resets momentum.",
        ]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="TezAtlas session start helper")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("."),
        help="Project root directory (default: current dir)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output raw JSON state instead of formatted summary",
    )
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    status_path = project_dir / "STATUS.md"

    if not status_path.exists():
        print(
            "STATUS.md not found. This appears to be a new project.\n"
            "Run: python3 scripts/new_project.py --type <type> --lang <lang>",
            file=sys.stderr,
        )
        sys.exit(1)

    sess = TezAtlasSession(project_dir)
    state = sess.load()

    if args.as_json:
        print(json.dumps(state, ensure_ascii=False, indent=2, default=str))
    else:
        print(_format_summary(state))


if __name__ == "__main__":
    main()
