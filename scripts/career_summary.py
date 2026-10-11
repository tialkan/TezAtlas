#!/usr/bin/env python3
"""
career_summary.py — TezAtlas Research Career Graph Reader

Reads CAREER_PROFILE.md and produces a summary:
  - Publication count and venues
  - Skills acquired per project
  - Skill gaps for target roles
  - Longitudinal timeline
  - Suggested next steps

Usage:
  python3 scripts/career_summary.py
  python3 scripts/career_summary.py --profile path/to/CAREER_PROFILE.md
  python3 scripts/career_summary.py --json           # machine-readable output
  python3 scripts/career_summary.py --gaps "grant"   # gaps for a specific target
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROFILE = REPO_ROOT / "CAREER_PROFILE.md"


@dataclass
class Publication:
    title: str
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    type: str = "article"  # article | conference | chapter | thesis | preprint


@dataclass
class Project:
    name: str
    year_start: int | None = None
    year_end: int | None = None
    field: str | None = None
    skills_gained: list[str] = field(default_factory=list)
    publications: list[str] = field(default_factory=list)
    status: str = "completed"  # active | completed | paused


@dataclass
class CareerProfile:
    name: str = ""
    field: str = ""
    target_roles: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    skill_gaps: dict[str, list[str]] = field(default_factory=dict)
    publications: list[Publication] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


def parse_career_profile(profile_path: Path) -> CareerProfile:
    """Parse CAREER_PROFILE.md. Handles both YAML frontmatter and Markdown sections."""
    if not profile_path.exists():
        print(f"✗ {profile_path} bulunamadı.")
        print("  Oluşturmak için: skills/core/research-career-graph.md şemasına bakın.")
        sys.exit(1)

    content = profile_path.read_text(encoding="utf-8")
    profile = CareerProfile()

    # Parse YAML frontmatter if present
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1)) or {}
            profile.raw = fm
            profile.name = fm.get("name", "")
            profile.field = fm.get("field", "")
            profile.target_roles = fm.get("target_roles", [])
            profile.skills = fm.get("skills", [])
            # Parse publications from frontmatter
            for pub in fm.get("publications", []):
                if isinstance(pub, dict):
                    profile.publications.append(Publication(
                        title=pub.get("title", ""),
                        year=pub.get("year"),
                        venue=pub.get("venue"),
                        doi=pub.get("doi"),
                        type=pub.get("type", "article"),
                    ))
            # Parse projects
            for proj in fm.get("projects", []):
                if isinstance(proj, dict):
                    profile.projects.append(Project(
                        name=proj.get("name", ""),
                        year_start=proj.get("year_start"),
                        year_end=proj.get("year_end"),
                        field=proj.get("field"),
                        skills_gained=proj.get("skills_gained", []),
                        publications=proj.get("publications", []),
                        status=proj.get("status", "completed"),
                    ))
            # Skill gaps per target role
            profile.skill_gaps = fm.get("skill_gaps", {})
        except yaml.YAMLError:
            pass

    # Also scan markdown body for ## Publications and ## Skills sections
    _parse_markdown_sections(content, profile)
    return profile


def _parse_markdown_sections(content: str, profile: CareerProfile) -> None:
    """Supplement frontmatter data with Markdown section parsing."""
    lines = content.split("\n")
    current_section = None
    for line in lines:
        if re.match(r"^## *(Publications|Yayınlar)", line, re.I):
            current_section = "publications"
        elif re.match(r"^## *(Skills|Beceriler)", line, re.I):
            current_section = "skills"
        elif re.match(r"^## *(Projects|Projeler)", line, re.I):
            current_section = "projects"
        elif re.match(r"^## ", line):
            current_section = None
        elif current_section == "skills" and line.startswith("- "):
            skill = line[2:].strip()
            if skill and skill not in profile.skills:
                profile.skills.append(skill)
        elif current_section == "publications" and line.startswith("- "):
            # Try to parse: "- Title (Year) — Venue. DOI: ..."
            pub_text = line[2:].strip()
            year_match = re.search(r"\((\d{4})\)", pub_text)
            year = int(year_match.group(1)) if year_match else None
            doi_match = re.search(r"DOI:\s*(\S+)", pub_text, re.I)
            doi = doi_match.group(1) if doi_match else None
            title = re.sub(r"\(\d{4}\).*", "", pub_text).strip().rstrip("—").strip()
            if title:
                existing_titles = {p.title.lower() for p in profile.publications}
                if title.lower() not in existing_titles:
                    profile.publications.append(Publication(title=title, year=year, doi=doi))


def compute_skill_gaps_for_target(profile: CareerProfile, target: str) -> list[str]:
    """Return known skill gaps for a target role from profile.skill_gaps."""
    # Check both exact match and partial match
    for key, gaps in profile.skill_gaps.items():
        if target.lower() in key.lower() or key.lower() in target.lower():
            return gaps
    return []


def print_summary(profile: CareerProfile, target_filter: str | None = None) -> None:
    print("\nTezAtlas — Araştırma Kariyer Grafiği Özeti")
    print("════════════════════════════════════════════")

    if profile.name:
        print(f"\nAraştırmacı : {profile.name}")
    if profile.field:
        print(f"Alan        : {profile.field}")
    if profile.target_roles:
        print(f"Hedef roller: {', '.join(profile.target_roles)}")

    # Publications
    pubs = profile.publications
    print(f"\n📚 Yayınlar ({len(pubs)})")
    if pubs:
        by_year: dict[int, list[Publication]] = {}
        no_year = []
        for p in pubs:
            if p.year:
                by_year.setdefault(p.year, []).append(p)
            else:
                no_year.append(p)
        for year in sorted(by_year.keys(), reverse=True):
            for p in by_year[year]:
                venue = f" — {p.venue}" if p.venue else ""
                doi = f" [DOI: {p.doi}]" if p.doi else ""
                print(f"  {year}  {p.title}{venue}{doi}")
        for p in no_year:
            print(f"  ?.??  {p.title}")
    else:
        print("  (Yayın bulunamadı — CAREER_PROFILE.md'ye ekleyin)")

    # Skills
    print(f"\n🔧 Beceriler ({len(profile.skills)})")
    if profile.skills:
        # Print in columns
        col = 3
        skills = profile.skills
        for i in range(0, len(skills), col):
            row = skills[i:i + col]
            print("  " + "  |  ".join(f"{s:<30}" for s in row))
    else:
        print("  (Beceri bulunamadı)")

    # Projects timeline
    if profile.projects:
        print(f"\n📁 Projeler ({len(profile.projects)})")
        for p in sorted(profile.projects, key=lambda x: x.year_start or 0, reverse=True):
            period = ""
            if p.year_start:
                period = f"{p.year_start}"
                if p.year_end:
                    period += f"–{p.year_end}"
                elif p.status == "active":
                    period += "–şimdi"
            status_icon = {"active": "🔵", "completed": "✅", "paused": "⏸"}.get(p.status, "")
            skills_note = f"  [{', '.join(p.skills_gained[:3])}]" if p.skills_gained else ""
            print(f"  {status_icon} {period:12} {p.name}{skills_note}")

    # Skill gaps
    print("\n⚠️  Beceri Eksiklikleri")
    if target_filter:
        gaps = compute_skill_gaps_for_target(profile, target_filter)
        if gaps:
            print(f"  [{target_filter}] için:")
            for g in gaps:
                print(f"    ✗ {g}")
        else:
            print(f"  '{target_filter}' için eksiklik kaydı bulunamadı")
    elif profile.skill_gaps:
        for role, gaps in profile.skill_gaps.items():
            print(f"  [{role}]:")
            for g in gaps[:5]:
                print(f"    ✗ {g}")
    else:
        print("  (Eksiklik kaydı yok — CAREER_PROFILE.md'ye ekleyin)")

    print(f"\n{'─'*50}")
    print(f"  Toplam: {len(pubs)} yayın · {len(profile.skills)} beceri · {len(profile.projects)} proje")


def to_json(profile: CareerProfile) -> dict:
    return {
        "name": profile.name,
        "field": profile.field,
        "target_roles": profile.target_roles,
        "publication_count": len(profile.publications),
        "publications": [
            {"title": p.title, "year": p.year, "venue": p.venue, "doi": p.doi, "type": p.type}
            for p in profile.publications
        ],
        "skill_count": len(profile.skills),
        "skills": profile.skills,
        "project_count": len(profile.projects),
        "projects": [
            {
                "name": p.name,
                "year_start": p.year_start,
                "year_end": p.year_end,
                "status": p.status,
                "skills_gained": p.skills_gained,
            }
            for p in profile.projects
        ],
        "skill_gaps": profile.skill_gaps,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="TezAtlas Araştırma Kariyer Grafiği Okuyucu")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE,
                        help=f"CAREER_PROFILE.md yolu (varsayılan: {DEFAULT_PROFILE})")
    parser.add_argument("--json", action="store_true",
                        help="JSON formatında çıktı ver")
    parser.add_argument("--gaps", metavar="TARGET",
                        help="Belirli bir hedef rol için beceri eksikliklerini göster")

    args = parser.parse_args()
    profile = parse_career_profile(args.profile)

    if args.json:
        print(json.dumps(to_json(profile), ensure_ascii=False, indent=2))
    else:
        print_summary(profile, target_filter=args.gaps)


if __name__ == "__main__":
    main()
