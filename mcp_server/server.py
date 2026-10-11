#!/usr/bin/env python3
"""
TezAtlas MCP Server — Academic APIs
-------------------------------------
Provides MCP tools for academic paper discovery and citation management.
Exposes Semantic Scholar, OpenAlex, and CrossRef APIs as structured tools.

Usage (via Claude Code MCP config):
    Add to claude_desktop_config.json or .claude/mcp.json:

    {
      "mcpServers": {
        "tezatlas-academic": {
          "command": "python3",
          "args": ["/path/to/TezAtlas/mcp_server/server.py"],
          "env": {
            "S2_API_KEY": "optional-semantic-scholar-key"
          }
        }
      }
    }

Tools provided:
    - search_papers        : Search academic papers across multiple sources
    - get_paper_details    : Detailed metadata for a specific paper (by DOI or S2 ID)
    - get_citations        : Papers citing a given paper
    - get_references       : Papers cited by a given paper
    - doi_to_bibtex        : Get BibTeX for a DOI
    - search_authors       : Find researcher profiles
    - get_related_papers   : Citation-graph-based related paper discovery
"""

import asyncio
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        TextContent, Tool,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from mcp_server.api_clients import AcademicSearch, CrossRefClient, SemanticScholarClient

S2_API_KEY = os.getenv("S2_API_KEY")
academic = AcademicSearch(s2_api_key=S2_API_KEY)
crossref = CrossRefClient()
s2 = SemanticScholarClient(api_key=S2_API_KEY)


# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "search_papers",
        "description": (
            "Search academic papers across Semantic Scholar, OpenAlex, and CrossRef. "
            "Returns ranked results with title, authors, year, DOI, citation count, "
            "abstract snippet, and open-access PDF link when available. "
            "Use for literature discovery in TezAtlas Phase 2 (source gathering)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query — keywords, topic, or research question"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results per source (default: 5, max: 20)",
                    "default": 5
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["s2", "openalex", "crossref"]},
                    "description": "Which sources to query (default: all three)"
                },
                "open_access_only": {
                    "type": "boolean",
                    "description": "Only return open-access papers",
                    "default": False
                },
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_paper_details",
        "description": (
            "Fetch detailed metadata for a specific paper by DOI or Semantic Scholar ID. "
            "Returns full author list, abstract, venue, citation counts, "
            "open-access PDF link, and fields of study."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "identifier": {
                    "type": "string",
                    "description": "DOI (e.g. '10.1234/example') or S2 paper ID or 'DOI:10.xxx' or 'arXiv:2301.xxxxx'"
                },
            },
            "required": ["identifier"]
        }
    },
    {
        "name": "get_citations",
        "description": (
            "Get papers that cite a given paper (incoming citations). "
            "Useful for TezAtlas snowball sampling — find newer work that builds on a source."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_id": {"type": "string", "description": "S2 paperId or DOI:xxx"},
                "limit": {"type": "integer", "default": 20, "description": "Max citations to return"},
            },
            "required": ["paper_id"]
        }
    },
    {
        "name": "get_references",
        "description": (
            "Get papers referenced by a given paper (outgoing references). "
            "Useful for backward snowball sampling — find foundational sources."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_id": {"type": "string", "description": "S2 paperId or DOI:xxx"},
                "limit": {"type": "integer", "default": 50, "description": "Max references to return"},
            },
            "required": ["paper_id"]
        }
    },
    {
        "name": "doi_to_bibtex",
        "description": (
            "Convert a DOI to a BibTeX entry. Uses CrossRef content negotiation. "
            "Returns ready-to-use BibTeX that can be added to references.bib."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "doi": {"type": "string", "description": "DOI string (e.g. '10.1234/example')"},
            },
            "required": ["doi"]
        }
    },
    {
        "name": "search_authors",
        "description": (
            "Search for researcher profiles by name. "
            "Returns affiliation, paper count, citation count, h-index, and ORCID when available."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Author name to search"},
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_related_papers",
        "description": (
            "Find papers related to a seed paper via citation graph. "
            "Returns both papers that cite it (newer work) and papers it cites (foundational). "
            "Core tool for TezAtlas snowball sampling protocol."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "paper_id": {"type": "string", "description": "S2 paperId or DOI:xxx"},
                "direction": {
                    "type": "string",
                    "enum": ["both", "forward", "backward"],
                    "default": "both",
                    "description": "forward=papers citing this, backward=papers cited by this"
                },
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["paper_id"]
        }
    },
]


