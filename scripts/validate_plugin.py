#!/usr/bin/env python3
"""
validate_plugin.py — TezAtlas Plugin Validator

Validates a TezAtlas community plugin package:
  - tezatlas-plugin.json manifest schema
  - All declared node files exist
  - Frontmatter schema valid (reuses check_frontmatter logic)
  - links_to references resolve
  - Namespace conflicts with core nodes

Usage:
  python3 scripts/validate_plugin.py path/to/plugin/
  python3 scripts/validate_plugin.py path/to/plugin/ --strict
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
CORE_NAMESPACES = {"core", "phases", "techniques", "templates", "tooling",
                   "disciplines", "moc", "community"}

# ── Manifest Validation ────────────────────────────────────────────────────────

MANIFEST_REQUIRED = ["name", "version", "description", "author", "license",
                     "tezatlas_version", "namespace", "nodes"]

def validate_manifest(plugin_dir: Path) -> tuple[dict, list[str], list[str]]:
    """Returns (manifest, errors, warnings)."""
    errors, warnings = [], []
    manifest_path = plugin_dir / "tezatlas-plugin.json"

    if not manifest_path.exists():
        errors.append("tezatlas-plugin.json bulunamadı")
        return {}, errors, warnings

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"tezatlas-plugin.json geçersiz JSON: {e}")
        return {}, errors, warnings

    for field in MANIFEST_REQUIRED:
        if field not in manifest:
            errors.append(f"Manifest: eksik alan '{field}'")

    # Check namespace not conflicting with core
    ns = manifest.get("namespace", "")
    if ns in {"core", "phases", "techniques", "templates", "tooling", "disciplines", "moc"}:
        errors.append(f"Namespace '{ns}' rezerve edilmiş — farklı bir isim seç")

    # Check license
    lic = manifest.get("license", "")
    if lic not in ("CC-BY-4.0", "CC-BY-SA-4.0", "MIT", "Apache-2.0"):
        warnings.append(f"Lisans '{lic}' — CC BY 4.0 önerilir")

    return manifest, errors, warnings


# ── Node File Validation ───────────────────────────────────────────────────────

VALID_NODE_TYPES = {"core", "phase", "phase-fork", "technique", "template",
                    "tooling", "foundation", "moc"}

def validate_frontmatter(filepath: Path) -> list[str]:
    """Returns list of errors for a single node file."""
    errors = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError as e:
        return [f"{filepath}: okunamadı — {e}"]

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return [f"{filepath}: frontmatter eksik veya geçersiz"]

    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        return [f"{filepath}: frontmatter YAML hatası — {e}"]

    for req in ["title", "node_type", "description", "tags", "language"]:
        if req not in fm or fm[req] is None:
            errors.append(f"{filepath.name}: eksik alan '{req}'")

    node_type = fm.get("node_type", "")
    if node_type and node_type not in VALID_NODE_TYPES:
        errors.append(f"{filepath.name}: bilinmeyen node_type '{node_type}'")

    return errors


def validate_links_to(filepath: Path) -> list[str]:
    """Check links_to paths exist relative to repo root."""
    warnings = []
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return []
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return []

    links = fm.get("links_to", []) or []
    for link in links:
        target = REPO_ROOT / link
        if not target.exists():
            warnings.append(f"{filepath.name}: links_to '{link}' → dosya mevcut değil")
    return warnings


# ── Core Node Conflict Check ──────────────────────────────────────────────────

def check_namespace_conflict(plugin_dir: Path, namespace: str) -> list[str]:
    """Warn if any plugin file would shadow a core file."""
    conflicts = []
    for plugin_file in plugin_dir.rglob("*.md"):
        # Check if same filename exists in core skills
        for core_file in SKILLS_ROOT.rglob(plugin_file.name):
            if "community" not in str(core_file):
                conflicts.append(
                    f"İsim çakışması: '{plugin_file.name}' → çekirdek '{core_file.relative_to(REPO_ROOT)}' ile çakışıyor"
                )
    return conflicts


# ── Main Validator ────────────────────────────────────────────────────────────

def validate_plugin(plugin_dir: Path, strict: bool = False) -> bool:
    plugin_dir = plugin_dir.resolve()
    all_errors, all_warnings = [], []

    print(f"\nTezAtlas Plugin Doğrulayıcı: {plugin_dir.name}")
    print("══════════════════════════════════════════")

    # 1. Manifest
    manifest, errors, warnings = validate_manifest(plugin_dir)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    if not manifest:
        _print_results(all_errors, all_warnings)
        return False

    namespace = manifest.get("namespace", "unknown")
    nodes = manifest.get("nodes", [])

    print(f"Paket:     {manifest.get('name', '?')} v{manifest.get('version', '?')}")
    print(f"Namespace: {namespace}")
    print(f"Node'lar:  {len(nodes)}")
    print()

    # 2. Node files
    found, missing = 0, 0
    for node_path_str in nodes:
        node_path = REPO_ROOT / node_path_str
        if not node_path.exists():
            all_errors.append(f"Node bulunamadı: {node_path_str}")
            missing += 1
        else:
            found += 1
            fm_errors = validate_frontmatter(node_path)
            all_errors.extend(fm_errors)
            link_warnings = validate_links_to(node_path)
            all_warnings.extend(link_warnings)

    print(f"✅ Node dosyaları: {found}/{len(nodes)} bulundu")

    # 3. Namespace conflicts
    conflicts = check_namespace_conflict(plugin_dir, namespace)
    all_warnings.extend(conflicts)

    # 4. README check
    if not (plugin_dir / "README.md").exists():
        all_warnings.append("README.md eksik — kurulum rehberi önerilir")

    # 5. LICENSE check
    if not any((plugin_dir / f).exists() for f in ["LICENSE", "LICENSE.md", "LICENCE"]):
        all_warnings.append("LICENSE dosyası eksik")

    _print_results(all_errors, all_warnings)

    if strict:
        return len(all_errors) == 0 and len(all_warnings) == 0
    return len(all_errors) == 0


def _print_results(errors: list[str], warnings: list[str]) -> None:
    if errors:
        print(f"\n❌ Hatalar ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print(f"\n⚠️  Uyarılar ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")
    if not errors and not warnings:
        print("\n✅ Tüm doğrulamalar geçti — plugin kuruluma hazır!")
    elif not errors:
        print(f"\n✅ Hata yok ({len(warnings)} uyarı) — kuruluma hazır (uyarıları gözden geçirin)")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas Plugin Doğrulayıcı",
    )
    parser.add_argument("plugin_dir", type=Path, help="Plugin dizini")
    parser.add_argument("--strict", action="store_true",
                        help="Uyarılar da başarısızlık sayılır")

    args = parser.parse_args()

    if not args.plugin_dir.is_dir():
        print(f"Hata: '{args.plugin_dir}' bir dizin değil")
        sys.exit(1)

    success = validate_plugin(args.plugin_dir, strict=args.strict)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
