# AGENTS.md — TezAtlas

Bu repo TezAtlas'tır: akademik çalışmaları yapay zekâ ajanlarıyla aşama aşama yürütmek için bir çalışma düzeni. Codex ve bu dosyayı okuyan diğer ajanlar için giriş noktasıdır.

1. Oturumun başında `CLAUDE.md` dosyasını oku ve oradaki Demir Kuralları, Soru Protokolünü ve çalışma modlarını uygula. Dosya Claude Code için yazıldı ama kurallar bütün ajanlar için geçerlidir.
2. Kullanıcı bir eğik çizgi komutu yazarsa (ör. `/tezatlas`, `/review-draft giris.md`), `.claude/commands/<komut>.md` dosyasını oku ve oradaki adımları uygula. `$ARGUMENTS` yerine kullanıcının yazdığı argümanı koy.
3. Hafızadan kaynak, DOI, sayfa, yıl ya da alıntı yazma (Demir Kural 4). Künyeleri `tools/bibtex_generator.py` üretir.
4. Tezin ana iddiası, veri yorumu ve sonuçlar yazarındır; bunları üretme.
5. Taslağı denetletmek için kendi şirketinin modelini değil, başka bir şirketin modelini kullan: `docs/coklu-model.md`.
6. Kod değişikliğinden sonra: `ruff check .`, `pytest -q`, `python3 scripts/check_links.py`.
