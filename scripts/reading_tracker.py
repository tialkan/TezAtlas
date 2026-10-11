#!/usr/bin/env python3
"""
scripts/reading_tracker.py — TezAtlas Okuma Takipçisi / Reading Tracker

READING_REPORT.md ile sources/ dizinini senkronize eder.
STATUS.md'deki sources.read ve sources.total_collected değerlerini günceller.

Komutlar:
    python3 scripts/reading_tracker.py sync           # sources/'daki PDF'leri tabloya ekle
    python3 scripts/reading_tracker.py status         # okuma istatistiklerini göster
    python3 scripts/reading_tracker.py mark <n> read  # #n'i okundu olarak işaretle
    python3 scripts/reading_tracker.py mark <n> defer # #n'i ertelenmiş olarak işaretle
    python3 scripts/reading_tracker.py mark <n> pool  # #n'i havuza geri al

Durum kodları:
    🔵 Havuzda    — okunmayı bekliyor
    🟡 Okunuyor   — aktif okumada
    🟢 Tamamlandı — okundu
    🔴 Ertelendi  — ERKEN (erken eleme): şu an kapsam dışı
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from core.session import TezAtlasSession

# ── Durum ikonları ────────────────────────────────────────────────────────────

STATUS_POOL     = "🔵 Havuzda"
STATUS_READING  = "🟡 Okunuyor"
STATUS_DONE     = "🟢 Tamamlandı"
STATUS_DEFERRED = "🔴 Ertelendi"

_STATUS_MAP = {
    "pool":    STATUS_POOL,
    "reading": STATUS_READING,
    "read":    STATUS_DONE,
    "done":    STATUS_DONE,
    "defer":   STATUS_DEFERRED,
    "deferred": STATUS_DEFERRED,
}


# ── READING_REPORT.md parser ──────────────────────────────────────────────────

def _read_report(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _parse_table(content: str) -> tuple[list[str], list[dict], list[str]]:
    """
    READING_REPORT.md'deki kaynak tablosunu parse eder.

    Döndürür:
        (before_lines, rows, after_lines)
        rows: [{"n": int, "author": str, "year": str, "title": str,
                "status": str, "alaka": str, "notlar": str, "raw": str}]
    """
    lines = content.splitlines(keepends=True)
    table_start = None
    table_end = None

    # Tablo başlık satırını bul: "| # |" ile başlıyor
    for i, line in enumerate(lines):
        stripped = line.strip()
        if table_start is None:
            if stripped.startswith("|") and "| # |" in stripped or (
                stripped.startswith("|") and re.search(r"\|\s*#\s*\|", stripped)
            ):
                table_start = i
        elif table_start is not None:
            # Tablo bitişi: boş satır veya ##
            if not stripped.startswith("|") and stripped not in ("", "---"):
                if table_end is None:
                    table_end = i
                    break

    if table_start is None:
        return list(lines), [], []

    if table_end is None:
        table_end = len(lines)

    before = lines[:table_start]
    after = lines[table_end:]
    table_lines = lines[table_start:table_end]

    rows: list[dict] = []
    for line in table_lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "---" in stripped:
            continue
        cols = [c.strip() for c in stripped.strip("|").split("|")]
        if not cols:
            continue
        # Başlık satırı atla
        if cols[0] in ("#", "No", "Nr", "") and any(
            kw in " ".join(cols).lower() for kw in ("yazar", "author", "başlık", "title")
        ):
            continue
        # Sayı sütunu
        try:
            n = int(cols[0])
        except (ValueError, IndexError):
            continue
        rows.append({
            "n": n,
            "author": cols[1] if len(cols) > 1 else "",
            "year": cols[2] if len(cols) > 2 else "",
            "title": cols[3] if len(cols) > 3 else "",
            "status": cols[4] if len(cols) > 4 else STATUS_POOL,
            "alaka": cols[5] if len(cols) > 5 else "",
            "notlar": cols[6] if len(cols) > 6 else "",
            "_raw": line,
        })

    return before, rows, after


def _render_row(row: dict) -> str:
    return (
        f"| {row['n']} | {row['author']} | {row['year']} | {row['title']} "
        f"| {row['status']} | {row['alaka']} | {row['notlar']} |\n"
    )


def _render_table(header_line: str, separator_line: str, rows: list[dict]) -> list[str]:
    """Tabloyu satır listesi olarak yeniden üretir."""
    out = [header_line, separator_line]
    for r in rows:
        out.append(_render_row(r))
    return out


def _write_report(path: Path, before: list[str], rows: list[dict], after: list[str]) -> None:
    """Değiştirilmiş rows ile READING_REPORT.md'i yeniden yazar."""
    header = "| # | Yazar(lar) | Yıl | Başlık | Durum | Alaka | Notlar |\n"
    separator = "|---|-----------|-----|--------|-------|-------|--------|\n"
    table_lines = _render_table(header, separator, rows)
    content = "".join(before) + "".join(table_lines) + "".join(after)
    path.write_text(content, encoding="utf-8")


# ── Komutlar ──────────────────────────────────────────────────────────────────

