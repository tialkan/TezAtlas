"""
core/phase_gate.py — TezAtlas Faz Kapısı Doğrulayıcı / Phase Gate Validator

Her belge türü ve faz geçişi için koşul setlerini tanımlar.
Koşullar dosya sistemi + STATUS.md state'ine dayanır.

Kullanım:
    from core.phase_gate import PhaseGate
    gate = PhaseGate(Path("."), "thesis")
    result = gate.check(from_phase=2, to_phase=3)
    # {"passed": bool, "passed_checks": [...], "failed_checks": [...], "message": str}
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass
class GateCheck:
    """Tek bir faz kapısı koşulu."""

    label: str
    check: Callable[[Path, dict[str, Any]], bool]
    failure_hint: str  # Kullanıcıya ne yapması gerektiğini anlat


# ── Koşul fonksiyonları ──────────────────────────────────────────────────────

def _status_exists(project_dir: Path, state: dict) -> bool:
    return (project_dir / "STATUS.md").exists()


def _sources_dir_exists(project_dir: Path, state: dict) -> bool:
    return (project_dir / "sources").is_dir()


def _has_at_least_n_pdfs(n: int) -> Callable:
    def _check(project_dir: Path, state: dict) -> bool:
        src_dir = project_dir / "sources"
        if not src_dir.is_dir():
            return False
        return len(list(src_dir.glob("*.pdf"))) >= n
    return _check


def _argumanlar_has_n_entries(n: int) -> Callable:
    def _check(project_dir: Path, state: dict) -> bool:
        path = project_dir / "ARGUMENTS.md"
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        rows = [
            line for line in content.splitlines()
            if line.strip().startswith("|")
            and "---" not in line
            and "İddia" not in line
            and "Claim" not in line
        ]
        data_rows = [
            r for r in rows
            if len([c.strip() for c in r.strip("|").split("|") if c.strip()]) >= 2
        ]
        return len(data_rows) >= n
    return _check


def _saturation_reached(project_dir: Path, state: dict) -> bool:
    """Okuma doygunluğu: ya saturation_reached=true ya da read >= %80."""
    src = state.get("sources") or {}
    if src.get("saturation_reached") is True:
        return True
    total = int(src.get("total_collected", 0))
    read = int(src.get("read", 0))
    if total > 0 and read / total >= 0.80:
        return True
    return False


def _savunma_zirhi_exists(project_dir: Path, state: dict) -> bool:
    return (project_dir / "SAVUNMA_ZIRHI.md").exists()


def _advisor_checkpoint_confirmed(project_dir: Path, state: dict) -> bool:
    """STATUS.md gates alanında advisor checkpoint onayı var mı?"""
    gates = state.get("gates") or {}
    # Herhangi bir advisor_checkpoint anahtarı arar
    for key, val in gates.items():
        if "advisor" in key.lower() or "danisман" in key.lower():
            if isinstance(val, dict) and val.get("confirmed"):
                return True
    return False


def _reading_report_has_sources(project_dir: Path, state: dict) -> bool:
    path = project_dir / "READING_REPORT.md"
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8")
    # En az bir kayıtlı kaynak satırı olsun
    rows = [
        line for line in content.splitlines()
        if line.strip().startswith("|") and "---" not in line and "Yazar" not in line
    ]
    return len(rows) >= 1


def _gate_key_confirmed(gate_key: str) -> Callable:
    """STATUS.md gates dict'inde belirli bir anahtarın onaylı olup olmadığını kontrol eder."""
    def _check(project_dir: Path, state: dict) -> bool:
        gates = state.get("gates") or {}
        entry = gates.get(gate_key)
        if isinstance(entry, dict):
            return entry.get("confirmed", False) or entry.get("passed", False)
        return False
    return _check


def _deferred_pool_cleared(project_dir: Path, state: dict) -> bool:
    """
    Iron Rule 9: Ertelenmiş (ERKEN) kaynak havuzu yazım fazına girmeden gözden geçirilmiş olmalı.

    Kontrol mantığı:
    - READING_REPORT.md'de 🔴 Ertelendi satırı yoksa → ✅ (ertelenen kaynak yok)
    - Varsa: STATUS.md'de gates.deferred_pool_reviewed=true ise → ✅
    - Varsa ve onay yoksa → ❌ (kullanıcı ertelenen kaynakları gözden geçirmeli)
    """
    report_path = project_dir / "READING_REPORT.md"
    if not report_path.exists():
        return True  # Rapor yok → engel yok

    content = report_path.read_text(encoding="utf-8")
    # 🔴 Ertelendi satırı var mı?
    has_deferred = any(
        "🔴" in line and "Ertelendi" in line
        for line in content.splitlines()
        if line.strip().startswith("|")
    )
    if not has_deferred:
        return True  # Ertelenmiş kaynak yoktur

    # Ertelenmiş kaynaklar var, manuel onay gerekiyor
    gates = state.get("gates") or {}
    reviewed = gates.get("deferred_pool_reviewed")
    if isinstance(reviewed, dict):
        return reviewed.get("confirmed", False)
    return False


