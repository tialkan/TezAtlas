#!/usr/bin/env python3
"""
install_plugin.py — TezAtlas Plugin Installer

Installs a validated TezAtlas community plugin into the skills/ directory.
Runs validate_plugin.py first; aborts if validation fails.

Usage:
  python3 scripts/install_plugin.py path/to/plugin/
  python3 scripts/install_plugin.py path/to/plugin/ --dry-run
  python3 scripts/install_plugin.py path/to/plugin/ --force
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
COMMUNITY_ROOT = SKILLS_ROOT / "community"


def run_validator(plugin_dir: Path) -> bool:
    """Run validate_plugin.py and return True if validation passes."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_plugin.py"), str(plugin_dir)],
        cwd=str(REPO_ROOT),
    )
    return result.returncode == 0


def load_manifest(plugin_dir: Path) -> dict:
    manifest_path = plugin_dir / "tezatlas-plugin.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def install_plugin(plugin_dir: Path, dry_run: bool = False, force: bool = False) -> bool:
    plugin_dir = plugin_dir.resolve()

    print(f"\nTezAtlas Plugin Installer: {plugin_dir.name}")
    print("══════════════════════════════════════════")

    # 1. Validate first
    print("\n[1/3] Doğrulama çalıştırılıyor…")
    if not run_validator(plugin_dir):
        print("\n✗ Doğrulama başarısız. Kurulum iptal edildi.")
        return False

    manifest = load_manifest(plugin_dir)
    namespace = manifest["namespace"]
    nodes = manifest.get("nodes", [])

    print(f"\n[2/3] Kurulum planı: namespace={namespace}, {len(nodes)} node")

    # Target directory: skills/community/<namespace>/
    target_dir = COMMUNITY_ROOT / namespace

    if target_dir.exists() and not force:
        print(f"\n✗ {target_dir.relative_to(REPO_ROOT)} zaten mevcut.")
        print("   Üzerine yazmak için --force kullanın.")
        return False

    # Show what will be copied
    copy_ops: list[tuple[Path, Path]] = []
    for node_path_str in nodes:
        src = REPO_ROOT / node_path_str
        # Place node in community/<namespace>/<filename>
        dst = target_dir / src.name
        copy_ops.append((src, dst))
        action = "ÜZERINE YAZ" if dst.exists() else "KOPYALA"
        print(f"  {action}: {node_path_str} → community/{namespace}/{src.name}")

    # Copy README if present
    readme_src = plugin_dir / "README.md"
    if readme_src.exists():
        readme_dst = target_dir / "README.md"
        copy_ops.append((readme_src, readme_dst))
        print(f"  KOPYALA: README.md → community/{namespace}/README.md")

    # Copy manifest
    manifest_dst = target_dir / "tezatlas-plugin.json"
    copy_ops.append((plugin_dir / "tezatlas-plugin.json", manifest_dst))

    if dry_run:
        print("\n[DRY RUN] Gerçek dosya kopyalanmadı. --dry-run kaldırılırsa bu işlemler yapılacak.")
        return True

    # 3. Execute
    print("\n[3/3] Kopyalanıyor…")
    target_dir.mkdir(parents=True, exist_ok=True)
    errors = []
    for src, dst in copy_ops:
        try:
            shutil.copy2(src, dst)
            print(f"  ✓ {dst.relative_to(REPO_ROOT)}")
        except OSError as e:
            print(f"  ✗ {dst.name}: {e}")
            errors.append(str(e))

    if errors:
        print(f"\n✗ {len(errors)} hata oluştu. Kurulum tamamlanamadı.")
        return False

    print(f"\n✅ Plugin kuruldu: skills/community/{namespace}/")
    print(f"   {len(nodes)} node + manifest")
    print("\n   Kullanmak için Claude Code'da /tezatlas komutunu çalıştırın.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="TezAtlas Plugin Installer")
    parser.add_argument("plugin_dir", type=Path, help="Plugin dizini")
    parser.add_argument("--dry-run", action="store_true",
                        help="Gerçek kopyalama yapmadan planı göster")
    parser.add_argument("--force", action="store_true",
                        help="Mevcut kurulumun üzerine yaz")

    args = parser.parse_args()

    if not args.plugin_dir.is_dir():
        print(f"Hata: '{args.plugin_dir}' bir dizin değil")
        sys.exit(1)

    success = install_plugin(args.plugin_dir, dry_run=args.dry_run, force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