def cmd_status(project_dir: Path) -> None:
    """Okuma istatistiklerini göster."""
    report_path = project_dir / "READING_REPORT.md"
    content = _read_report(report_path)
    _, rows, _ = _parse_table(content)

    if not rows:
        print("READING_REPORT.md bulunamadı veya kaynak yok.")
        return

    total = len(rows)
    done = sum(1 for r in rows if STATUS_DONE in r["status"])
    reading = sum(1 for r in rows if STATUS_READING in r["status"])
    pool = sum(1 for r in rows if STATUS_POOL in r["status"])
    deferred = sum(1 for r in rows if STATUS_DEFERRED in r["status"])
    pct = round(done / total * 100) if total > 0 else 0

    sat_threshold = 80
    saturation_status = "✅ Doygunluğa ulaşıldı" if pct >= sat_threshold else f"⏳ {sat_threshold - pct}% daha gerekli"

    print("\n📚 Okuma Durumu")
    print(f"  Toplam kaynak  : {total}")
    print(f"  Tamamlandı     : {done} ({pct}%)")
    print(f"  Okunuyor       : {reading}")
    print(f"  Havuzda        : {pool}")
    print(f"  Ertelendi      : {deferred}")
    print(f"  Doygunluk      : {saturation_status}")
    print()

    # Okunmamış kaynaklar listesi
    pending = [r for r in rows if STATUS_DONE not in r["status"] and STATUS_DEFERRED not in r["status"]]
    if pending:
        print(f"  Sıradaki okumalar ({len(pending)} kaynak):")
        for r in pending[:5]:
            icon = "🟡" if STATUS_READING in r["status"] else "🔵"
            print(f"    {icon} #{r['n']:>2}  {r['author'] or '?'} ({r['year'] or '?'}) — {r['title'][:50] or '?'}")
        if len(pending) > 5:
            print(f"    ... ve {len(pending) - 5} kaynak daha")


def cmd_sync(project_dir: Path) -> None:
    """sources/'daki PDF'leri READING_REPORT.md tablosuna ekle."""
    report_path = project_dir / "READING_REPORT.md"
    sources_dir = project_dir / "sources"

    if not sources_dir.is_dir():
        print("sources/ dizini bulunamadı.", file=sys.stderr)
        return

    pdfs = sorted(sources_dir.glob("*.pdf"))
    if not pdfs:
        print("sources/ dizininde PDF bulunamadı.")
        return

    content = _read_report(report_path)
    before, rows, after = _parse_table(content)

    max_n = max((r["n"] for r in rows), default=0)
    added = 0

    for pdf in pdfs:
        stem = pdf.stem
        # Dosya adı zaten tabloda var mı? (notlar sütununda stem arama)
        stem_lower = stem.lower()
        if any(stem_lower in r["notlar"].lower() for r in rows):
            continue
        if any(stem_lower in r["title"].lower() for r in rows):
            continue

        max_n += 1
        rows.append({
            "n": max_n,
            "author": "",
            "year": "",
            "title": stem,
            "status": STATUS_POOL,
            "alaka": "",
            "notlar": pdf.name,
        })
        added += 1
        print(f"  + Eklendi: #{max_n} {stem}")

    if added == 0:
        print("Eklenecek yeni PDF bulunamadı (tüm PDF'ler zaten tabloda).")
    else:
        _write_report(report_path, before, rows, after)
        print(f"\n✅ {added} yeni kaynak READING_REPORT.md'e eklendi.")
        _sync_status_md(project_dir, rows)


def cmd_mark(project_dir: Path, n: int, new_status_key: str) -> None:
    """#n numaralı kaynağın durumunu güncelle."""
    report_path = project_dir / "READING_REPORT.md"
    content = _read_report(report_path)
    before, rows, after = _parse_table(content)

    new_status = _STATUS_MAP.get(new_status_key.lower())
    if not new_status:
        print(f"Geçersiz durum: '{new_status_key}'. Geçerli: pool, reading, read, defer", file=sys.stderr)
        sys.exit(1)

    found = False
    for row in rows:
        if row["n"] == n:
            old = row["status"]
            row["status"] = new_status
            found = True
            print(f"  #{n} güncellendi: {old} → {new_status}")
            break

    if not found:
        print(f"#{n} numaralı kaynak bulunamadı.", file=sys.stderr)
        sys.exit(1)

    _write_report(report_path, before, rows, after)
    _sync_status_md(project_dir, rows)


def _sync_status_md(project_dir: Path, rows: list[dict]) -> None:
    """STATUS.md'deki sources alanını güncel kaynak sayılarıyla senkronize et."""
    status_path = project_dir / "STATUS.md"
    if not status_path.exists():
        return

    total = len(rows)
    done = sum(1 for r in rows if STATUS_DONE in r["status"])
    deferred = sum(1 for r in rows if STATUS_DEFERRED in r["status"])
    pct = done / total if total > 0 else 0.0
    saturation = pct >= 0.80

    sess = TezAtlasSession(project_dir)
    state = sess.load()
    src = state.get("sources") or {}
    src["total_collected"] = total
    src["read"] = done
    src["deferred"] = deferred
    src["saturation_reached"] = saturation
    sess.save({"sources": src})

    sat_label = "✅ Doygunluğa ulaşıldı" if saturation else f"{done}/{total} okundu"
    print(f"📊 STATUS.md güncellendi: {sat_label}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas okuma takipçisi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--project-dir", type=Path, default=Path("."))
    sub = parser.add_subparsers(dest="command", required=True)

    # sync
    sub.add_parser("sync", help="sources/'daki PDF'leri tabloya ekle")

    # status
    sub.add_parser("status", help="Okuma istatistiklerini göster")

    # mark
    mark_p = sub.add_parser("mark", help="Kaynak durumunu güncelle")
    mark_p.add_argument("n", type=int, help="Kaynak numarası (#n)")
    mark_p.add_argument(
        "status",
        choices=list(_STATUS_MAP.keys()),
        help="Yeni durum",
    )

    args = parser.parse_args()
    project_dir = args.project_dir.resolve()

    if args.command == "sync":
        cmd_sync(project_dir)
    elif args.command == "status":
        cmd_status(project_dir)
    elif args.command == "mark":
        cmd_mark(project_dir, args.n, args.status)


if __name__ == "__main__":
    main()
