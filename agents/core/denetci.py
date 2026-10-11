"""Denetçi ve hakem ajanları: taslağı yazan modelden farklı bir modelle bağımsız denetim.

Aynı modelin kendi hatasını yakalaması zordur. Denetçi, yazarın gerekçelerini görmeden
yalnız taslağa ve kaynak notlarına bakar ("kör okuma"). Birden fazla model aynı taslağı
denetlediğinde bulgular yan yana konur; karar kullanıcınındır.
"""

from __future__ import annotations

import asyncio
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from agents.providers.base import LLMProvider

_PROMPTS = Path(__file__).resolve().parent.parent / "prompts"
NOT_KLASORLERI = ("notes", "notlar")
KAYNAK_KARAKTER_SINIRI = 6000      # kaynak başına
TOPLAM_KAYNAK_SINIRI = 120_000     # bütün kaynaklar


def kaynak_notlarini_oku(proje: Path, adlar: list[str] | None = None) -> dict[str, str]:
    """Projedeki not dosyalarını (notes/ veya notlar/) okur; isteğe bağlı ada göre süzer."""
    notlar: dict[str, str] = {}
    toplam = 0
    for klasor in NOT_KLASORLERI:
        d = proje / klasor
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            if adlar and not any(a.lower() in f.stem.lower() for a in adlar):
                continue
            metin = f.read_text(encoding="utf-8", errors="replace")[:KAYNAK_KARAKTER_SINIRI]
            if toplam + len(metin) > TOPLAM_KAYNAK_SINIRI:
                break
            notlar[f.stem] = metin
            toplam += len(metin)
    return notlar


def _json_ayikla(metin: str) -> dict:
    temiz = metin.strip()
    if temiz.startswith("```"):
        temiz = "\n".join(s for s in temiz.split("\n") if not s.strip().startswith("```"))
    try:
        return json.loads(temiz)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", temiz, re.S)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return {"raw_response": metin, "_parse_error": True}