# ── Tool handlers ─────────────────────────────────────────────────────────────

def _format_paper_list(papers: list[dict], max_items: int = 20) -> str:
    """Format a list of papers as readable markdown."""
    if not papers:
        return "No papers found."
    lines = []
    for i, p in enumerate(papers[:max_items], 1):
        lines.append(f"**{i}. {p.get('title', 'Unknown title')}**")
        if p.get("authors"):
            lines.append(f"   Authors: {p['authors']}")
        parts = []
        if p.get("year"):
            parts.append(p["year"])
        if p.get("journal"):
            parts.append(p["journal"])
        if parts:
            lines.append(f"   {' — '.join(parts)}")
        if p.get("doi"):
            lines.append(f"   DOI: {p['doi']}")
        if p.get("citation_count"):
            lines.append(f"   Citations: {p['citation_count']}")
        if p.get("open_access_pdf"):
            lines.append(f"   PDF: {p['open_access_pdf']}")
        if p.get("abstract"):
            lines.append(f"   Abstract: {p['abstract'][:200]}...")
        lines.append("")
    return "\n".join(lines)


def handle_search_papers(args: dict) -> str:
    query = args["query"]
    limit = min(args.get("limit", 5), 20)
    sources = args.get("sources", None)
    open_access = args.get("open_access_only", False)

    results = academic.search(query, limit_per_source=limit, sources=sources)

    if open_access:
        results = [r for r in results if r.get("open_access") or r.get("open_access_pdf")]

    hatalar = getattr(academic, "son_hatalar", [])
    if not results:
        if hatalar:
            return f"Sonuç alınamadı; kaynaklardan biri ya da birkaçı hata verdi (hız sınırı olabilir): {'; '.join(hatalar)}"
        return f"No papers found for query: '{query}'"

    header = f"## Search Results: '{query}'\n{len(results)} papers found\n\n"
    return header + _format_paper_list(results)


def handle_get_paper_details(args: dict) -> str:
    identifier = args["identifier"].strip()
    paper = s2.get_paper(identifier)
    if not paper:
        # Try CrossRef if identifier looks like a DOI
        if identifier.startswith("10.") or identifier.startswith("DOI:"):
            doi = identifier.replace("DOI:", "").strip()
            work = crossref.works_by_doi(doi)
            if work:
                paper = crossref.format_work(work)
    if not paper:
        return f"Paper not found: {identifier}"
    lines = [f"## {paper.get('title', 'Unknown')}"]
    for field in ["authors", "year", "journal", "doi", "citation_count",
                  "influential_citations", "open_access_pdf", "fields"]:
        val = paper.get(field)
        if val:
            lines.append(f"**{field.replace('_', ' ').title()}:** {val}")
    if paper.get("abstract"):
        lines.append(f"\n**Abstract:** {paper['abstract']}")
    return "\n".join(lines)


def handle_get_citations(args: dict) -> str:
    paper_id = args["paper_id"]
    limit = args.get("limit", 20)
    papers = s2.get_citations(paper_id, limit=limit)
    if not papers:
        return f"No citations found for: {paper_id}"
    return f"## Papers citing {paper_id} ({len(papers)} found)\n\n" + _format_paper_list(papers)


def handle_get_references(args: dict) -> str:
    paper_id = args["paper_id"]
    limit = args.get("limit", 50)
    papers = s2.get_references(paper_id, limit=limit)
    if not papers:
        return f"No references found for: {paper_id}"
    return f"## References in {paper_id} ({len(papers)} found)\n\n" + _format_paper_list(papers)


def handle_doi_to_bibtex(args: dict) -> str:
    doi = args["doi"].strip().replace("https://doi.org/", "")
    bibtex = academic.doi_to_bibtex(doi)
    if bibtex:
        return f"```bibtex\n{bibtex}\n```"
    return f"Could not retrieve BibTeX for DOI: {doi}"


def handle_search_authors(args: dict) -> str:
    name = args["name"]
    limit = args.get("limit", 5)
    results = s2.search_author(name, limit=limit)
    if not results:
        return f"No authors found for: {name}"
    lines = [f"## Author Search: '{name}'\n"]
    for a in results:
        lines.append(f"**{a.get('name', '')}**")
        if a.get("affiliations"):
            affs = [x.get("name", "") for x in a["affiliations"][:2] if isinstance(x, dict)]
            if affs:
                lines.append(f"  Affiliation: {', '.join(affs)}")
        if a.get("paperCount"):
            lines.append(f"  Papers: {a['paperCount']} | Citations: {a.get('citationCount', 0)} | h-index: {a.get('hIndex', '?')}")
        lines.append("")
    return "\n".join(lines)


