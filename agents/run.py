#!/usr/bin/env python3
"""TezAtlas Multi-Agent CLI — run agents from the command line.

Usage:
    python agents/run.py source_hunter --research-question "..." --field economics
    python agents/run.py methodology_checker --input methodology.md --research-question "..."
    python agents/run.py citation_verifier --claim "..." --source sources/file.pdf
    python agents/run.py denetci --input bolumler/giris.md [--notes-dir .] [--kaynak Smith2020]
    python agents/run.py hakem --input makale.md
    python agents/run.py capraz_denetim --input bolumler/giris.md [--modeller openrouter/openai/gpt-6.1-sol,openrouter/google/gemini-3.8-flash]
    python agents/run.py --list-providers
    python agents/run.py --test-providers
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so `agents` package resolves
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agents.config import AgentConfig
from agents.core.source_hunter import SourceHunterAgent
from agents.core.methodology_checker import MethodologyCheckerAgent
from agents.core.citation_verifier import CitationVerifierAgent
from agents.core.denetci import DenetciAgent, capraz_denetim, kaynak_notlarini_oku, karsilastirma_raporu
from agents.maliyet import kaydet, maliyet_hesapla, ozet_satiri


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ── List providers ──────────────────────────────────────────────

def cmd_list_providers(config: AgentConfig) -> None:
    print("=== Configured Providers ===\n")
    for p in config.list_providers():
        key_status = "SET" if p["api_key_set"] else "NOT SET"
        print(f"  {p['name']}")
        print(f"    Type:    {p['type']}")
        print(f"    Base:    {p['base_url']}")
        print(f"    Model:   {p['default_model']}")
        print(f"    Key env: {p['api_key_env']} ({key_status})")
        print()

    print("=== Agent Assignments ===\n")
    for a in config.list_agents():
        model = a["model"] or "(provider default)"
        print(f"  {a['name']}  →  {a['provider']} / {model}")
        print(f"    {a['description']}")
        print()


# ── Test providers ──────────────────────────────────────────────

async def _test_providers(config: AgentConfig) -> None:
    print("=== Provider Health Check ===\n")
    for info in config.list_providers():
        name = info["name"]
        if not info["api_key_set"] and info["api_key_env"].lower() != "none":
            print(f"  {name}: SKIPPED (no API key)")
            continue
        try:
            provider = config.get_provider(name)
            result = await provider.health_check()
            status = result["status"].upper()
            detail = result.get("detail", "")
            print(f"  {name}: {status} — {detail}")
        except Exception as exc:
            print(f"  {name}: ERROR — {exc}")
    print()


def cmd_test_providers(config: AgentConfig) -> None:
    asyncio.run(_test_providers(config))


# ── Source Hunter ───────────────────────────────────────────────

async def _run_source_hunter(config: AgentConfig, args: argparse.Namespace) -> None:
    provider, model = config.get_agent_provider("source_hunter")
    agent = SourceHunterAgent(provider, model)

    existing = []
    if args.existing_sources:
        src_dir = Path(args.existing_sources)
        if src_dir.is_dir():
            existing = [f.stem for f in src_dir.iterdir() if f.suffix == ".pdf"]

    result = await agent.run(
        research_question=args.research_question,
        field=args.field or "",
        existing_sources=existing,
        language_preference=args.language or "both",
    )
    _print_json(result)


# ── Methodology Checker ────────────────────────────────────────

async def _run_methodology_checker(config: AgentConfig, args: argparse.Namespace) -> None:
    provider, model = config.get_agent_provider("methodology_checker")
    agent = MethodologyCheckerAgent(provider, model)

    input_path = Path(args.input)
    if input_path.exists():
        methodology_text = input_path.read_text(encoding="utf-8")
    else:
        methodology_text = args.input  # treat as inline text

    result = await agent.run(
        methodology_text=methodology_text,
        research_question=args.research_question or "",
        field=args.field or "",
        document_type=args.document_type or "thesis",
    )
    _print_json(result)


# ── Citation Verifier ──────────────────────────────────────────

async def _run_citation_verifier(config: AgentConfig, args: argparse.Namespace) -> None:
    provider, model = config.get_agent_provider("citation_verifier")
    agent = CitationVerifierAgent(provider, model)

    result = await agent.run(
        claim=args.claim,
        source_path=args.source,
    )
    _print_json(result)


# ── Denetçi, hakem, çapraz denetim ─────────────────────────────

def _taslak_oku(yol: str) -> tuple[str, str]:
    p = Path(yol)
    if not p.is_file():
        print(f"Taslak dosyası bulunamadı: {yol}", file=sys.stderr)
        sys.exit(2)
    return p.read_text(encoding="utf-8"), p.name


def _maliyet_bildir(config: AgentConfig, proje: Path, gorev: str, saglayicilar) -> None:
    tekil = list({id(s): s for s in saglayicilar}.values())  # aynı sağlayıcı iki kez sayılmasın
    kullanim = [k for s in tekil for k in getattr(s, "usage", [])]
    if not kullanim:
        return
    m = maliyet_hesapla(kullanim, config.raw.get("fiyatlar", {}) or {})
    print(ozet_satiri(m), file=sys.stderr)
    kaydet(proje, gorev, kullanim, m)


async def _run_denetci(config: AgentConfig, args: argparse.Namespace, rol: str) -> None:
    taslak, ad = _taslak_oku(args.input)
    proje = Path(args.notes_dir).resolve()
    notlar = kaynak_notlarini_oku(proje, args.kaynak or None)
    if not notlar:
        print("Uyarı: notes/ ya da notlar/ klasöründe kaynak notu bulunamadı; denetçi yalnız taslağa bakacak "
              "ve kaynak-iddia uyumunu denetleyemeyecek.", file=sys.stderr)
    provider, model = config.get_agent_provider(rol)
    sonuc = await DenetciAgent(provider, model, rol=rol).run(taslak, notlar, belge_turu=args.document_type, alan=args.field)
    _maliyet_bildir(config, proje, f"{rol}:{ad}", [provider])
    _print_json(sonuc)


async def _run_capraz(config: AgentConfig, args: argparse.Namespace) -> None:
    taslak, ad = _taslak_oku(args.input)
    proje = Path(args.notes_dir).resolve()
    notlar = kaynak_notlarini_oku(proje, args.kaynak or None)
    hedefler = [h.strip() for h in (args.modeller.split(",") if args.modeller else config.raw.get("capraz_denetim", [])) if h.strip()]
    if len(hedefler) < 2:
        print("Çapraz denetim için en az iki model gerekir (agents.yaml: capraz_denetim ya da --modeller).", file=sys.stderr)
        sys.exit(2)
    saglayicilar = []
    for h in hedefler:
        ad_saglayici, _, model = h.partition("/")
        saglayicilar.append((config.get_provider(ad_saglayici), model or None))
    sonuclar = await capraz_denetim(saglayicilar, taslak, notlar, belge_turu=args.document_type, alan=args.field)
    rapor = karsilastirma_raporu(ad, sonuclar)
    cikti = Path(args.output) if args.output else Path(args.input).with_name(Path(args.input).stem + "_DENETIM.md")
    cikti.write_text(rapor, encoding="utf-8")
    _maliyet_bildir(config, proje, f"capraz_denetim:{ad}", [p for p, _ in saglayicilar])
    print(f"Rapor yazıldı: {cikti}")


# ── Argument parser ────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agents/run.py",
        description="TezAtlas Multi-Agent CLI",
    )
    parser.add_argument(
        "--list-providers", action="store_true",
        help="Show all configured providers and agent assignments",
    )
    parser.add_argument(
        "--test-providers", action="store_true",
        help="Health-check all configured providers",
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to agents.yaml (default: project root)",
    )

    sub = parser.add_subparsers(dest="agent")

    # source_hunter
    sh = sub.add_parser("source_hunter", help="Run Source Hunter Agent")
    sh.add_argument("--research-question", required=True)
    sh.add_argument("--field", default="")
    sh.add_argument("--existing-sources", default=None,
                    help="Path to sources/ directory")
    sh.add_argument("--language", default="both",
                    choices=["tr", "en", "both"])

    # methodology_checker
    mc = sub.add_parser("methodology_checker", help="Run Methodology Checker Agent")
    mc.add_argument("--input", required=True,
                    help="Path to methodology text file, or inline text")
    mc.add_argument("--research-question", default="")
    mc.add_argument("--field", default="")
    mc.add_argument("--document-type", default="thesis",
                    choices=["thesis", "article", "report"])

    # citation_verifier
    cv = sub.add_parser("citation_verifier", help="Run Citation Verifier Agent")
    cv.add_argument("--claim", required=True)
    cv.add_argument("--source", required=True,
                    help="Path to source PDF file")

    for ad, yardim in (("denetci", "Taslağı farklı bir modelle kör denetle"),
                       ("hakem", "Dergi hakemi simülasyonu"),
                       ("capraz_denetim", "Taslağı birden çok modelle denetle, bulguları yan yana koy")):
        d = sub.add_parser(ad, help=yardim)
        d.add_argument("--input", required=True, help="Taslak dosyası (Markdown)")
        d.add_argument("--notes-dir", default=".", help="notes/ ya da notlar/ klasörünü içeren proje klasörü")
        d.add_argument("--kaynak", action="append", help="Yalnız adı bu ifadeyi içeren notları kullan (tekrarlanabilir)")
        d.add_argument("--document-type", default="thesis")
        d.add_argument("--field", default="")
        if ad == "capraz_denetim":
            d.add_argument("--modeller", default=None, help="Virgülle ayrılmış saglayici/model listesi")
            d.add_argument("--output", default=None, help="Rapor dosyası (varsayılan: <taslak>_DENETIM.md)")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None
    config = AgentConfig(config_path) if config_path else AgentConfig()

    if args.list_providers:
        cmd_list_providers(config)
        return

    if args.test_providers:
        cmd_test_providers(config)
        return

    if args.agent == "source_hunter":
        asyncio.run(_run_source_hunter(config, args))
    elif args.agent == "methodology_checker":
        asyncio.run(_run_methodology_checker(config, args))
    elif args.agent == "citation_verifier":
        asyncio.run(_run_citation_verifier(config, args))
    elif args.agent in ("denetci", "hakem"):
        asyncio.run(_run_denetci(config, args, args.agent))
    elif args.agent == "capraz_denetim":
        asyncio.run(_run_capraz(config, args))
    else:
        parser.print_help()
        sys.exit(1)


def _calistir() -> None:
    """Yapılandırma hatalarını (eksik anahtar, bilinmeyen sağlayıcı) okunur mesaja çevirir."""
    try:
        main()
    except ValueError as hata:
        print(f"Hata: {hata}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    _calistir()
