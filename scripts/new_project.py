#!/usr/bin/env python3
"""
new_project.py — TezAtlas Template Scaffolding Command

One-command project bootstrap:
  python3 scripts/new_project.py --type article --lang tr --field law --title "My Paper"

Creates:
  STATUS.md, READING_REPORT.md, ARGUMENTS.md,
  sources/.gitkeep, notes/.gitkeep
  Plus discipline-specific extras (e.g., METODOLOJI.md for empirical)

NOTE — Canonical entry point:
  This script creates the directory structure for a new project.
  For the full interactive workflow (phase gates, Iron Rules, guided session),
  always start with `/tezatlas` inside a Claude Code session.
  Use this script only for offline scaffolding or automation.
"""

import argparse
from datetime import date
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────────

DOCUMENT_TYPES = {
    "thesis":            ("Tez", "Thesis"),
    "article":           ("Makale", "Article"),
    "conference":        ("Konferans Bildirisi", "Conference Paper"),
    "lit-review":        ("Literatür Derlemesi", "Literature Review"),
    "report":            ("Araştırma Raporu", "Research Report"),
    "book-chapter":      ("Kitap Bölümü", "Book Chapter"),
    "grant-proposal":    ("Hibe Başvurusu", "Grant Proposal"),
    "research-proposal": ("Araştırma Önerisi", "Research Proposal"),
}

FIELDS = [
    "economics", "law", "education", "psychology", "sociology", "history",
    "engineering", "medicine", "management", "political-science", "linguistics",
    "philosophy", "literature", "computer-science", "environmental-science",
    "other",
]

TODAY = date.today().isoformat()

# ── Template Builders ──────────────────────────────────────────────────────────

def build_status(doc_type: str, lang: str, field: str, title: str) -> str:
    doc_tr, doc_en = DOCUMENT_TYPES.get(doc_type, ("Belge", "Document"))
    lang_label = {"tr": "Türkçe", "en": "English", "both": "Bilingual"}.get(lang, lang)

    return f"""# STATUS.md — TezAtlas Proje Durumu

## Proje Kimliği

```yaml
title: "{title}"
document_type: {doc_type}
field: {field}
language: {lang_label}
created: "{TODAY}"
last_updated: "{TODAY}"
current_phase: 0
```

## Faz İlerlemesi

| Faz | Ad | Durum | Tamamlanma |
|-----|----|-------|------------|
| 0 | Başlangıç / Onboarding | ✅ Tamamlandı | {TODAY} |
| 1 | Araştırma Sorusu | ⏳ Devam ediyor | — |
| 2 | Metodoloji (ampirik ise) | ⏸ Bekliyor | — |
| 3 | Okuma | ⏸ Bekliyor | — |
| 4 | Yapı / Outline | ⏸ Bekliyor | — |
| 5 | Yazım | ⏸ Bekliyor | — |
| 6 | Revizyon | ⏸ Bekliyor | — |
| 7 | Finalizasyon | ⏸ Bekliyor | — |

## Kaynak Havuzu

```yaml
sources:
  total_collected: 0
  read: 0
  active: 0
  deferred: 0
  saturation_reached: false
```

## Yazım Takibi

```yaml
writing_schedule:
  current_streak: 0
  longest_streak: 0
  last_session_date: null
  total_sessions: 0

wellbeing:
  last_session_date: "{TODAY}"
  days_inactive: 0
  goals_missed_consecutive: 0
  last_advisor_checkpoint: null
  attrition_risk: low

motivation:
  why_statement: null
  recorded_at: null
```

## Notlar

<!-- Danışman geri bildirimleri, kararlar, önemli notlar -->
"""


def build_reading_report(title: str) -> str:
    return f"""# READING_REPORT.md — Okuma Raporu

**Proje:** {title}
**Başlangıç:** {TODAY}

## Kaynak Envanteri

| # | Yazar(lar) | Yıl | Başlık | Durum | Alaka | Notlar |
|---|-----------|-----|--------|-------|-------|--------|
| 1 | | | | 🔵 Havuzda | | |

**Durum kodları:** 🔵 Havuzda → 🟡 Okunuyor → 🟢 Tamamlandı → 🔴 Elendi

## Doygunluk Takibi

| Tur | Yeni Kaynak | Önceden Bilinen | Doygunluk % |
|-----|-------------|-----------------|-------------|
| 1 | | | |

**Doygunluk hedefi:** Yeni kaynakların ≥ %80'i önceden bilinen → okuma tamamdır.

## Özet Notlar

<!-- Okuma süreci notları -->
"""


