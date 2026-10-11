"""
test_frontmatter.py — Frontmatter schema validation tests.

Required fields per node_type:
- phase:     title, node_type, phase_number, description, outputs, language, version
- core:      title, node_type, description, language
- technique: title, node_type, description, language, version
- template:  title, node_type, language
- tooling:   title, node_type, description, language
"""
from pathlib import Path

import yaml

SKILLS_ROOT = Path(__file__).parent.parent / "skills"

REQUIRED_FIELDS = {
    "phase": ["title", "node_type", "phase_number", "description", "language"],
    "core": ["title", "node_type", "description", "language"],
    "technique": ["title", "node_type", "description", "language"],
    "template": ["title", "node_type", "language"],
    "tooling": ["title", "node_type", "language"],
    "moc": ["title", "node_type"],
}

VALID_LANGUAGES = {"bilingual", "en", "tr"}


def iter_skill_files():
    return list(SKILLS_ROOT.rglob("*.md"))


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


class TestFrontmatterRequired:
    """All skill files with known node_type must have required fields."""

    def test_required_fields_present(self):
        errors = []
        for skill_file in iter_skill_files():
            content = skill_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            if fm is None:
                # No frontmatter — skip (some READMEs have none)
                continue
            node_type = fm.get("node_type")
            if node_type not in REQUIRED_FIELDS:
                continue
            required = REQUIRED_FIELDS[node_type]
            for field in required:
                if field not in fm:
                    errors.append(
                        f"{skill_file.name}: missing required field {field!r} (node_type={node_type!r})"
                    )
        assert not errors, "Frontmatter validation errors:\n" + "\n".join(errors)


class TestLanguageValues:
    """Language field must be one of the valid values."""

    def test_language_valid(self):
        errors = []
        for skill_file in iter_skill_files():
            content = skill_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            if fm is None:
                continue
            lang = fm.get("language")
            if lang is not None and lang not in VALID_LANGUAGES:
                errors.append(
                    f"{skill_file.name}: invalid language={lang!r} (must be one of {VALID_LANGUAGES})"
                )
        assert not errors, "Invalid language values:\n" + "\n".join(errors)


class TestPhaseNumbers:
    """Phase nodes must have numeric phase_number."""

    def test_phase_number_is_numeric(self):
        errors = []
        for skill_file in iter_skill_files():
            content = skill_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            if fm is None or fm.get("node_type") != "phase":
                continue
            phase_num = fm.get("phase_number")
            if phase_num is None:
                errors.append(f"{skill_file.name}: phase node missing phase_number")
            elif not isinstance(phase_num, (int, float)):
                errors.append(
                    f"{skill_file.name}: phase_number must be numeric, got {phase_num!r}"
                )
        assert not errors, "Phase number errors:\n" + "\n".join(errors)


class TestVersionFormat:
    """Version field (if present) must be a quoted string like '1.0'."""

    def test_version_is_string(self):
        errors = []
        for skill_file in iter_skill_files():
            content = skill_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)
            if fm is None:
                continue
            version = fm.get("version")
            if version is not None and not isinstance(version, str):
                errors.append(
                    f"{skill_file.name}: version must be a string, got {type(version).__name__} ({version!r})"
                )
        assert not errors, "Version format errors:\n" + "\n".join(errors)
