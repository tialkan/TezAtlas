"""Kaynak avcısı önerilerinin Crossref ile doğrulanması (ağa çıkmaz)."""

import asyncio

from agents.core.kaynak_dogrulama import benzerlik, oneriyi_dogrula, onerileri_dogrula

GERCEK = {"title": ["Implementation intentions: Strong effects of simple plans."], "DOI": "10.1037/0003-066x.54.7.493",
          "published": {"date-parts": [[1999]]}}


def test_benzerlik_noktalama_ve_alt_baslik() -> None:
    assert benzerlik("Implementation intentions: strong effects of simple plans", GERCEK["title"][0]) > 0.95
    assert benzerlik("Leaving the ivory tower", "Leaving the Ivory Tower: The Causes and Consequences of Departure") == 1.0
    assert benzerlik("Procrastination and the five-factor model: a facet approach", "Studying Procrastination Scale") < 0.9


def test_dogru_doi_dogrulanir() -> None:
    s = oneriyi_dogrula({"title": "Implementation intentions: Strong effects of simple plans", "doi": "10.1037/0003-066x.54.7.493"},
                        doi_getir=lambda d: GERCEK, ara=lambda b, y: [])
    assert s["dogrulama"]["durum"] == "dogrulandi"


def test_baska_esere_ait_doi_reddedilir() -> None:
    s = oneriyi_dogrula({"title": "Procrastination and the five-factor model: A facet approach", "doi": "10.1037/0003-066x.54.7.493"},
                        doi_getir=lambda d: GERCEK, ara=lambda b, y: [])
    assert s["dogrulama"]["durum"] == "dogrulanamadi"


def test_doisiz_oneri_aramayla_bulunur_ve_doi_eklenir() -> None:
    s = oneriyi_dogrula({"title": "Implementation intentions: strong effects of simple plans", "authors": ["Gollwitzer, P."], "year": 1999},
                        doi_getir=lambda d: None, ara=lambda b, y: [GERCEK])
    assert s["dogrulama"]["durum"] == "dogrulandi"
    assert s["doi"] == "10.1037/0003-066x.54.7.493"


def test_yil_cok_farkliysa_reddedilir() -> None:
    s = oneriyi_dogrula({"title": "Implementation intentions: strong effects of simple plans", "year": 2012},
                        doi_getir=lambda d: None, ara=lambda b, y: [GERCEK])
    assert s["dogrulama"]["durum"] == "dogrulanamadi"


def test_ag_hatasi_dogrulanmis_sayilmaz() -> None:
    def patla(*a):
        raise OSError("ağ yok")
    s = oneriyi_dogrula({"title": "X Y Z W", "doi": "10.1/x"}, doi_getir=patla, ara=patla)
    assert s["dogrulama"]["durum"] == "denetlenemedi"


def test_cikti_ikiye_ayrilir() -> None:
    cikti = {"recommendations": [
        {"title": "Implementation intentions: Strong effects of simple plans", "doi": "10.1037/0003-066x.54.7.493"},
        {"title": "Uydurma bir makale başlığı burada", "doi": "10.9/yok"},
    ]}
    sonuc = asyncio.run(onerileri_dogrula(cikti, doi_getir=lambda d: GERCEK if d.startswith("10.1037") else None, ara=lambda b, y: []))
    assert len(sonuc["recommendations"]) == 1
    assert len(sonuc["unverified"]) == 1
    assert "doğrulanamadı" in sonuc["verification_note"]
