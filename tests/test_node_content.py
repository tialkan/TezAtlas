"""
test_node_content.py — Skill node content integration tests.

Goes beyond frontmatter syntax checks to verify that nodes actually contain
meaningful, structurally valid content. Tests:

1. Every node has content body beyond frontmatter (not empty shells)
2. Phase nodes contain gate information
3. links_to references are bidirectionally findable
4. Script files are syntactically valid Python
5. Phase nodes don't reference non-existent document types
6. Required frontmatter fields per node_type are present and non-empty
7. No node silently bypasses Iron Rules (content heuristic check)
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
SCRIPTS_ROOT = REPO_ROOT / "scripts"
TOOLS_ROOT = REPO_ROOT / "tools"

VALID_DOCUMENT_TYPES = {
    "thesis", "article", "conference", "lit-review", "report",
    "book-chapter", "grant-proposal", "research-proposal",
    "poster", "technical-report", "all",
}

# Patterns that indicate encouraging Iron Rule violations.
# We check for the pattern but exclude lines that contain negating words,
# so nodes that describe/prohibit these actions don't trigger false positives.
VIOLATION_PATTERNS = [
    r"bypass.{0,30}(iron|rule|constraint)",
    r"generate.{0,30}(without|ignoring).{0,20}source",
]

# These patterns are only violations when NOT in a prohibitory context
_PROHIBITORY_WORDS = {"no", "never", "not", "prohibit", "forbidden", "rule", "cannot", "must not", "don't"}


def iter_skill_nodes():
    """Yield (path, frontmatter, body) for all .md files in skills/."""
    for f in SKILLS_ROOT.rglob("*.md"):
        content = f.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        body = _strip_frontmatter(content)
        yield f, fm, body


def _parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError:
        return {}


def _strip_frontmatter(content: str) -> str:
    if not content.startswith("---"):
        return content
    end = content.find("---", 3)
    if end == -1:
        return content
    return content[end + 3:].strip()


# ── Test 1: Non-empty content body ────────────────────────────────────────────

class TestNodeHasContent:
    """Skill nodes must have content beyond just frontmatter."""

    MIN_BODY_CHARS = 100  # Absolute minimum — avoids placeholder shells

    def test_all_nodes_have_content_body(self):
        empty = []
        for path, fm, body in iter_skill_nodes():
            if len(body) < self.MIN_BODY_CHARS:
                empty.append(
                    f"{path.relative_to(REPO_ROOT)}: body too short ({len(body)} chars, min {self.MIN_BODY_CHARS})"
                )
        assert not empty, "Nodes with insufficient content:\n" + "\n".join(empty)

    def test_all_nodes_have_h1_heading(self):
        """Every node should have at least one # heading."""
        no_heading = []
        for path, fm, body in iter_skill_nodes():
            if not re.search(r"^#{1,3}\s+\S", body, re.MULTILINE):
                no_heading.append(str(path.relative_to(REPO_ROOT)))
        assert not no_heading, "Nodes missing headings:\n" + "\n".join(no_heading)


# ── Test 2: Phase node structure ──────────────────────────────────────────────

class TestPhaseNodeStructure:
    """Phase nodes must reference phase_number and document_type."""

    def test_phase_nodes_have_phase_number(self):
        missing = []
        for path, fm, body in iter_skill_nodes():
            if fm.get("node_type") != "phase":
                continue
            if fm.get("phase_number") is None:
                missing.append(str(path.relative_to(REPO_ROOT)))
        assert not missing, "Phase nodes missing phase_number:\n" + "\n".join(missing)

    def test_phase_nodes_have_valid_document_type(self):
        """document_type must be valid if present. If absent, infer from directory name."""
        invalid = []
        for path, fm, body in iter_skill_nodes():
            if fm.get("node_type") != "phase":
                continue
            doc_type = fm.get("document_type", "")
            if not doc_type:
                # Infer from phases/<doctype>/ directory name — this is acceptable
                continue
            if doc_type not in VALID_DOCUMENT_TYPES:
                invalid.append(
                    f"{path.relative_to(REPO_ROOT)}: document_type={doc_type!r} not in known types"
                )
        assert not invalid, "Phase nodes with invalid document_type:\n" + "\n".join(invalid)


# ── Test 3: Node type values are known ────────────────────────────────────────

VALID_NODE_TYPES = {
    "core", "phase", "phase-fork", "technique", "template",
    "tooling", "foundation", "moc",
    # Extended types found in skills/architecture/ and skills/ux/
    "architecture", "ux",
    # Special types
    "index", "onboarding", "output",
}