# ── Gate tanımları ───────────────────────────────────────────────────────────
#
# Her (from_phase, to_phase) çifti için bir koşul listesi.
# Bir koşul başarısız olursa faz geçişi bloklanır (force=True ile atlanabilir).
#
# Yapı: {doc_type: {(from, to): [GateCheck, ...]}}
# "all" anahtarı tüm doc type'lara uygulanır.

_GATES: dict[str, dict[tuple[int, int], list[GateCheck]]] = {
    "all": {
        (0, 1): [
            GateCheck(
                label="STATUS.md mevcut",
                check=_status_exists,
                failure_hint="Önce `python3 scripts/new_project.py --type <tür> --lang tr` çalıştır.",
            ),
            GateCheck(
                label="sources/ dizini mevcut",
                check=_sources_dir_exists,
                failure_hint="`mkdir -p sources` ile kaynak dizini oluştur.",
            ),
        ],
        (1, 2): [
            GateCheck(
                label="En az 1 PDF kaynakta mevcut",
                check=_has_at_least_n_pdfs(1),
                failure_hint=(
                    "Demir Kural 3 — AI önce kaynak arar:\n"
                    "  1. Otomatik: python3 scripts/find_source.py '<araştırma sorusu>' --output sources/\n"
                    "  2. DOI ile: python3 scripts/find_source.py --doi '10.xxxx/xxxxx'\n"
                    "  3. Agent ile: python3 agents/run.py source_hunter --research-question '...'\n"
                    "  4. Manuel: açık erişim (Unpaywall, DergiPark) ya da kurum kütüphanesinden PDF indir → sources/ klasörüne koy"
                ),
            ),
        ],
        (2, 3): [
            GateCheck(
                label="En az 3 kaynak kaynakta mevcut",
                check=_has_at_least_n_pdfs(3),
                failure_hint=(
                    "Okuma fazı için en az 3 PDF gerekli (Demir Kural 1).\n"
                    "  1. Otomatik: python3 scripts/find_source.py '<konu>' --output sources/\n"
                    "  2. Agent ile: python3 agents/run.py source_hunter --research-question '...'\n"
                    "  3. Manuel: açık erişim ya da kurum kütüphanesinden PDF indir → sources/"
                ),
            ),
            GateCheck(
                label="ARGUMENTS.md en az 3 argüman içeriyor",
                check=_argumanlar_has_n_entries(3),
                failure_hint=(
                    "ARGUMENTS.md dosyasına en az 3 argüman/iddia girişi ekle. "
                    "Argüman iskeletini oluşturmadan okuma fazına geçilmez."
                ),
            ),
        ],
    },
    "thesis": {
        (3, 4): [
            GateCheck(
                label="Okuma doygunluğu sağlandı (≥%80 okundu ya da saturation_reached=true)",
                check=_saturation_reached,
                failure_hint=(
                    "Phase 3 okuma doygunluğu kapısı: Kaynakların en az %80'ini oku "
                    "VEYA STATUS.md'de `saturation_reached: true` olarak işaretle."
                ),
            ),
            GateCheck(
                label="ARGUMENTS.md en az 5 argüman içeriyor",
                check=_argumanlar_has_n_entries(5),
                failure_hint="Okuma fazını bitirmeden önce en az 5 argüman/iddia girişi gerekli.",
            ),
            GateCheck(
                label="SAVUNMA_ZIRHI.md mevcut (Iron Rule 8)",
                check=_savunma_zirhi_exists,
                failure_hint=(
                    "Iron Rule 8: SAVUNMA_ZIRHI.md dosyasını oluştur. "
                    "Her argüman için en güçlü destek + en güçlü karşı argümanı yaz. "
                    "Bu dosya olmadan yazım fazına geçilemez."
                ),
            ),
        ],
        (4, 5): [
            GateCheck(
                label="Danışman onayı alındı (Faz 4 outline için)",
                check=_advisor_checkpoint_confirmed,
                failure_hint=(
                    "Iron Rule 5: Danışmanınla outline review toplantısı yap. "
                    "Onaydan sonra /tezatlas'a 'danışman onayladı' yaz."
                ),
            ),
        ],
        (5, 6): [
            GateCheck(
                label="Iron Rule 9: Ertelenmiş kaynak havuzu gözden geçirildi",
                check=_deferred_pool_cleared,
                failure_hint=(
                    "Iron Rule 9: Yazım fazına girmeden önce 🔴 ERKEN etiketli kaynakları gözden geçir. "
                    "Kapsam dışı olduklarını doğruladıktan sonra: "
                    "`python3 scripts/phase_gate_check.py --confirm deferred_pool_reviewed`"
                ),
            ),
        ],
    },
    "article": {
        (3, 4): [
            GateCheck(
                label="Okuma doygunluğu sağlandı",
                check=_saturation_reached,
                failure_hint="Kaynakların en az %80'ini oku veya saturation_reached=true işaretle.",
            ),
            GateCheck(
                label="ARGUMENTS.md en az 3 argüman içeriyor",
                check=_argumanlar_has_n_entries(3),
                failure_hint="Taslak yazmadan önce en az 3 argüman/iddia girişi gerekli.",
            ),
        ],
        (4, 5): [
            GateCheck(
                label="En az 5 kaynak kaynakta mevcut",
                check=_has_at_least_n_pdfs(5),
                failure_hint="Makale için en az 5 kaynak gerekli (Iron Rule 1).",
            ),
            GateCheck(
                label="Iron Rule 9: Ertelenmiş kaynak havuzu gözden geçirildi",
                check=_deferred_pool_cleared,
                failure_hint=(
                    "Iron Rule 9: Makale taslağına başlamadan önce ertelenen kaynakları gözden geçir. "
                    "`python3 scripts/phase_gate_check.py --confirm deferred_pool_reviewed`"
                ),
            ),
        ],
    },
    "lit-review": {
        (2, 3): [
            GateCheck(
                label="En az 10 kaynak kaynakta mevcut",
                check=_has_at_least_n_pdfs(10),
                failure_hint=(
                    "Literatür derlemesi için en az 10 kaynak gerekli. "
                    "Sistematik arama tamamlanmadan eleme fazına geçilmez."
                ),
            ),
        ],
        (3, 4): [
            GateCheck(
                label="Okuma doygunluğu sağlandı",
                check=_saturation_reached,
                failure_hint="Veri çıkarma fazına girmeden önce okuma doygunluğu gerekli.",
            ),
        ],
    },
}


