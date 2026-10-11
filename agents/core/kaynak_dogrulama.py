"""Model önerdiği kaynakların gerçekten var olup olmadığını Crossref ile denetler.

Dil modelleri var olmayan makaleleri, yanlış DOI'leri ve yanlış yılları kendinden emin
biçimde önerebilir. Bu modül her öneriyi Crossref kaydıyla karşılaştırır:

- DOI verilmişse: DOI çözülür ve kayıttaki başlık önerilen başlıkla eşleşmelidir.
- DOI yoksa: başlık ve ilk yazarla arama yapılır; en iyi sonucun başlığı yeterince benzer
  ve yılı en fazla bir yıl farklı olmalıdır.

Eşleşmeyen öneri kullanıcıya "doğrulanmış kaynak" olarak gösterilmez.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from typing import Callable

MAILTO = os.environ.get("TEZATLAS_MAILTO", "tezatlas@example.com")
_UA = f"TezAtlas/1.1 (https://github.com/tialkan/TezAtlas; mailto:{MAILTO})"
ESIK = 0.9


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c)).replace("ı", "i").casefold()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def benzerlik(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return 0.0
    # Alt başlıklı kayıtlar: "Başlık: Alt başlık" ile "Başlık" eşleşebilsin
    kisa, uzun = sorted((a, b), key=len)
    if len(kisa.split()) >= 4 and uzun.startswith(kisa):
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def _yil(kayit: dict) -> int | None:
    for alan in ("published", "published-print", "published-online", "issued"):
        parcalar = (kayit.get(alan) or {}).get("date-parts") or [[None]]
        if parcalar and parcalar[0] and parcalar[0][0]:
            return int(parcalar[0][0])
    return None


def _crossref_get(url: str) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode()).get("message")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def crossref_doi(doi: str) -> dict | None:
    return _crossref_get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="") + f"?mailto={MAILTO}")


def crossref_ara(baslik: str, yazar: str = "") -> list[dict]:
    q = urllib.parse.urlencode({"query.bibliographic": f"{baslik} {yazar}".strip()[:300], "rows": "3", "mailto": MAILTO})
    msg = _crossref_get(f"https://api.crossref.org/works?{q}")
    return (msg or {}).get("items", []) or []


def oneriyi_dogrula(
    oneri: dict,
    doi_getir: Callable[[str], dict | None] = crossref_doi,
    ara: Callable[[str, str], list[dict]] = crossref_ara,
) -> dict:
    """Tek bir öneriyi denetler ve `dogrulama` alanını ekleyerek döndürür."""
    baslik = str(oneri.get("title") or "")
    yazarlar = oneri.get("authors") or []
    ilk_yazar = str(yazarlar[0]).split(",")[0] if yazarlar else ""
    yil = oneri.get("year")
    doi = (oneri.get("doi") or "").strip().removeprefix("https://doi.org/") or None
    sonuc = dict(oneri)

    try:
        if doi:
            kayit = doi_getir(doi)
            if not kayit:
                sonuc["dogrulama"] = {"durum": "dogrulanamadi", "neden": "DOI Crossref'te yok"}
                return sonuc
            kayit_baslik = (kayit.get("title") or [""])[0]
            if benzerlik(baslik, kayit_baslik) >= ESIK:
                sonuc["dogrulama"] = {"durum": "dogrulandi", "kaynak": "crossref", "doi": doi, "baslik": kayit_baslik, "yil": _yil(kayit)}
            else:
                sonuc["dogrulama"] = {"durum": "dogrulanamadi", "neden": "DOI başka bir esere ait", "doi_kaydi": kayit_baslik}
            return sonuc

        for kayit in ara(baslik, ilk_yazar):
            kayit_baslik = (kayit.get("title") or [""])[0]
            kayit_yil = _yil(kayit)
            yil_uygun = not yil or not kayit_yil or abs(int(yil) - kayit_yil) <= 1
            if benzerlik(baslik, kayit_baslik) >= ESIK and yil_uygun:
                sonuc["doi"] = kayit.get("DOI")
                sonuc["dogrulama"] = {"durum": "dogrulandi", "kaynak": "crossref-arama", "doi": kayit.get("DOI"), "baslik": kayit_baslik, "yil": kayit_yil}
                return sonuc
        sonuc["dogrulama"] = {"durum": "dogrulanamadi", "neden": "Crossref'te eşleşen kayıt bulunamadı"}
    except Exception as hata:  # ağ hatası: öneri doğrulanmış sayılmaz
        sonuc["dogrulama"] = {"durum": "denetlenemedi", "neden": f"Crossref'e ulaşılamadı ({type(hata).__name__})"}
    return sonuc


async def onerileri_dogrula(cikti: dict, **kw) -> dict:
    """Kaynak avcısı çıktısını böler: doğrulananlar `recommendations`, kalanlar `unverified`."""
    if not isinstance(cikti, dict) or "recommendations" not in cikti:
        return cikti
    dogrulanan, kalan = [], []
    for oneri in cikti.get("recommendations") or []:
        sonuc = await asyncio.to_thread(oneriyi_dogrula, oneri, **kw)
        (dogrulanan if sonuc["dogrulama"]["durum"] == "dogrulandi" else kalan).append(sonuc)
    yeni = dict(cikti)
    yeni["recommendations"] = dogrulanan
    yeni["unverified"] = kalan
    yeni["verification_note"] = (
        f"{len(dogrulanan)} öneri Crossref kaydıyla eşleşti. {len(kalan)} öneri doğrulanamadı; "
        "bunlar kaynak olarak kullanılmadan önce elle kontrol edilmelidir."
    )
    return yeni
