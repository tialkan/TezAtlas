"""Token kullanımı ve tahmini maliyet.

Fiyatlar agents.yaml içindeki `fiyatlar` bölümünden okunur (1 milyon token başına USD,
girdi/çıktı). Fiyatlar değişir; bu bölümün tarihli olarak güncellenmesi gerekir.
Fiyatı bilinmeyen model için maliyet "bilinmiyor" yazılır, tahmin uydurulmaz.
Kayıt proje klasöründeki `.tezatlas/kullanim.jsonl` dosyasına eklenir.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def maliyet_hesapla(kullanim: list[dict], fiyatlar: dict) -> dict:
    toplam_girdi = sum(k["girdi_token"] for k in kullanim)
    toplam_cikti = sum(k["cikti_token"] for k in kullanim)
    usd = 0.0
    bilinmeyen = set()
    for k in kullanim:
        f = fiyatlar.get(k["model"])
        if not f:
            bilinmeyen.add(k["model"])
            continue
        usd += k["girdi_token"] / 1e6 * float(f["girdi"]) + k["cikti_token"] / 1e6 * float(f["cikti"])
    return {
        "girdi_token": toplam_girdi,
        "cikti_token": toplam_cikti,
        "tahmini_usd": round(usd, 4) if not bilinmeyen else None,
        "kismi_usd": round(usd, 4),
        "fiyati_bilinmeyen_modeller": sorted(bilinmeyen),
    }


def ozet_satiri(m: dict) -> str:
    tutar = f"≈ {m['tahmini_usd']:.4f} USD" if m["tahmini_usd"] is not None else (
        f"en az {m['kismi_usd']:.4f} USD (fiyatı bilinmeyen: {', '.join(m['fiyati_bilinmeyen_modeller'])})")
    return f"Kullanım: {m['girdi_token']:,} girdi + {m['cikti_token']:,} çıktı token, {tutar}"


def kaydet(proje: Path, gorev: str, kullanim: list[dict], m: dict) -> None:
    d = proje / ".tezatlas"
    d.mkdir(exist_ok=True)
    kayit = {"zaman": datetime.now(timezone.utc).isoformat(timespec="seconds"), "gorev": gorev, "kullanim": kullanim, **m}
    with open(d / "kullanim.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