# ── PhaseGate sınıfı ─────────────────────────────────────────────────────────

class PhaseGate:
    """
    Faz geçişi doğrulayıcı.

    Kullanım:
        gate = PhaseGate(Path("."), "thesis")
        result = gate.check(from_phase=3, to_phase=4)
    """

    def __init__(self, project_dir: Path, doc_type: str) -> None:
        self.project_dir = project_dir
        self.doc_type = doc_type

    def check(
        self, from_phase: int, to_phase: int, state: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Faz geçişi koşullarını kontrol eder.

        Döndürür:
            {
                "passed": bool,
                "passed_checks": [str, ...],
                "failed_checks": [{"label": str, "hint": str}, ...],
                "message": str,
            }
        """
        if state is None:
            from core.session import TezAtlasSession
            sess = TezAtlasSession(self.project_dir)
            state = sess.load()

        checks = self._collect_checks(from_phase, to_phase)

        passed_checks: list[str] = []
        failed_checks: list[dict[str, str]] = []

        for gc in checks:
            try:
                ok = gc.check(self.project_dir, state)
            except Exception:
                ok = False
            if ok:
                passed_checks.append(gc.label)
            else:
                failed_checks.append({"label": gc.label, "hint": gc.failure_hint})

        passed = len(failed_checks) == 0

        if passed:
            message = (
                f"✅ Faz {from_phase} → {to_phase} geçişi onaylandı. "
                f"{len(passed_checks)} koşul karşılandı."
            )
        else:
            message = (
                f"🚫 Faz {from_phase} → {to_phase} geçişi bloklandı. "
                f"{len(failed_checks)} koşul eksik."
            )

        return {
            "passed": passed,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "message": message,
            "from_phase": from_phase,
            "to_phase": to_phase,
        }

    def _collect_checks(
        self, from_phase: int, to_phase: int
    ) -> list[GateCheck]:
        """İlgili tüm gate check'leri toplar (genel + doc_type özgü)."""
        key = (from_phase, to_phase)
        checks: list[GateCheck] = []
        checks.extend(_GATES.get("all", {}).get(key, []))
        checks.extend(_GATES.get(self.doc_type, {}).get(key, []))
        return checks

    def check_all_remaining(
        self, current_phase: int, state: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Mevcut fazdan itibaren tüm gelecek kapıları kontrol eder.
        İlerleme haritası üretmek için kullanışlı.
        """
        results = []
        phase_names = _GATES.get("all", {})
        doc_gates = _GATES.get(self.doc_type, {})
        all_keys = set(phase_names.keys()) | set(doc_gates.keys())

        for from_ph, to_ph in sorted(all_keys):
            if from_ph >= current_phase:
                results.append(self.check(from_ph, to_ph, state))

        return results
