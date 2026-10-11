"""Denetçi, hakem ve çapraz denetim (ağa çıkmaz; sahte sağlayıcı)."""

import asyncio
import json
from pathlib import Path

from agents.core.denetci import (
    DenetciAgent, alintilari_dogrula, capraz_denetim, karsilastir, karsilastirma_raporu, kaynak_notlarini_oku,
)
from agents.maliyet import maliyet_hesapla, ozet_satiri
from agents.providers.base import LLMProvider

TASLAK = (
    "Merkez bankası dijital paraları bankacılık sistemini kesinlikle istikrarsızlaştırır (Smith, 2020). "
    "Bu konu kritik öneme sahiptir ve yalnızca ekonomik değil aynı zamanda siyasi bir meseledir."
)


class SahteSaglayici(LLMProvider):
    def __init__(self, ad: str, yanit: dict):
        super().__init__(name=ad, default_model=f"{ad}-model")
        self.yanit = yanit
        self.gelen: list = []
        self.usage = []

    async def chat(self, messages, model=None, temperature=0.3) -> str:
        self.gelen.append(messages)
        self.usage.append({"model": model or self.default_model, "girdi_token": 1000, "cikti_token": 200})
        return json.dumps(self.yanit, ensure_ascii=False)

    async def health_check(self) -> dict:
        return {"status": "ok"}


def _bulgu(alinti, tur="iddia_gucu"):
    return {"tur": tur, "ciddiyet": "yuksek", "alinti": alinti, "aciklama": "x", "kaynak": "Smith_2020_notlar", "oneri": "y"}


def test_denetci_kor_okur_ve_alintiyi_dogrular() -> None:
    p = SahteSaglayici("a", {"bulgular": [_bulgu("kesinlikle istikrarsızlaştırır"), _bulgu("Bu cümle taslakta hiç yok")],
                             "genel_degerlendirme": "g"})
    sonuc = asyncio.run(DenetciAgent(p, None).run(TASLAK, {"Smith_2020_notlar": "olabilir diyor"}))
    yuk = json.loads(p.gelen[0][1]["content"])
    assert set(yuk) == {"belge_turu", "alan", "taslak", "kaynak_notlari"}, "yazarın gerekçeleri denetçiye gitmez"
    assert sonuc["bulgular"][0]["alinti_taslakta"] is True
    assert sonuc["bulgular"][1]["alinti_taslakta"] is False
    assert sonuc["_model"] == "a/a-model"


def test_hakem_rolu_ayri_istem_kullanir() -> None:
    p = SahteSaglayici("h", {"karar_onerisi": "buyuk_duzeltme", "buyuk_sorunlar": [_bulgu("kritik öneme sahiptir")]})
    ajan = DenetciAgent(p, None, rol="hakem")
    assert "hakem" in ajan.system_prompt.lower()
    sonuc = asyncio.run(ajan.run(TASLAK))
    assert sonuc["buyuk_sorunlar"][0]["alinti_taslakta"] is True


def test_capraz_denetim_ortak_ve_tekil_bulgular() -> None:
    a = SahteSaglayici("a", {"bulgular": [_bulgu("kesinlikle istikrarsızlaştırır"), _bulgu("kritik öneme sahiptir", "ai_kalibi")]})
    b = SahteSaglayici("b", {"bulgular": [_bulgu("bankacılık sistemini kesinlikle istikrarsızlaştırır")]})
    sonuclar = asyncio.run(capraz_denetim([(a, None), (b, None)], TASLAK, {}))
    satirlar = karsilastir(sonuclar)
    assert len(satirlar[0]["modeller"]) == 2, "iki modelin bulduğu sorun önce gelir"
    assert len(satirlar) == 2
    rapor = karsilastirma_raporu("giris.md", sonuclar)
    assert "Ortak bulgular (1)" in rapor and "Yalnız bir modelin bulduğu sorunlar (1)" in rapor
    assert "Kararınız" in rapor


def test_ayristirilamayan_yanit_bozmaz() -> None:
    sonuc = alintilari_dogrula({"raw_response": "metin", "_parse_error": True}, TASLAK)
    assert sonuc["_parse_error"]


def test_not_okuma(tmp_path: Path) -> None:
    (tmp_path / "notlar").mkdir()
    (tmp_path / "notlar" / "Smith_2020_notlar.md").write_text("Smith: olabilir", encoding="utf-8")
    (tmp_path / "notlar" / "Jones_2019_notlar.md").write_text("Jones", encoding="utf-8")
    assert set(kaynak_notlarini_oku(tmp_path)) == {"Smith_2020_notlar", "Jones_2019_notlar"}
    assert set(kaynak_notlarini_oku(tmp_path, ["smith"])) == {"Smith_2020_notlar"}


def test_maliyet() -> None:
    k = [{"model": "openai/gpt-6.1-sol", "girdi_token": 1_000_000, "cikti_token": 100_000}]
    m = maliyet_hesapla(k, {"openai/gpt-6.1-sol": {"girdi": 2.0, "cikti": 10.0}})
    assert m["tahmini_usd"] == 3.0
    bilinmeyen = maliyet_hesapla(k + [{"model": "x/y", "girdi_token": 5, "cikti_token": 5}], {"openai/gpt-6.1-sol": {"girdi": 2.0, "cikti": 10.0}})
    assert bilinmeyen["tahmini_usd"] is None and "x/y" in ozet_satiri(bilinmeyen)
