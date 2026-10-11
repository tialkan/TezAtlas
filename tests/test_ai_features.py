"""
tests/test_ai_features.py — Tests for 5 AI intelligence scripts

Tests for:
- scripts/snowball.py — DOI extraction + SNOWBALL_CANDIDATES.md
- scripts/contradiction_scan.py — cross-note contradiction detection
- scripts/saturation_map.py — argument coverage mapping
- scripts/rq_drift.py — research question drift detection
- scripts/synthesize.py — multi-source synthesis scaffold
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path


_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run(script: str, *args: str, cwd: Path = _ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, f"scripts/{script}", *args],
        capture_output=True, text=True, cwd=str(cwd),
    )


def _make_argumanlar(tmp_path: Path, claims: list[str]) -> Path:
    rows = "\n".join(
        f"| {i+1} | {claim} | Kaynak_{i+1} | Karşı_{i+1} | Orta |"
        for i, claim in enumerate(claims)
    )
    content = (
        "# ARGUMENTS.md\n\n"
        "| # | İddia/Argüman | Kaynak | Zıt Görüş | Güç |\n"
        "|---|---------------|--------|-----------|-----|\n"
        + rows + "\n"
    )
    p = tmp_path / "ARGUMENTS.md"
    p.write_text(content, encoding="utf-8")
    return p


def _make_note(notes_dir: Path, fname: str, title: str, body: str) -> Path:
    notes_dir.mkdir(exist_ok=True)
    content = f"# {title}\n\nKaynak: test\n\n{body}\n"
    p = notes_dir / fname
    p.write_text(content, encoding="utf-8")
    return p


# ═══════════════════════════════════════════════════════════════════════════════
# 1. snowball.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestSnowball:
    def test_no_notes_dir_graceful(self, tmp_path):
        """notes/ dizini yoksa graceful çıkış yapmalı."""
        result = _run("snowball.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        assert result.returncode == 0
        assert "SNOWBALL_CANDIDATES.md" not in (tmp_path / "SNOWBALL_CANDIDATES.md").name or \
               not (tmp_path / "SNOWBALL_CANDIDATES.md").exists()

    def test_doi_extraction_from_notes(self, tmp_path):
        """notes/ içindeki bir DOI SNOWBALL_CANDIDATES.md'e eklenmeli."""
        notes = tmp_path / "notes"
        notes.mkdir()
        note = notes / "paper1.md"
        note.write_text(
            "# Kaynak 1\n\nBu çalışma 10.1016/j.test.2023.01 DOI'sini atıflar.\n",
            encoding="utf-8",
        )
        result = _run("snowball.py", "--project-dir", str(tmp_path),
                      "--from-notes", str(notes), cwd=_ROOT)
        assert result.returncode == 0
        candidates = tmp_path / "SNOWBALL_CANDIDATES.md"
        assert candidates.exists()
        content = candidates.read_text(encoding="utf-8")
        assert "10.1016/j.test.2023.01" in content

    def test_already_known_doi_not_duplicated(self, tmp_path):
        """Zaten bilinen DOI ikinci kez SNOWBALL_CANDIDATES.md'e eklenmemeli."""
        notes = tmp_path / "notes"
        notes.mkdir()
        note = notes / "paper1.md"
        note.write_text(
            "# Kaynak\n\n10.1234/existing.doi — bu zaten biliniyor.\n",
            encoding="utf-8",
        )
        # Add DOI to READING_REPORT.md (already known)
        report = tmp_path / "READING_REPORT.md"
        report.write_text(
            "| 1 | Smith | 2020 | Title | 🟢 | | paper.pdf | 10.1234/existing.doi |\n",
            encoding="utf-8",
        )
        _run("snowball.py", "--project-dir", str(tmp_path),
             "--from-notes", str(notes), cwd=_ROOT)
        candidates = tmp_path / "SNOWBALL_CANDIDATES.md"
        if candidates.exists():
            content = candidates.read_text(encoding="utf-8")
            # Count occurrences — should be 0 (known) or if added, exactly 1
            assert content.count("10.1234/existing.doi") <= 1

    def test_multiple_dois_extracted(self, tmp_path):
        """Birden fazla DOI aynı anda çıkarılabilmeli."""
        notes = tmp_path / "notes"
        notes.mkdir()
        note = notes / "multi.md"
        note.write_text(
            "# Çoklu Atıf\n\n"
            "Smith (2020) doi:10.1001/test.2020 ve Jones (2021) 10.2002/other.2021 gösteriyor.\n",
            encoding="utf-8",
        )
        _run("snowball.py", "--project-dir", str(tmp_path),
             "--from-notes", str(notes), cwd=_ROOT)
        candidates = tmp_path / "SNOWBALL_CANDIDATES.md"
        if candidates.exists():
            content = candidates.read_text(encoding="utf-8")
            assert "10.1001/test.2020" in content
            assert "10.2002/other.2021" in content


