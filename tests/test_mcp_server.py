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
    # İstekler sırayla gönderilir ve her yanıt beklenir; girdi hemen kapanırsa sunucu
    # son isteği yanıtlamadan çıkabiliyor (yük altında yarış durumu).
    p = subprocess.Popen([sys.executable, str(SERVER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    try:
        def gonder(obj: dict) -> None:
            p.stdin.write(_mesaj(obj))
            p.stdin.flush()

        def bekle(kimlik: int) -> dict:
            while True:
                satir = p.stdout.readline()
                assert satir, "sunucu yanıt vermeden kapandı"
                y = json.loads(satir)
                if y.get("id") == kimlik:
                    return y

        gonder({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}})
        bekle(1)
        gonder({"jsonrpc": "2.0", "method": "notifications/initialized"})
        gonder({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        liste = bekle(2)
    finally:
        p.kill()
        p.wait(timeout=10)
    adlar = {t["name"] for t in liste["result"]["tools"]}
    assert {"search_papers", "doi_to_bibtex", "get_citations", "get_references"} <= adlar