def handle_get_related_papers(args: dict) -> str:
    paper_id = args["paper_id"]
    direction = args.get("direction", "both")
    limit = args.get("limit", 10)

    lines = [f"## Related Papers for: {paper_id}\n"]

    if direction in ("backward", "both"):
        refs = s2.get_references(paper_id, limit=limit)
        if refs:
            lines.append(f"### Foundational Sources (cited by this paper) — {len(refs)} papers\n")
            lines.append(_format_paper_list(refs, max_items=limit))

    if direction in ("forward", "both"):
        cits = s2.get_citations(paper_id, limit=limit)
        if cits:
            lines.append(f"### Newer Work (papers citing this) — {len(cits)} papers\n")
            lines.append(_format_paper_list(cits, max_items=limit))

    if len(lines) == 1:
        return f"No related papers found for: {paper_id}"
    return "\n".join(lines)


HANDLERS = {
    "search_papers": handle_search_papers,
    "get_paper_details": handle_get_paper_details,
    "get_citations": handle_get_citations,
    "get_references": handle_get_references,
    "doi_to_bibtex": handle_doi_to_bibtex,
    "search_authors": handle_search_authors,
    "get_related_papers": handle_get_related_papers,
}


# ── MCP server setup ──────────────────────────────────────────────────────────

def run_mcp_server():
    """Run as an MCP server (stdio transport)."""
    if not MCP_AVAILABLE:
        print("ERROR: 'mcp' package not installed. Run: pip install mcp", file=sys.stderr)
        sys.exit(1)

    server = Server("tezatlas-academic")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(**t) for t in TOOLS]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        handler = HANDLERS.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        try:
            # API istemcileri eşzamanlı (urllib); olay döngüsünü kilitlemesin diye iş parçacığında çalışır.
            result = await asyncio.to_thread(handler, arguments)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            return [TextContent(type="text", text=f"Tool error ({name}): {type(e).__name__}: {e}")]

    async def _main() -> None:
        async with stdio_server() as (okuma, yazma):
            await server.run(okuma, yazma, server.create_initialization_options())

    asyncio.run(_main())


# ── Standalone CLI (for testing without MCP) ──────────────────────────────────

def run_cli():
    """Simple CLI for testing API clients without MCP."""
    import argparse
    parser = argparse.ArgumentParser(description="TezAtlas Academic API CLI")
    sub = parser.add_subparsers(dest="tool")

    p_search = sub.add_parser("search", help="Search papers")
    p_search.add_argument("query", nargs="+")
    p_search.add_argument("--limit", type=int, default=5)

    p_doi = sub.add_parser("bibtex", help="DOI to BibTeX")
    p_doi.add_argument("doi")

    p_paper = sub.add_parser("paper", help="Get paper details")
    p_paper.add_argument("identifier")

    p_refs = sub.add_parser("references", help="Get references of a paper")
    p_refs.add_argument("paper_id")

    p_cites = sub.add_parser("citations", help="Get citations of a paper")
    p_cites.add_argument("paper_id")

    p_author = sub.add_parser("author", help="Search author")
    p_author.add_argument("name", nargs="+")

    args = parser.parse_args()

    if args.tool == "search":
        print(handle_search_papers({"query": " ".join(args.query), "limit": args.limit}))
    elif args.tool == "bibtex":
        print(handle_doi_to_bibtex({"doi": args.doi}))
    elif args.tool == "paper":
        print(handle_get_paper_details({"identifier": args.identifier}))
    elif args.tool == "references":
        print(handle_get_references({"paper_id": args.paper_id}))
    elif args.tool == "citations":
        print(handle_get_citations({"paper_id": args.paper_id}))
    elif args.tool == "author":
        print(handle_search_authors({"name": " ".join(args.name)}))
    else:
        parser.print_help()


if __name__ == "__main__":
    # If stdin is a TTY (interactive), run CLI. Otherwise run as MCP server.
    if sys.stdin.isatty():
        run_cli()
    else:
        run_mcp_server()