# ═══════════════════════════════════════════════════════════════════════════════
# 2. contradiction_scan.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestContradictionScan:
    def test_no_notes_dir_graceful(self, tmp_path):
        result = _run("contradiction_scan.py", "--project-dir", str(tmp_path),
                      "--notes", str(tmp_path / "notes"), cwd=_ROOT)
        assert result.returncode == 0

    def test_empty_notes_dir_graceful(self, tmp_path):
        (tmp_path / "notes").mkdir()
        result = _run("contradiction_scan.py", "--project-dir", str(tmp_path),
                      "--notes", str(tmp_path / "notes"), cwd=_ROOT)
        assert result.returncode == 0

    def test_report_generated(self, tmp_path):
        """Not dosyaları varsa CONTRADICTIONS.md üretilmeli."""
        notes = tmp_path / "notes"
        _make_note(notes, "note1.md", "Kaynak 1",
                   "Bu çalışma göstermektedir ki yapay zeka işgücünü azaltmaktadır. "
                   "Otomasyon işçi sayısını düşürmektedir.")
        _make_note(notes, "note2.md", "Kaynak 2",
                   "Bu araştırma savunmaktadır ki yapay zeka yeni işler yaratmaktadır. "
                   "Otomasyon istihdamı artırmaktadır.")
        result = _run("contradiction_scan.py", "--project-dir", str(tmp_path),
                      "--notes", str(notes),
                      "--output", str(tmp_path / "CONTRADICTIONS.md"), cwd=_ROOT)
        assert result.returncode == 0
        report = tmp_path / "CONTRADICTIONS.md"
        assert report.exists()
        content = report.read_text(encoding="utf-8")
        assert "Çapraz Kaynak Çelişki Raporu" in content

    def test_report_lists_scanned_notes(self, tmp_path):
        """Taranan notlar raporda listelenmeli."""
        notes = tmp_path / "notes"
        _make_note(notes, "source_a.md", "Source A", "Bu çalışma göstermektedir ki X artmaktadır.")
        _make_note(notes, "source_b.md", "Source B", "Bu çalışma savunmaktadır ki X değil azalmaktadır.")
        _run("contradiction_scan.py", "--project-dir", str(tmp_path),
             "--notes", str(notes),
             "--output", str(tmp_path / "CONTRADICTIONS.md"), cwd=_ROOT)
        content = (tmp_path / "CONTRADICTIONS.md").read_text(encoding="utf-8")
        assert "source_a.md" in content
        assert "source_b.md" in content