def alintilari_dogrula(sonuc: dict, taslak: str) -> dict:
    """Modelin 'birebir alıntı' dediği metin gerçekten taslakta mı? Değilse bulgu işaretlenir."""
    def var_mi(alinti: str) -> bool:
        a = re.sub(r"\s+", " ", alinti or "").strip().strip("\"'“”…. ")
        if not a:
            return False
        t = re.sub(r"\s+", " ", taslak)
        if a in t:
            return True
        # Küçük farklılıklara (tırnak, tek harf) tolerans
        n = len(a)
        return any(SequenceMatcher(None, a, t[i:i + n]).ratio() > 0.9 for i in range(0, max(1, len(t) - n + 1), max(1, n // 4)))

    for alan in ("bulgular", "buyuk_sorunlar", "kucuk_sorunlar"):
        for b in sonuc.get(alan, []) or []:
            if isinstance(b, dict) and "alinti" in b:
                b["alinti_taslakta"] = var_mi(b.get("alinti", ""))
    return sonuc


class DenetciAgent:
    """Taslağı bağımsız denetler. rol='denetci' kanıt odaklı; rol='hakem' dergi hakemi gözüyle."""

    def __init__(self, provider: LLMProvider, model: str | None = None, rol: str = "denetci"):
        if rol not in ("denetci", "hakem"):
            raise ValueError("rol 'denetci' ya da 'hakem' olmalı")
        self.provider = provider
        self.model = model
        self.rol = rol
        self.system_prompt = (_PROMPTS / f"{rol}.md").read_text(encoding="utf-8")

    @property
    def etiket(self) -> str:
        return f"{self.provider.name}/{self.model or self.provider.default_model}"

    async def run(self, taslak: str, kaynak_notlari: dict[str, str] | None = None,
                  belge_turu: str = "thesis", alan: str = "") -> dict:
        yuk = {
            "belge_turu": belge_turu,
            "alan": alan,
            "taslak": taslak,
            "kaynak_notlari": [{"ad": ad, "metin": metin} for ad, metin in (kaynak_notlari or {}).items()],
        }
        mesajlar = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": json.dumps(yuk, ensure_ascii=False)},
        ]
        ham = await self.provider.chat(mesajlar, model=self.model, temperature=0.2)
        sonuc = alintilari_dogrula(_json_ayikla(ham), taslak)
        sonuc["_model"] = self.etiket
        return sonuc


def _benzer(a: str, b: str) -> bool:
    a, b = (re.sub(r"\s+", " ", x or "").strip().lower() for x in (a, b))
    if not a or not b:
        return False
    return a in b or b in a or SequenceMatcher(None, a, b).ratio() > 0.7


def karsilastir(sonuclar: list[dict]) -> list[dict]:
    """Birden fazla denetçinin bulgularını alıntıya göre eşleştirir.

    Dönen her satır: {"alinti", "tur", "modeller": {model: bulgu}}. Birden çok modelin bulduğu
    sorun daha güvenilirdir; yalnız birinin bulduğu sorun kullanıcının kararına bırakılır.
    """
    satirlar: list[dict] = []
    for s in sonuclar:
        model = s.get("_model", "?")
        for b in s.get("bulgular", []) or []:
            if not isinstance(b, dict):
                continue
            eslesen = next((r for r in satirlar if _benzer(r["alinti"], b.get("alinti", "")) and model not in r["modeller"]), None)
            if eslesen:
                eslesen["modeller"][model] = b
            else:
                satirlar.append({"alinti": b.get("alinti", ""), "tur": b.get("tur", ""), "modeller": {model: b}})
    satirlar.sort(key=lambda r: (-len(r["modeller"]), r["tur"]))
    return satirlar


def karsilastirma_raporu(taslak_adi: str, sonuclar: list[dict]) -> str:
    """Kullanıcının karar vereceği yan yana Markdown raporu."""
    modeller = [s.get("_model", "?") for s in sonuclar]
    satirlar = karsilastir(sonuclar)
    ortak = [r for r in satirlar if len(r["modeller"]) > 1]
    tekil = [r for r in satirlar if len(r["modeller"]) == 1]
    out = [
        f"# Çapraz denetim: {taslak_adi}",
        "",
        f"Denetçiler: {', '.join(modeller)}. Denetçiler yazarın notlarını görmeden yalnız taslağa ve kaynak notlarına baktı.",
        "Birden çok modelin bulduğu sorunlar önce gelir. Yalnız bir modelin bulduğu sorunlarda karar sizindir: kaynağa bakın, katılıyorsanız düzeltin, katılmıyorsanız nedenini bir satırla not edin.",
        "`alıntı taslakta: hayır` olan bulgularda model metinde olmayan bir şeyden söz ediyor olabilir; önce onu doğrulayın.",
        "",
        f"## Ortak bulgular ({len(ortak)})",
        "",
    ]

    def blok(r: dict) -> list[str]:
        satir = [f"### {r['tur'] or 'bulgu'}", "", f"> {r['alinti']}", ""]
        for m, b in r["modeller"].items():
            taslakta = "evet" if b.get("alinti_taslakta") else "hayır"
            satir.append(f"- **{m}** ({b.get('ciddiyet', '?')}; alıntı taslakta: {taslakta}): {b.get('aciklama', '')}")
            if b.get("kaynak"):
                satir.append(f"  - Kaynak: {b['kaynak']}")
            if b.get("oneri"):
                satir.append(f"  - Öneri: {b['oneri']}")
        satir += ["", "Kararınız: [ ] düzelttim  [ ] katılmıyorum, çünkü: ", ""]
        return satir

    for r in ortak:
        out += blok(r)
    out += [f"## Yalnız bir modelin bulduğu sorunlar ({len(tekil)})", ""]
    for r in tekil:
        out += blok(r)
    out += ["## Genel değerlendirmeler", ""]
    for s in sonuclar:
        out += [f"**{s.get('_model', '?')}:** {s.get('genel_degerlendirme', s.get('raw_response', '')[:500])}", ""]
    return "\n".join(out)


async def capraz_denetim(saglayicilar: list[tuple[LLMProvider, str | None]], taslak: str,
                         kaynak_notlari: dict[str, str], **kw) -> list[dict]:
    """Aynı taslağı birden fazla modelle paralel denetler."""
    ajanlar = [DenetciAgent(p, m) for p, m in saglayicilar]
    return await asyncio.gather(*(a.run(taslak, kaynak_notlari, **kw) for a in ajanlar))
