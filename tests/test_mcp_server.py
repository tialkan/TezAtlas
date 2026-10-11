"""MCP sunucusu duman testi: süreç açılır, el sıkışır, araç listesini döndürür (ağa çıkmaz)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("mcp")

SERVER = Path(__file__).resolve().parent.parent / "mcp_server" / "server.py"


def _mesaj(obj: dict) -> bytes:
    return (json.dumps(obj) + "\n").encode()


def test_server_lists_tools() -> None:
    istekler = b"".join([
        _mesaj({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}}),
        _mesaj({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        _mesaj({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ])
    p = subprocess.run([sys.executable, str(SERVER)], input=istekler, capture_output=True, timeout=30)
    yanitlar = [json.loads(s) for s in p.stdout.decode().splitlines() if s.strip()]
    liste = next(y for y in yanitlar if y.get("id") == 2)
    adlar = {t["name"] for t in liste["result"]["tools"]}
    assert {"search_papers", "doi_to_bibtex", "get_citations", "get_references"} <= adlar