def build_argumanlar(title: str) -> str:
    return f"""# ARGUMENTS.md — Argüman İzleyici

**Proje:** {title}
**Son güncelleme:** {TODAY}

## Aktif İddialar

| # | İddia | Kaynak | Kanıt Gücü | Durum |
|---|-------|--------|-----------|-------|
| 1 | | | ○ | 🔴 BOŞLUK |

**Kanıt gücü:** ●●● Güçlü · ●●○ Orta · ●○○ Zayıf · ○ Kanıt yok

## Çelişkiler

| # | Konu | Kaynak A | Kaynak B | Ele Alış |
|---|------|---------|---------|---------|
| | | | | |

## Şeytan'ın Avukatı — Bekleyen İtirazlar

- [ ] *İtiraz eklemek için `/şeytan-avukatı` komutunu çalıştır*
"""


# ── Directory + File Creator ───────────────────────────────────────────────────

def create_project(
    output_dir: Path,
    doc_type: str,
    lang: str,
    field: str,
    title: str,
    empirical: bool,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Core directories
    for subdir in ["sources", "notes", "cikti"]:
        d = output_dir / subdir
        d.mkdir(exist_ok=True)
        (d / ".gitkeep").touch()

    # Core files
    files = {
        "STATUS.md": build_status(doc_type, lang, field, title),
        "READING_REPORT.md": build_reading_report(title),
        "ARGUMENTS.md": build_argumanlar(title),
    }

    if empirical:
        files["METODOLOJI.md"] = f"""# METODOLOJI.md — Araştırma Metodolojisi

**Proje:** {title}
**Tarih:** {TODAY}

## Araştırma Tasarımı

- Tasarım türü: [...]
- Araştırma sorusu / hipotez: [...]

## Örneklem

- Hedef popülasyon: [...]
- Örnekleme yöntemi: [...]
- n: [...] | Güç analizi: [G*Power — doldur]

## Veri Toplama

- Araç: [...]
- Kaynak: [...]

## Analiz Planı

- Yöntem: [...]
- Yazılım: [...]
- Raporlama: [APA 7]
"""

    # .gitignore snippet
    gitignore_path = output_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# TezAtlas — kişisel veri\nsources/*\n!sources/.gitkeep\n*.pdf\n.env\nnotlar/\n"
        )

    # Write files (skip existing)
    created, skipped = [], []
    for filename, content in files.items():
        fp = output_dir / filename
        if fp.exists():
            skipped.append(filename)
        else:
            fp.write_text(content, encoding="utf-8")
            created.append(filename)

    # Report
    doc_tr, doc_en = DOCUMENT_TYPES.get(doc_type, ("Belge", "Document"))
    print("\n✅ TezAtlas Projesi Oluşturuldu / Project Created")
    print(f"   Tür / Type:  {doc_en} ({doc_tr})")
    print(f"   Alan / Field: {field}")
    print(f"   Dil / Lang:  {lang}")
    print(f"   Dizin / Dir: {output_dir}\n")

    if created:
        print("📄 Oluşturulan dosyalar / Created files:")
        for f in created:
            print(f"   + {f}")

    if skipped:
        print("\n⏭️  Atlandı (zaten mevcut) / Skipped (already exists):")
        for f in skipped:
            print(f"   = {f}")

    print("\n🚀 Başlamak için / To start:")
    print(f"   cd {output_dir}")
    print("   # Claude Code'u aç ve /tezatlas komutunu çalıştır")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TezAtlas — Proje iskele oluşturucu / Project scaffolding tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler / Examples:
  python3 scripts/new_project.py --type article --lang tr --field law --title "Türk Hukukunda AI"
  python3 scripts/new_project.py --type thesis --lang both --field economics --empirical
  python3 scripts/new_project.py --type conference --lang en --field cs --output ~/papers/myconf
        """,
    )
    parser.add_argument(
        "--type", choices=list(DOCUMENT_TYPES.keys()), required=True,
        help="Belge türü / Document type",
    )
    parser.add_argument(
        "--lang", choices=["tr", "en", "both"], default="tr",
        help="Çalışma dili / Working language (default: tr)",
    )
    parser.add_argument(
        "--field", choices=FIELDS, default="other",
        help="Akademik alan / Academic field (default: other)",
    )
    parser.add_argument(
        "--title", default="[Başlık Belirlenmedi]",
        help="Çalışma başlığı / Working title",
    )
    parser.add_argument(
        "--empirical", action="store_true",
        help="Ampirik çalışma — METODOLOJI.md oluştur",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("."),
        help="Çıktı dizini / Output directory (default: current dir)",
    )

    args = parser.parse_args()

    create_project(
        output_dir=args.output,
        doc_type=args.type,
        lang=args.lang,
        field=args.field,
        title=args.title,
        empirical=args.empirical,
    )


if __name__ == "__main__":
    main()
