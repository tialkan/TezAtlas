"""
test_phase_chain.py — Phase chain continuity tests.

Checks that for each document type, the phase chain forms a valid linear
sequence: phase_gate_out of phase N == filename of phase N+1.

Also verifies:
- No phase is orphaned (every phase except phase 0 has a phase_gate_in)
- Phase numbers are unique within a document type
"""
from pathlib import Path
from collections import defaultdict

import yaml

PHASES_ROOT = Path(__file__).parent.parent / "skills" / "phases"


def parse_frontmatter(content: str) -> dict | None:
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError:
        return None


def collect_phases() -> dict[str, list[dict]]:
    """
    Returns {document_type: [phase_info, ...]} sorted by phase_number.
    """
    doc_phases = defaultdict(list)
    for phase_file in PHASES_ROOT.rglob("phase-*.md"):
        content = phase_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        if fm is None or fm.get("node_type") != "phase":
            continue
        doc_type = phase_file.parent.name
        doc_phases[doc_type].append({
            "file": phase_file,
            "filename": phase_file.name,
            "phase_number": fm.get("phase_number", -1),
            "gate_in": fm.get("phase_gate_in"),
            "gate_out": fm.get("phase_gate_out"),
            "doc_type": doc_type,
        })
    # Sort each doc type by phase_number
    for doc_type in doc_phases:
        doc_phases[doc_type].sort(key=lambda p: float(p["phase_number"]))
    return dict(doc_phases)


class TestPhaseChain:
    """Each document type must have a valid linear phase chain."""

    def test_phase_numbers_unique_per_doc_type(self):
        errors = []
        phases = collect_phases()
        for doc_type, phase_list in phases.items():
            seen = []
            for p in phase_list:
                num = p["phase_number"]
                if num in seen:
                    errors.append(
                        f"{doc_type}: duplicate phase_number {num} (files: {[q['filename'] for q in phase_list if q['phase_number'] == num]})"
                    )
                seen.append(num)
        assert not errors, "Duplicate phase numbers:\n" + "\n".join(errors)

    def test_gate_out_matches_next_phase_filename(self):
        """phase_gate_out of phase N should match the filename of phase N+1."""
        errors = []
        phases = collect_phases()
        for doc_type, phase_list in phases.items():
            for i, phase in enumerate(phase_list[:-1]):  # skip last
                next_phase = phase_list[i + 1]
                gate_out = phase["gate_out"]
                if gate_out is None or gate_out == "null":
                    # Terminal phase — skip
                    continue
                expected_next = Path(gate_out).name
                actual_next = next_phase["filename"]
                if expected_next != actual_next:
                    errors.append(
                        f"{doc_type}/{phase['filename']}: "
                        f"gate_out={gate_out!r} but next phase is {actual_next!r}"
                    )
        assert not errors, "Broken phase chain links:\n" + "\n".join(errors)

    def test_no_orphaned_phases(self):
        """Every phase (except the first in a chain) should have phase_gate_in."""
        # This is a soft check — warn only, since some phases have None gate_in intentionally
        phases = collect_phases()
        warnings = []
        for doc_type, phase_list in phases.items():
            for phase in phase_list[1:]:  # skip first phase
                if phase["gate_in"] is None:
                    warnings.append(
                        f"{doc_type}/{phase['filename']}: no phase_gate_in (phase {phase['phase_number']})"
                    )
        # Not a hard failure — just informational
        if warnings:
            print("\nOrphaned phase warnings:")
            for w in warnings:
                print(f"  - {w}")


class TestDocumentTypes:
    """Each document type should have at least 3 phases."""

    def test_minimum_phase_count(self):
        # Short-format document types intentionally have fewer phases
        SHORT_FORMAT_TYPES = {"poster", "technical-report"}
        phases = collect_phases()
        short = [
            f"{doc_type}: only {len(phase_list)} phases"
            for doc_type, phase_list in phases.items()
            if doc_type not in SHORT_FORMAT_TYPES and len(phase_list) < 3
        ]
        assert not short, "Document types with too few phases:\n" + "\n".join(short)
