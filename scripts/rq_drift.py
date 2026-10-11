#!/usr/bin/env python3
"""
scripts/rq_drift.py — TezAtlas Araştırma Sorusu Kayma Dedektörü
                      Research Question Drift Detector

Faz 1'de belirlenen orijinal araştırma sorusunu mevcut durumla karşılaştırır.
Konu kayması erken tespiti için Claude Code'a uyarı sinyalleri üretir.

Kullanım:
    python3 scripts/rq_drift.py                    # otomatik kontrol
    python3 scripts/rq_drift.py --report           # DRIFT_REPORT.md yaz
    python3 scripts/rq_drift.py --lock-rq          # mevcut RQ'yu orijinal olarak kilitle

Kontrol ettiği dosyalar:
    - konu_kesfi.md       → Faz 1 araştırma soruları (orijinal)
    - STATUS.md           → original_rq alanı (kilitli versiyon)
    - ARGUMENTS.md       → mevcut argümanlar (konu yönelimi için)
    - notes/              → son okuma notları (yeni temalar için)
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from core.session import TezAtlasSession


# ── Keyword extraction ────────────────────────────────────────────────────────

_WORD_PATTERN = re.compile(r"\b[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}\b")
_STOP_WORDS = {
    "için", "ile", "bir", "olan", "olarak", "ancak", "fakat", "daha", "gibi",
    "this", "that", "with", "from", "have", "been", "their", "they", "will",
    "more", "also", "such", "these", "those", "into", "other", "which",
    "when", "where", "what", "were", "than", "then", "some", "each",
    "veya", "yahut", "yani", "hem", "ise", "ama", "öyle", "böyle",
    "kadar", "sonra", "önce", "üzere", "göre", "karşı", "arasında",
    "araştırma", "çalışma", "inceleme", "analiz", "study", "research",
    "analysis", "investigation", "examination",
}


def extract_keywords(text: str, top_n: int = 15) -> set[str]:
    from collections import Counter
    words = _WORD_PATTERN.findall(text.lower())
    freq = Counter(w for w in words if w not in _STOP_WORDS and len(w) >= 4)
    return {w for w, _ in freq.most_common(top_n)}


# ── Source parsers ─────────────────────────────────────────────────────────────

def extract_original_rq(project_dir: Path) -> dict:
    """
    Orijinal araştırma sorusunu bul:
    1. STATUS.md'de original_rq varsa → kullan
    2. konu_kesfi.md'den çıkar → Araştırma Soruları bölümü
    3. Bulunamazsa → boş döndür
    """
    # Try STATUS.md first
    sess = TezAtlasSession(project_dir)
    state = sess.load()
    if state.get("original_rq"):
        return {
            "source": "STATUS.md (original_rq)",
            "text": state["original_rq"],
            "keywords": extract_keywords(state["original_rq"]),
        }

    # Try konu_kesfi.md
    konu_path = project_dir / "konu_kesfi.md"
    if konu_path.exists():
        content = konu_path.read_text(encoding="utf-8")
        # Look for "Araştırma Soruları" section
        rq_section = ""
        in_section = False
        for line in content.splitlines():
            if re.match(r"#+\s*(araştırma soru|research question)", line, re.IGNORECASE):
                in_section = True
                continue
            if in_section:
                if line.startswith("#"):
                    break
                rq_section += line + " "
        if rq_section.strip():
            return {
                "source": "konu_kesfi.md",
                "text": rq_section.strip(),
                "keywords": extract_keywords(rq_section),
            }
        # Fallback: use full file content
        return {
            "source": "konu_kesfi.md (tam içerik)",
            "text": content[:500],
            "keywords": extract_keywords(content),
        }

    return {}


def extract_current_focus(project_dir: Path) -> dict:
    """
    Mevcut araştırma odağını tespit et:
    - ARGUMENTS.md argümanlarından
    - Son 5 not dosyasından
    """
    texts = []

    argumanlar_path = project_dir / "ARGUMENTS.md"
    if argumanlar_path.exists():
        texts.append(argumanlar_path.read_text(encoding="utf-8"))

    notes_dir = project_dir / "notes"
    if notes_dir.is_dir():
        note_files = sorted(notes_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        for nf in note_files[:5]:
            texts.append(nf.read_text(encoding="utf-8"))

    full_text = " ".join(texts)
    if not full_text.strip():
        return {}

    return {
        "source": "ARGUMENTS.md + son notlar",
        "text": full_text[:1000],
        "keywords": extract_keywords(full_text),
    }


def compute_drift(original: dict, current: dict) -> dict:
    """
    Orijinal ve mevcut odak arasındaki keyword kaymasını hesaplar.
    """
    if not original or not current:
        return {"drift_score": 0, "status": "unknown", "analysis": {}}

    orig_kw = original["keywords"]
    curr_kw = current["keywords"]

    if not orig_kw:
        return {"drift_score": 0, "status": "unknown", "analysis": {}}

    # Overlap = retained focus
    retained = orig_kw & curr_kw
    lost = orig_kw - curr_kw      # Was in original, not in current
    new_kw = curr_kw - orig_kw    # New themes not in original

    retention_ratio = len(retained) / len(orig_kw) if orig_kw else 1.0
    drift_score = int((1 - retention_ratio) * 100)

    if drift_score < 20:
        status = "stable"
    elif drift_score < 40:
        status = "minor_drift"
    elif drift_score < 60:
        status = "moderate_drift"
    else:
        status = "major_drift"

    return {
        "drift_score": drift_score,
        "retention_ratio": retention_ratio,
        "status": status,
        "retained_keywords": sorted(retained),
        "lost_keywords": sorted(lost),
        "new_keywords": sorted(new_kw),
    }


def lock_rq(project_dir: Path) -> None:
    """konu_kesfi.md'deki RQ'yu STATUS.md'e original_rq olarak kilitle."""
    konu_path = project_dir / "konu_kesfi.md"
    if not konu_path.exists():
        print("❌ konu_kesfi.md bulunamadı.")
        sys.exit(1)
    content = konu_path.read_text(encoding="utf-8")
    # Extract first 300 chars of research questions section
    rq_text = ""
    in_section = False
    for line in content.splitlines():
        if re.match(r"#+\s*(araştırma soru|research question)", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if line.startswith("#"):
                break
            rq_text += line.strip() + " "

    rq_text = rq_text.strip()[:500] or content[:300]

    sess = TezAtlasSession(project_dir)
    state = sess.load()
    if not state:
        print("❌ STATUS.md bulunamadı.")
        sys.exit(1)

    # Update original_rq in STATUS.md
    status_content = (project_dir / "STATUS.md").read_text(encoding="utf-8")
    if "original_rq:" in status_content:
        new_content = re.sub(
            r"original_rq:.*",
            f"original_rq: \"{rq_text[:200]}\"",
            status_content,
        )
    else:
        # Add to first yaml block
        new_content = status_content.replace(
            "```yaml",
            "```yaml\noriginal_rq: |",
            1,
        )
        # More robust: inject before closing ```
        new_content = re.sub(
            r"(```yaml\n)(.*?)(```)",
            lambda m: m.group(1) + m.group(2) + f'original_rq: "{rq_text[:200]}"\n' + m.group(3),
            new_content,
            count=1,
            flags=re.DOTALL,
        )

    (project_dir / "STATUS.md").write_text(new_content, encoding="utf-8")
    print("✅ Orijinal araştırma sorusu STATUS.md'e kilitlendi.")
    print(f"   original_rq: {rq_text[:100]}...")


def write_report(project_dir: Path, original: dict, current: dict, drift: dict) -> Path:
    """DRIFT_REPORT.md dosyasını yazar."""
    output_path = project_dir / "DRIFT_REPORT.md"

    status_labels = {
        "stable": "🟢 Stabil — konu odağı korunuyor",
        "minor_drift": "🟡 Küçük kayma — dikkat et",
        "moderate_drift": "🟠 Orta kayma — danışmanla kontrol et",
        "major_drift": "🔴 Büyük kayma — araştırma sorusunu gözden geçir",
        "unknown": "⚪ Bilinmiyor — konu_kesfi.md veya ARGUMENTS.md eksik",
    }

    status = drift.get("status", "unknown")
    status_label = status_labels.get(status, status)
    drift_score = drift.get("drift_score", 0)

    lines = [
        "# Araştırma Sorusu Kayma Raporu / RQ Drift Report",
        "",
        f"_Oluşturulma: {date.today().isoformat()}_",
        "",
        f"## Durum: {status_label}",
        "",
        f"**Kayma skoru:** {drift_score}/100  (0 = sıfır kayma, 100 = tamamen farklı konu)",
        "",
    ]

    if original:
        lines += [
            "## Orijinal Araştırma Sorusu",
            f"_Kaynak: {original['source']}_",
            "",
            f"> {original['text'][:400]}",
            "",
            f"**Orijinal anahtar kelimeler:** {', '.join(sorted(original['keywords'])[:10])}",
            "",
        ]

    if current:
        lines += [
            "## Mevcut Araştırma Odağı",
            f"_Kaynak: {current['source']}_",
            "",
            f"**Mevcut anahtar kelimeler:** {', '.join(sorted(current['keywords'])[:10])}",
            "",
        ]

    if drift.get("status") not in ("unknown", None):
        lines += [
            "## Analiz",
            "",
            "| Kategori | Anahtar Kelimeler |",
            "|----------|-------------------|",
            f"| ✅ Korunan odak | {', '.join(drift.get('retained_keywords', [])[:8]) or '—'} |",
            f"| ⚠️  Kaybolan odak | {', '.join(drift.get('lost_keywords', [])[:8]) or '—'} |",
            f"| 🆕 Yeni temalar | {', '.join(drift.get('new_keywords', [])[:8]) or '—'} |",
            "",
        ]

        if status in ("moderate_drift", "major_drift"):
            lines += [
                "## ⚠️ Önerilen Eylemler",
                "",
                "1. **Danışmanınla konuş:** Konu kaymasını ve bunun kasıtlı mı olduğunu tartış",
                "2. **Araştırma sorusunu gözden geçir:** ARGUMENTS.md'deki argümanlar hâlâ orijinal soruyu yanıtlıyor mu?",
                "3. **Kaybolan odağı değerlendir:** Gerçekten kapsam dışında mı, yoksa hâlâ ilgili mi?",
                "4. **Orijinal RQ'yu güncelle:** Kasıtlı bir evrim varsa STATUS.md'i güncelle:",
                "   ```",
                "   python3 scripts/rq_drift.py --lock-rq",
                "   ```",
                "",
            ]
        elif status == "minor_drift":
            lines += [
                "## 💡 Not",
                "",
                "Küçük bir kayma normal — okuma sürecinde konu incelir ve netleşir.",
                "Yeni temalara dikkat et ve bunların orijinal araştırma sorusuyla bağlantısını kur.",
                "",
            ]
        else:
            lines += [
                "## ✅ Değerlendirme",
                "",
                "Araştırma odağın orijinal soruyla uyumlu görünüyor. İyi iş!",
                "",
            ]

    lines += [
        "---",
        "",
        "## Güncelleme",
        "",
        "Okuma/yazım fazlarında düzenli olarak çalıştır:",
        "```",
        "python3 scripts/rq_drift.py --report",
        "```",
        "",
        "Kasıtlı konu değişimi varsa orijinal RQ'yu güncelle:",
        "```",
        "python3 scripts/rq_drift.py --lock-rq",
        "```",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Araştırma Sorusu Kayma Dedektörü"
    )
    parser.add_argument(
        "--report", action="store_true",
        help="DRIFT_REPORT.md dosyasını oluştur/güncelle",
    )
    parser.add_argument(
        "--lock-rq", action="store_true",
        help="konu_kesfi.md'deki RQ'yu STATUS.md'e orijinal olarak kilitle",
    )
    parser.add_argument(
        "--project-dir", metavar="DIR", default=".",
        help="Proje kök dizini",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    if args.lock_rq:
        lock_rq(project_dir)
        return

    original = extract_original_rq(project_dir)
    current = extract_current_focus(project_dir)
    drift = compute_drift(original, current)

    status = drift.get("status", "unknown")
    score = drift.get("drift_score", 0)

    status_icons = {
        "stable": "🟢",
        "minor_drift": "🟡",
        "moderate_drift": "🟠",
        "major_drift": "🔴",
        "unknown": "⚪",
    }

    print()
    print(f"{'─' * 50}")
    print("  Araştırma Sorusu Kayma Analizi")
    print(f"{'─' * 50}")
    print(f"  Durum   : {status_icons.get(status, '?')} {status.replace('_', ' ').title()}")
    print(f"  Skor    : {score}/100")

    if original:
        print(f"  Orijinal: {original.get('source', '?')}")

    if drift.get("retained_keywords"):
        print(f"  Korunan : {', '.join(drift['retained_keywords'][:5])}")
    if drift.get("lost_keywords"):
        print(f"  Kaybolan: {', '.join(drift['lost_keywords'][:5])}")
    if drift.get("new_keywords"):
        print(f"  Yeni    : {', '.join(drift['new_keywords'][:5])}")

    print(f"{'─' * 50}")
    print()

    if not original:
        print("ℹ️  Orijinal araştırma sorusu bulunamadı.")
        print("   konu_kesfi.md yoksa önce Faz 1'i tamamla.")
        print("   Ya da RQ'yu kilitle: python3 scripts/rq_drift.py --lock-rq")
    elif status in ("moderate_drift", "major_drift"):
        print(f"⚠️  Konu kayması tespit edildi (skor: {score}/100).")
        print("   Danışmanınla konuş ve ARGUMENTS.md'i gözden geçir.")
        print("   Detaylı rapor için: python3 scripts/rq_drift.py --report")
    elif status == "minor_drift":
        print(f"💡 Küçük kayma var (skor: {score}/100) — normal okuma süreci.")
        print("   Detaylı rapor için: python3 scripts/rq_drift.py --report")
    else:
        print("✅ Araştırma odağı stabil.")

    if args.report:
        out = write_report(project_dir, original, current, drift)
        print(f"\n📄 Rapor yazıldı: {out.name}")


if __name__ == "__main__":
    main()
