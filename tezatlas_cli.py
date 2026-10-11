#!/usr/bin/env python3
"""
tezatlas_cli.py — Universal CLI for TezAtlas

Works with ANY AI tool or standalone from the terminal.
No Claude Code dependency.

Usage:
  python3 tezatlas_cli.py <command> [options]
  python3 tezatlas_cli.py intake
  python3 tezatlas_cli.py gaps --project-dir ~/thesis
  python3 tezatlas_cli.py import --type thesis --lang tr --field law

Install as global command:
  pip install -e .   (if setup.py/pyproject.toml configured)
  # or
  alias tezatlas='python3 /path/to/tezatlas_cli.py'
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent
_SCRIPTS = _ROOT / "scripts"


# ── Command Registry ─────────────────────────────────────────────────────────

COMMANDS = {
    # Project Management
    "new": {
        "script": "new_project.py",
        "help": "Create new TezAtlas project",
        "pass_project_dir": False,
    },
    "import": {
        "script": "import_project.py",
        "help": "Import existing academic work into TezAtlas",
        "pass_project_dir": True,
        "dir_flag": "--dir",
    },
    "status": {
        "script": "session_start.py",
        "help": "Show current project status",
        "pass_project_dir": True,
    },
    "session-start": {
        "script": "session_start.py",
        "help": "Start a new session (load state)",
        "pass_project_dir": True,
    },
    "session-end": {
        "script": "session_end.py",
        "help": "End session (save state)",
        "pass_project_dir": True,
    },
    "gate": {
        "script": "phase_gate_check.py",
        "help": "Run phase gate validation",
        "pass_project_dir": True,
    },

    # Literature Intelligence
    "intake": {
        "script": "intake_protocol.py",
        "help": "Source clustering + conflict detection → SOURCE_MAP.md",
        "pass_project_dir": True,
    },
    "contradictions": {
        "script": "contradiction_scan.py",
        "help": "Cross-source contradiction analysis → CONTRADICTIONS.md",
        "pass_project_dir": True,
    },
    "citation-chain": {
        "script": "citation_chain.py",
        "help": "Intellectual lineage tracking → CITATION_CHAIN.md",
        "pass_project_dir": True,
    },
    "gaps": {
        "script": "gap_scanner.py",
        "help": "Research gap detection → GAPS.md",
        "pass_project_dir": True,
    },
    "assumptions": {
        "script": "assumption_killer.py",
        "help": "Untested assumption detection → ASSUMPTIONS.md",
        "pass_project_dir": True,
    },
    "knowledge-map": {
        "script": "knowledge_map.py",
        "help": "Field structure mapping → KNOWLEDGE_MAP.md",
        "pass_project_dir": True,
    },
    "so-what": {
        "script": "so_what_test.py",
        "help": "'So What?' significance test → SO_WHAT.md",
        "pass_project_dir": True,
    },
    "synthesize": {
        "script": "synthesize.py",
        "help": "Multi-source synthesis → SYNTHESIS.md",
        "pass_project_dir": True,
    },

    # Source Management
    "find-source": {
        "script": "find_source.py",
        "help": "Search and download academic sources",
        "pass_project_dir": False,
    },
    "reading": {
        "script": "reading_tracker.py",
        "help": "Reading tracker (sync/status/mark)",
        "pass_project_dir": True,
    },
    "snowball": {
        "script": "snowball.py",
        "help": "Snowball sampling from notes",
        "pass_project_dir": True,
    },
    "saturation": {
        "script": "saturation_map.py",
        "help": "Reading saturation check",
        "pass_project_dir": True,
    },

    # Writing & Review
    "style-lint": {
        "script": None,
        "tool": "style_linter.py",
        "help": "Style check (passive voice, hedging, over-claiming)",
        "pass_project_dir": False,
    },
    "bibtex": {
        "script": None,
        "tool": "bibtex_generator.py",
        "help": "Generate BibTeX/RIS citations from DOI",
        "pass_project_dir": False,
    },
    "rq-drift": {
        "script": "rq_drift.py",
        "help": "Research question drift detection",
        "pass_project_dir": True,
    },
}


# ── Runner ────────────────────────────────────────────────────────────────────

def run_command(cmd_name: str, cmd_info: dict, extra_args: list[str],
                project_dir: Path) -> int:
    """Run a TezAtlas command script."""
    if cmd_info.get("tool"):
        script_path = _ROOT / "tools" / cmd_info["tool"]
    else:
        script_path = _SCRIPTS / cmd_info["script"]

    if not script_path.exists():
        print(f"Error: Script not found: {script_path}", file=sys.stderr)
        return 1

    cmd = [sys.executable, str(script_path)]

    # Add project dir flag if needed
    if cmd_info.get("pass_project_dir"):
        dir_flag = cmd_info.get("dir_flag", "--project-dir")
        # Only add if not already in extra_args
        if dir_flag not in extra_args and "--dir" not in extra_args:
            cmd.extend([dir_flag, str(project_dir)])

    cmd.extend(extra_args)

    try:
        result = subprocess.run(cmd, cwd=str(_ROOT))
        return result.returncode
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="tezatlas",
        description="TezAtlas — Universal Academic Workflow CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_build_help_text(),
    )
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("--project-dir", "-d", type=Path, default=Path("."),
                        help="Project directory (default: current)")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all available commands")

    args, extra = parser.parse_known_args()

    if args.list or not args.command:
        _print_command_list()
        return

    cmd_name = args.command.lower()

    if cmd_name not in COMMANDS:
        # Try fuzzy match
        matches = [c for c in COMMANDS if c.startswith(cmd_name)]
        if len(matches) == 1:
            cmd_name = matches[0]
        else:
            print(f"Unknown command: {cmd_name}")
            if matches:
                print(f"Did you mean: {', '.join(matches)}?")
            print("\nRun 'tezatlas --list' to see all commands.")
            sys.exit(1)

    project_dir = args.project_dir.resolve()
    exit_code = run_command(cmd_name, COMMANDS[cmd_name], extra, project_dir)
    sys.exit(exit_code)


def _print_command_list() -> None:
    """Print formatted command list."""
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  TezAtlas — Universal Academic Workflow CLI                  ║")
    print("║  Works with any AI tool or standalone                       ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║                                                              ║")

    categories = {
        "PROJECT MANAGEMENT": ["new", "import", "status", "session-start", "session-end", "gate"],
        "LITERATURE INTELLIGENCE": ["intake", "contradictions", "citation-chain", "gaps",
                                     "assumptions", "knowledge-map", "so-what", "synthesize"],
        "SOURCE MANAGEMENT": ["find-source", "reading", "snowball", "saturation"],
        "WRITING & REVIEW": ["style-lint", "bibtex", "rq-drift"],
    }

    for cat_name, cmd_names in categories.items():
        print(f"║  📋 {cat_name:<55}║")
        for name in cmd_names:
            info = COMMANDS[name]
            line = f"  {name:<18} {info['help']}"
            print(f"║  {line:<58}║")
        print("║                                                              ║")

    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  Usage: tezatlas <command> [options]                         ║")
    print("║  Example: tezatlas intake --project-dir ~/thesis             ║")
    print("║  Help: tezatlas <command> --help                             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()


def _build_help_text() -> str:
    lines = ["\nCommands:"]
    for name, info in COMMANDS.items():
        lines.append(f"  {name:<18} {info['help']}")
    lines.append("\nRun 'tezatlas <command> --help' for command-specific options.")
    lines.append("Run 'tezatlas --list' for the full command reference.")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