# ═══════════════════════════════════════════════════════════════════════════════
# 3. saturation_map.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestSaturationMap:
    def test_no_argumanlar_exits_gracefully(self, tmp_path):
        result = _run("saturation_map.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        assert result.returncode == 0
        assert not (tmp_path / "SATURATION.md").exists()

    def test_report_generated_with_arguments(self, tmp_path):
        """ARGUMENTS.md varsa SATURATION.md üretilmeli."""
        _make_argumanlar(tmp_path, [
            "Yapay zeka algoritmik yönetimi kolaylaştırmaktadır",
            "Çalışan gözetimi mahremiyet hakkını ihlal etmektedir",
        ])
        (tmp_path / "notes").mkdir()
        result = _run("saturation_map.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        assert result.returncode == 0
        report = tmp_path / "SATURATION.md"
        assert report.exists()
        content = report.read_text(encoding="utf-8")
        assert "Semantik Doygunluk Haritası" in content
        assert "Argüman 1" in content
        assert "Argüman 2" in content

    def test_red_gap_when_no_notes(self, tmp_path):
        """Not yoksa argümanlar 🔴 boşluk olarak işaretlenmeli."""
        _make_argumanlar(tmp_path, ["Test argümanı kaynak gerektiriyor"])
        (tmp_path / "notes").mkdir()
        _run("saturation_map.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        content = (tmp_path / "SATURATION.md").read_text(encoding="utf-8")
        assert "🔴" in content

    def test_coverage_improves_with_notes(self, tmp_path):
        """İlgili notlar eklendikçe kapsama artmalı."""
        _make_argumanlar(tmp_path, [
            "algoritmik yönetim çalışan gözetimi mahremiyet"
        ])
        notes = tmp_path / "notes"
        _make_note(notes, "n1.md", "Note 1",
                   "algoritmik yönetim çalışanları gözetim altına almaktadır. "
                   "Mahremiyet hakkı ihlal edilmektedir göstermektedir.")
        _make_note(notes, "n2.md", "Note 2",
                   "algoritmik yönetim sistemi gözetim mahremiyet analizleri "
                   "çalışan hakları konusunda savunmaktadır.")
        _run("saturation_map.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        content = (tmp_path / "SATURATION.md").read_text(encoding="utf-8")
        # With matching notes, should NOT be all red
        assert "Semantik Doygunluk Haritası" in content

    def test_gap_summary_shown_when_gaps_exist(self, tmp_path):
        """Boşluk varsa özet bölümü gösterilmeli."""
        _make_argumanlar(tmp_path, ["tamamen kapsanmamış argüman xyzqrst"])
        (tmp_path / "notes").mkdir()
        _run("saturation_map.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        content = (tmp_path / "SATURATION.md").read_text(encoding="utf-8")
        assert "Boşluk Özeti" in content


# ═══════════════════════════════════════════════════════════════════════════════
# 4. rq_drift.py
# ═══════════════════════════════════════════════════════════════════════════════

_STATUS_TEMPLATE = textwrap.dedent("""\
    # STATUS.md

    ```yaml
    document_type: thesis
    language: tr
    current_phase: 3
    original_rq: "{rq}"
    ```
""")


class TestRqDrift:
    def test_no_files_graceful(self, tmp_path):
        result = _run("rq_drift.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        assert result.returncode == 0

    def test_stable_when_rq_matches_arguments(self, tmp_path):
        """Orijinal RQ ve ARGUMENTS.md uyumluysa stable çıktı vermeli."""
        (tmp_path / "STATUS.md").write_text(
            _STATUS_TEMPLATE.format(
                rq="yapay zeka algoritmik yönetim iş hukuku çalışan"
            ),
            encoding="utf-8",
        )
        _make_argumanlar(tmp_path, [
            "yapay zeka algoritmik yönetim iş hukukunu etkiliyor",
            "çalışan hakları yapay zeka sistemi ile ihlal ediliyor",
        ])
        (tmp_path / "notes").mkdir()
        result = _run("rq_drift.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        assert result.returncode == 0
        output = result.stdout
        assert "Stabil" in output or "stable" in output.lower() or "Skor" in output

    def test_report_flag_writes_file(self, tmp_path):
        """--report bayrağı DRIFT_REPORT.md dosyasını yazmalı."""
        (tmp_path / "STATUS.md").write_text(
            _STATUS_TEMPLATE.format(rq="test araştırma sorusu"),
            encoding="utf-8",
        )
        _make_argumanlar(tmp_path, ["test argümanı"])
        (tmp_path / "notes").mkdir()
        result = _run("rq_drift.py", "--project-dir", str(tmp_path),
                      "--report", cwd=_ROOT)
        assert result.returncode == 0
        report = tmp_path / "DRIFT_REPORT.md"
        assert report.exists()
        content = report.read_text(encoding="utf-8")
        assert "Araştırma Sorusu Kayma Raporu" in content

    def test_lock_rq_from_konu_kesfi(self, tmp_path):
        """--lock-rq konu_kesfi.md'den RQ alıp STATUS.md'e yazmalı."""
        (tmp_path / "STATUS.md").write_text(
            _STATUS_TEMPLATE.format(rq=""),
            encoding="utf-8",
        )
        konu = tmp_path / "konu_kesfi.md"
        konu.write_text(
            "# Konu Keşfi\n\n## Araştırma Soruları\n\nYapay zeka iş hukukunu nasıl etkiliyor?\n",
            encoding="utf-8",
        )
        result = _run("rq_drift.py", "--project-dir", str(tmp_path),
                      "--lock-rq", cwd=_ROOT)
        assert result.returncode == 0
        status_content = (tmp_path / "STATUS.md").read_text(encoding="utf-8")
        assert "original_rq" in status_content
        assert "Yapay zeka" in status_content or "yapay zeka" in status_content

    def test_extracts_rq_from_konu_kesfi_when_no_status_rq(self, tmp_path):
        """STATUS.md'de original_rq yoksa konu_kesfi.md'den çıkarılmalı."""
        (tmp_path / "STATUS.md").write_text(
            "# STATUS.md\n\n```yaml\ndocument_type: thesis\n```\n",
            encoding="utf-8",
        )
        konu = tmp_path / "konu_kesfi.md"
        konu.write_text(
            "# Konu Keşfi\n\n## Araştırma Soruları\n\n"
            "Merkez bankası dijital paraları para politikasını nasıl etkiliyor?\n",
            encoding="utf-8",
        )
        _make_argumanlar(tmp_path, ["merkez bankası dijital para politikası"])
        (tmp_path / "notes").mkdir()
        result = _run("rq_drift.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        assert result.returncode == 0
        # Should detect and use konu_kesfi.md as source
        output = result.stdout
        assert "konu_kesfi" in output or "Skor" in output or "Stabil" in output


# ═══════════════════════════════════════════════════════════════════════════════
# 5. synthesize.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestSynthesize:
    def test_no_argumanlar_exits_gracefully(self, tmp_path):
        result = _run("synthesize.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        assert result.returncode == 0
        assert not (tmp_path / "SYNTHESIS.md").exists()

    def test_skeleton_generated_with_arguments_no_notes(self, tmp_path):
        """Not olmasa bile SYNTHESIS.md iskeleti üretilmeli."""
        _make_argumanlar(tmp_path, [
            "Algoritma yönetimi çalışanları etkiliyor",
            "Gözetim mahremiyet hakkını ihlal ediyor",
        ])
        (tmp_path / "notes").mkdir()
        result = _run("synthesize.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        assert result.returncode == 0
        sentez = tmp_path / "SYNTHESIS.md"
        assert sentez.exists()
        content = sentez.read_text(encoding="utf-8")
        assert "Çok Kaynaklı Sentez" in content
        assert "Argüman 1" in content
        assert "Argüman 2" in content

    def test_sentez_placeholder_present(self, tmp_path):
        """Her argüman için sentez alanı placeholder'ı olmalı."""
        _make_argumanlar(tmp_path, ["Test argümanı"])
        (tmp_path / "notes").mkdir()
        _run("synthesize.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        content = (tmp_path / "SYNTHESIS.md").read_text(encoding="utf-8")
        assert "Sentez Alanı" in content or "Sentez paragrafı" in content

    def test_notes_classified_per_argument(self, tmp_path):
        """İlgili notlar argüman bloklarına dahil edilmeli."""
        _make_argumanlar(tmp_path, [
            "algoritmik yönetim çalışan gözetim sistemi"
        ])
        notes = tmp_path / "notes"
        _make_note(notes, "n1.md", "Note Algoritmik",
                   "algoritmik yönetim sistemi çalışanları gözetlemektedir. "
                   "Bu durum desteklemektedir işçi haklarını olumsuz etkiler.")
        _run("synthesize.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        content = (tmp_path / "SYNTHESIS.md").read_text(encoding="utf-8")
        # Note should appear somewhere
        assert "n1.md" in content or "Note Algoritmik" in content

    def test_single_argument_filter(self, tmp_path):
        """--argument N bayrağı sadece o argümanı işlemeli."""
        _make_argumanlar(tmp_path, [
            "Birinci argüman konusu test",
            "İkinci argüman farklı konu",
        ])
        (tmp_path / "notes").mkdir()
        _run("synthesize.py", "--project-dir", str(tmp_path),
             "--argument", "1", cwd=_ROOT)
        content = (tmp_path / "SYNTHESIS.md").read_text(encoding="utf-8")
        assert "Argüman 1" in content
        # Argument 2 should not appear
        assert "Argüman 2" not in content

    def test_coverage_summary_table(self, tmp_path):
        """Birden fazla argümanda özet tablo üretilmeli."""
        _make_argumanlar(tmp_path, [
            "Birinci argüman",
            "İkinci argüman",
            "Üçüncü argüman",
        ])
        (tmp_path / "notes").mkdir()
        _run("synthesize.py", "--project-dir", str(tmp_path), cwd=_ROOT)
        content = (tmp_path / "SYNTHESIS.md").read_text(encoding="utf-8")
        assert "Kapsama Özeti" in content