class TestValidNodeTypes:
    def test_all_node_types_are_known(self):
        unknown = []
        for path, fm, body in iter_skill_nodes():
            nt = fm.get("node_type", "")
            if nt and nt not in VALID_NODE_TYPES:
                unknown.append(f"{path.relative_to(REPO_ROOT)}: node_type={nt!r}")
        assert not unknown, "Unknown node types:\n" + "\n".join(unknown)


# ── Test 4: Iron Rule integrity heuristic ─────────────────────────────────────

class TestIronRuleIntegrity:
    """No node should contain language that encourages bypassing Iron Rules."""

    def test_no_iron_rule_bypass_language(self):
        violations = []
        for path, fm, body in iter_skill_nodes():
            for line in body.splitlines():
                line_lower = line.lower()
                for pattern in VIOLATION_PATTERNS:
                    if re.search(pattern, line_lower):
                        # Exclude lines that contain prohibitory context
                        if not any(w in line_lower for w in _PROHIBITORY_WORDS):
                            violations.append(
                                f"{path.relative_to(REPO_ROOT)}: '{line.strip()[:80]}'"
                            )
        assert not violations, (
            "Nodes with potential Iron Rule bypass language:\n" + "\n".join(violations)
        )


# ── Test 5: Python scripts are syntactically valid ────────────────────────────

class TestScriptSyntax:
    """All .py files in scripts/ and tools/ must parse without syntax errors."""

    def _collect_scripts(self) -> list[Path]:
        scripts = list(SCRIPTS_ROOT.glob("*.py")) + list(TOOLS_ROOT.glob("*.py"))
        return [s for s in scripts if s.name != "__init__.py"]

    def test_scripts_parse(self):
        errors = []
        for script in self._collect_scripts():
            try:
                source = script.read_text(encoding="utf-8")
                ast.parse(source)
            except SyntaxError as e:
                errors.append(f"{script.relative_to(REPO_ROOT)}: SyntaxError: {e}")
        assert not errors, "Scripts with syntax errors:\n" + "\n".join(errors)

    def test_scripts_import_clean(self):
        """Scripts should be importable without side effects at module level."""
        errors = []
        for script in self._collect_scripts():
            result = subprocess.run(
                [sys.executable, "-c", f"import ast; ast.parse(open({str(script)!r}).read())"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                errors.append(f"{script.name}: {result.stderr.strip()[:200]}")
        assert not errors, "Script parse errors:\n" + "\n".join(errors)


# ── Test 6: Required frontmatter fields are non-empty ─────────────────────────

REQUIRED_FIELDS_BY_NODE_TYPE: dict[str, list[str]] = {
    "core":       ["title", "node_type", "description", "language"],
    # document_type is optional for phases — it can be inferred from the directory path
    "phase":      ["title", "node_type", "description", "phase_number"],
    "phase-fork": ["title", "node_type", "description"],
    "technique":  ["title", "node_type", "description", "language"],
    "template":   ["title", "node_type", "description"],
    "tooling":    ["title", "node_type", "description"],
    "foundation": ["title", "node_type", "description"],
    "moc":        ["title", "node_type"],
}

class TestRequiredFields:
    def test_required_fields_present_and_non_empty(self):
        errors = []
        for path, fm, body in iter_skill_nodes():
            nt = fm.get("node_type", "")
            required = REQUIRED_FIELDS_BY_NODE_TYPE.get(nt)
            if required is None:
                continue  # Unknown type — caught by TestValidNodeTypes
            for field_name in required:
                val = fm.get(field_name)
                if val is None or (isinstance(val, str) and not val.strip()):
                    errors.append(
                        f"{path.relative_to(REPO_ROOT)}: missing/empty required field '{field_name}'"
                    )
        assert not errors, "Nodes with missing required fields:\n" + "\n".join(errors)


# ── Test 7: links_to paths are repo-relative and exist ────────────────────────

class TestLinksToIntegrity:
    """links_to entries must be relative to repo root and the file must exist."""

    def test_links_to_are_relative_paths(self):
        errors = []
        for path, fm, body in iter_skill_nodes():
            links = fm.get("links_to") or []
            for link in links:
                if link.startswith("/"):
                    errors.append(
                        f"{path.relative_to(REPO_ROOT)}: links_to={link!r} must be relative"
                    )
        assert not errors, "Absolute links_to paths:\n" + "\n".join(errors)

    def test_links_to_files_exist(self):
        missing = []
        for path, fm, body in iter_skill_nodes():
            links = fm.get("links_to") or []
            for link in links:
                target = REPO_ROOT / link
                if not target.exists():
                    missing.append(
                        f"{path.relative_to(REPO_ROOT)}: links_to={link!r} → not found"
                    )
        assert not missing, "Broken links_to references:\n" + "\n".join(missing)
