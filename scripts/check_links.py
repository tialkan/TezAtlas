#!/usr/bin/env python3
"""Skill grafiğindeki iç bağlantıları denetler.

Denetlenenler: [[wikilink]], göreli markdown bağlantıları ve frontmatter'daki
links_to / used_by / phase_gate_in / phase_gate_out yolları.
Kırık bağlantı varsa listeleyip 1 ile çıkar (CI bunu hata sayar).

Kullanım: python3 scripts/check_links.py [repo_kökü]
"""
from __future__ import annotations

import collections
import os
import re
import sys

ALANLAR = ("links_to", "used_by", "phase_gate_in", "phase_gate_out")


def md_dosyalari(kok: str) -> list[str]:
    dosyalar = []
    for d, _, fs in os.walk(os.path.join(kok, "skills")):
        dosyalar += [os.path.join(d, f) for f in fs if f.endswith(".md")]
    komutlar = os.path.join(kok, ".claude", "commands")
    if os.path.isdir(komutlar):
        dosyalar += [os.path.join(komutlar, f) for f in os.listdir(komutlar) if f.endswith(".md")]
    for ek in ("CLAUDE.md",):
        if os.path.exists(os.path.join(kok, ek)):
            dosyalar.append(os.path.join(kok, ek))
    return dosyalar


def var_mi(hedef: str, kaynak: str, kok: str) -> bool:
    hedef = hedef.split("#")[0].strip()
    if not hedef:
        return True
    adaylar = [os.path.join(os.path.dirname(kaynak), hedef), os.path.join(kok, hedef), os.path.join(kok, "skills", hedef)]
    adaylar += [a + ".md" for a in adaylar]
    return any(os.path.exists(a) for a in adaylar)


def frontmatter_yollari(metin: str):
    fm = re.match(r"---\n(.*?)\n---", metin, re.S)
    if not fm:
        return
    alan = None
    for satir in fm.group(1).splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", satir)
        if m:
            alan, deger = m.group(1), m.group(2).strip()
        else:
            m2 = re.match(r'^\s+-\s+"?([^"#]+?)"?\s*$', satir)
            if not m2:
                continue
            deger = m2.group(1)
        if alan not in ALANLAR:
            continue
        for oge in re.split(r",\s*", deger.strip("[]")):
            oge = oge.strip().strip('"').strip("'")
            if oge.endswith(".md"):
                yield alan, oge


def denetle(kok: str) -> dict[str, list[tuple[str, str]]]:
    dosyalar = md_dosyalari(kok)
    kokler = {os.path.splitext(os.path.basename(f))[0] for f in dosyalar}
    kirik: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for f in dosyalar:
        metin = open(f, encoding="utf-8").read()
        govde = re.sub(r"```.*?```", "", metin, flags=re.S)
        goreli = os.path.relpath(f, kok)
        for m in re.finditer(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", govde):
            h = m.group(1).strip()
            if not (var_mi(h, f, kok) or os.path.basename(h) in kokler):
                kirik["wikilink"].append((goreli, h))
        for m in re.finditer(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)", govde):
            h = m.group(1)
            if re.match(r"(https?|mailto):", h) or h.startswith("#"):
                continue
            if not var_mi(h, f, kok):
                kirik["markdown"].append((goreli, h))
        for alan, h in frontmatter_yollari(metin):
            if not var_mi(h, f, kok):
                kirik[alan].append((goreli, h))
    return kirik


def main() -> int:
    kok = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kirik = denetle(kok)
    toplam = sum(len(v) for v in kirik.values())
    if not toplam:
        print("Bağlantı denetimi: kırık bağlantı yok.")
        return 0
    for tur, liste in kirik.items():
        print(f"\n[{tur}] {len(liste)} kırık bağlantı")
        for kaynak, hedef in liste:
            print(f"  {kaynak} -> {hedef}")
    print(f"\nToplam {toplam} kırık bağlantı.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
