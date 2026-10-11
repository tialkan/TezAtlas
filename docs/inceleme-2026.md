# TezAtlas framework incelemesi (Ekim 2026)

İnceleme tarihi: 11 Ekim 2026. İncelenen sürüm: `c6be3f4` (26 Eylül 2026). Bu aşamada repoda kod değiştirilmedi; yalnız bu rapor eklendi.

Yöntem: depo baştan sona okundu, testler çalıştırıldı (266 test, hepsi geçti), ruff ile tarandı, iç bağlantılar bir betikle denetlendi, `pip install` ve MCP sunucusu denendi. Web arama aracı bu oturumda kapalı olduğu için güncel model adları, fiyatlar ve kurum kuralları resmî kaynaktan denetlenemedi; bu maddeler "doğrulanmadı" diye işaretli.

## Kısa sonuç

Fikir ve içerik güçlü: faz kapıları, Türkçe ve kurum desteği, "uydurma atıf yok" ilkesi, öz-düzenleme pedagojisi. Ancak üç ciddi sorun var:

1. **Kurulum ve MCP sunucusu çalışmıyor.** `pip install -e .` hata veriyor; MCP sunucusu hiçbir güncel `mcp` sürümünde açılmıyor.
2. **Projenin temel ilkesi kodda delinebiliyor.** BibTeX üreticisi ve kaynak avcısı ajanı, doğrulanmış görünen ama yanlış eserlere ait künyeler üretebiliyor. `RESEARCH_BACKING.md` içinde hatalı künyeler var.
3. **Belgeler kodla uyuşmuyor.** README'deki sayılar, Python sürümü ve dosya yolları yanlış. Bazı belge türleri ilk adımda var olmayan dosyaya yönleniyor.

Hepsi düzeltilebilir. Hızlı kazanımların çoğu birkaç saatlik iş.

## 1. Mimari harita

| Katman | Yer | Sayı |
|---|---|---|
| Faz düğümleri | `skills/phases/<tür>/` | 60 dosya, 10 belge türü (tez 9, makale 9, bildiri 7, rapor 6, kitap bölümü 6, hibe 6, literatür taraması 6, araştırma önerisi 5, poster 3, teknik rapor 3) |
| Çekirdek kurallar ve modlar | `skills/core/` | 37 |
| Teknikler | `skills/techniques/` | 35 |
| Şablonlar | `skills/templates/` | 30 (17 `tpl-*`, 6 atıf stili, 6 disiplin, 1 üniversite) |
| Araç rehberleri | `skills/tooling/` | 10 |
| Gezinme haritaları (MOC) | `skills/moc/` | 6 |
| Mimari notlar | `skills/architecture/` | 8 |
| Disiplin | `skills/disciplines/` | 2 (`law`, `yok-compliance`) |
| Claude Code komutları | `.claude/commands/` | 21 |
| Python betikleri | `scripts/` | 24 |
| LLM ajanları | `agents/` + `agents.yaml` | 3 ajan: kaynak avcısı, metodoloji denetçisi, atıf doğrulayıcı |
| Çekirdek Python | `core/` | faz kapısı, oturum, pano, literatür zekâsı |
| Araçlar | `tools/` | BibTeX üretici, LaTeX dönüştürücü, üslup denetçisi |
| MCP sunucusu | `mcp_server/` | Semantic Scholar, OpenAlex, Crossref |
| Eski tanıtım sitesi | `website/` | Next.js, canlı siteyle ilgisi yok |

Düğümler iki yolla bağlanıyor: frontmatter (`links_to`, `used_by`, `phase_gate_in/out`) ve gövde içinde `[[wikilink]]`.

Kullanıcı yolculuğu:

1. `claude` açılır, `/tezatlas` yazılır.
2. `STATUS.md` varsa oturum kaldığı yerden sürer (`session_start.py`, pano, araç önerisi).
3. Yoksa `core/onboarding.md`: dil, belge türü, kullanıcı tipi, çalışma modu. Ardından türün `phase-0` dosyasına geçilir.
4. Fazlar `phase_gate_out` zinciriyle ilerler; her geçişte yapay zekâ hakem incelemesi veya danışman kontrolü var.
5. Son adım: `/latex`, `/compile-pdf`, `/submission-check`.

## 2. Güncellik

| Bulgu | Yer | Durum |
|---|---|---|
| Model adları eski: `gemini-2.0-flash`, `gpt-4o`, `claude-sonnet-4-20250514`, `grok-3`, `llama-3.3-70b-versatile`, `llama3.2` | `agents.yaml:9-39`, `README.md:385-391` | Kesin. Hangilerinin kullanımdan kalktığı doğrulanmadı. |
| README "Python 3.8+" diyor; `pyproject.toml` 3.11 istiyor, kod 3.10+ sözdizimi kullanıyor | `README.md:136,371`, `pyproject.toml:10` | Kesin |
| README "API anahtarı gerekmez" diyor; ajanlar `.env` istiyor | `README.md:129` | Kesin |
| README "~130 düğüm", "30 teknik", "5 disiplin modülü" diyor; gerçekte 192 düğüm, 35 teknik, disiplinler üç ayrı klasöre dağılmış | `README.md:495` vd. | Kesin |
| Var olmayan betiklere atıf: `scripts/annas_archive_helper.sh`, `scripts/export.sh`, `scripts/export_career_data.py`; var olmayan komutlar: `/mode`, `tez-baslat`, `thesis-start` | `tooling/annas-archive.md:29-35`, `phases/thesis/phase-7-finalization.md:181`, `core/context-management.md:16-17` vd. | Kesin |
| Bağımlılıkların hepsi yalnız alt sınırlı (`>=`), kilit dosyası yok. `mcp` 2.x çıkınca sunucu kırılmış. | `pyproject.toml` | Kesin |
| `website/` Next.js 16.1.6 ile kurulmuş, `npm ci` kilit dosyası uyumsuzluğu yüzünden düşüyor | `website/` | Kesin |
| "YÖK standardı" denilen tez biçim kuralları. YÖK'ün ulusal bir biçim kılavuzu yok bilgisi; değerler enstitü kılavuzlarından geliyor gibi. | `skills/disciplines/yok-compliance.md` | Doğrulanmadı |
| "ULAKBİM Sosyal Bilimler", "YÖK ESBD puanlaması", "TÜBİTAK 1001/1003 Q1-Q2 zorunluluğu" ifadeleri | `techniques/publication-strategist.md:152-157` | Doğrulanmadı, kaynaksız |
| Doçentlik kriterleri, TR Dizin etik kurul tarihi (Aralık 2019) | `techniques/journal-selection.md:94-96`, `core/research-ethics.md:74,268` | Güncel ÜAK ve TR Dizin belgesinden doğrulanmalı |
| YÖK'ün üretken yapay zekâ etik rehberine ve yapay zekâ kullanım beyanına hiç değinilmiyor | tüm `skills/` | Kesin (eksik) |

## 3. Kalite

### Kaynak uydurma riski (en yüksek öncelik)

1. **`tools/bibtex_generator.py:342-356`:** PDF'in ilk üç sayfasında bulunan ilk DOI kabul ediliyor. Crossref'ten gelen başlık PDF metniyle karşılaştırılmıyor. İlk sayfalarda başka eserlerin DOI'si sık geçtiği için PDF'e yanlış makalenin künyesi bağlanabilir.
2. **`tools/bibtex_generator.py:360-371`:** PDF'ten tahmin edilen başlıkla OpenAlex'te tek sonuçlu arama yapılıyor ve sonuç benzerlik denetimi olmadan kabul ediliyor. Gerçek ama yanlış bir eserin temiz görünen künyesi çıkabilir.
3. **`agents/prompts/source_hunter.md:49`:** Ajan, kaynakları modelin hafızasından öneriyor; önerilen DOI ve başlıklar hiçbir API ile doğrulanmıyor. `phases/*/phase-2-sources.md:127-139` bu çıktıyı doğrudan kullanıcıya gösteriyor.
4. **`skills/tooling/reference-managers.md:41-42`:** `.bib` dosyasını doğrulanmış üretici yerine modelin yazması öneriliyor.
5. **`skills/techniques/publication-strategist.md:62-80`:** Dergi etki faktörleri hafızadan veriliyor.
6. **`agents/citation_verifier.py:58-71`:** PDF'in yalnız ilk 50.000 karakteri gönderiliyor. İddia sonraki sayfalardaysa "desteklemiyor" gibi yanlış sonuç çıkabilir ve kullanıcı uyarılmıyor.
7. **`RESEARCH_BACKING.md`:** Hiçbir künyede DOI yok. Aşağıdakiler hatalı görünüyor (bilgiye dayalı tespit; Crossref ile doğrulanmadı):
   - Lovitts (2001) için verilen kitap başlığı tanınmıyor; bilinen eseri *Leaving the Ivory Tower* (Rowman & Littlefield).
   - Pychyl ve Flett (2012), *Personality and Individual Differences* 53(7): bu künye muhtemelen yanlış.
   - Flower ve Hayes (1981): dergi *College Composition and Communication* 32(4) olmalı; dosyada *College English* 44(4) yazıyor.
   - Wisker (2005): yayınevi Palgrave Macmillan olmalı.
   - Bereiter ve Scardamalia iki kez geçiyor (satır 44 ve 94).

   "Uydurma atıf yok" diyen bir projede bu dosya güven kaybına yol açar; ilk düzeltilmesi gereken yer burası.

İyi taraflar: `iron-rules.md:61` ve `source-policy.md:30` hafızadan kaynak üretimini yasaklıyor; `/generate-citations` komutu yalnız Crossref ve OpenAlex verisi kullanacak biçimde kurulmuş.

### Çelişen talimatlar

- Varsayılan çalışma modu dört dosyada farklı anlatılıyor. `core/modes.md:21` "Düşünce Ortağı varsayılan, taslak üretimi kilitli" diyor; `core/operating-modes.md`, `core/user-modes.md` ve `CLAUDE.md` "Araştırma Yardımcısı varsayılan, kilit yok" diyor.
- `/review-draft`: `INDEX.md:14` "3 katman", `CLAUDE.md:82` "4 katman".
- Kaynaksız yazım: `core/guided-writing-mode.md:118-120` yazımı durduruyor; `techniques/drafting-alternatives.md:106` yalnız işaretleyip izin veriyor.
- Dosya adları karışık: `READING_REPORT` 12 dosyada, `OKUMA_RAPORU` 10 dosyada; `notes/` 21, `notlar/` 8 dosyada.
- Demir Kural 8 ve 9, tezin faz numaralarını kullanıyor (`iron-rules.md:113,131`). Makale gibi faz sayısı farklı türlerde yanlış faza denk geliyor.
- Slogan ("AI writes. You guide.") ile "yapay zekâ asla temel argüman üretmez" kuralı çelişiyor.

### Kırık bağlantılar

| Tür | Toplam | Kırık |
|---|---|---|
| `[[wikilink]]` | 238 | 0 |
| Göreli markdown bağlantısı | 10 | 0 |
| `links_to`, `phase_gate_*` | 619 | 0 |
| `used_by` | 160 | 47 (çoğu `thesis/` alt klasörünü atlayan yollar) |

Metin içinde yaklaşık 41 yol diskte yok. En kritikleri:

- `core/onboarding.md:288-289` hibe ve araştırma önerisi türlerini var olmayan `phase-0-brief.md` ve `phase-0-prospectus.md` dosyalarına yönlendiriyor; bu iki tür ilk adımda kırılıyor.
- Poster ve teknik rapor yönlendirme tablosunda hiç yok; bu türlere ulaşılamıyor.
- `templates/universities/*.yaml` (ODTÜ, İTÜ, Boğaziçi, Hacettepe, Ankara, ASBÜ, örnek) yok; `MOC-universities.md` ve tez `phase-0-identity.md:98` bunlara dayanıyor.
- Onboarding'in Türkçe bölümünde yönlendirme tablosu yok.
- 19 düğüme hiçbir yerden bağlantı yok (ör. `core/orchestrator.md`, `techniques/citation-graph.md`, `tooling/statistics.md`).

### Kod kalitesi

- 266 test geçiyor, ama CI 18 test dosyasından yalnız 6'sını çalıştırıyor; lint adımı yok; MCP sunucusunun testi yok.
- ruff: varsayılan kurallarla 236 bulgu; yalnız hata sınıfında 25 bulgu (kullanılmayan importlar, `scripts/synthesize.py:407` aynı fonksiyonun iki tanımı, kullanılmayan değişkenler).
- `scripts/find_source.py:452-480`, `agents/run.py`'ye var olmayan `--top` ve `--provider` argümanlarını geçiyor. LLM ile sorgu genişletme hiç çalışmamış; hata sessizce yutuluyor.
- Anthropic sağlayıcısı: `max_tokens=4096` sabit, birden fazla sistem mesajında yalnız sonuncusu kalıyor (`agents/providers/anthropic.py:33-38`). `agents.yaml` içindeki `timeout` ve `max_retries` hiçbir yerde okunmuyor.
- `agents/config.py:98` her hatayı yutup sessizce yedek sağlayıcıya geçiyor.
- Akademik API istemcisi: polite pool e-postası `tezatlas@example.com` olarak sabit; 429 için yeniden deneme yok; hız sınırı hataları "sonuç bulunamadı" diye gösteriliyor (`mcp_server/api_clients.py:21,81,255,352-371`).
- BibTeX alanlarında `&`, `%`, `_` kaçışlanmıyor; anahtarlar ASCII değil (`Öz2020`); aynı yazar-yıl çakışmasında anahtar tekrarlanıyor.
- Token ve maliyet kaydı hiç yok.

### Güvenlik ve hukuk

- **`.claude/settings.local.json` repoya commit edilmiş.** İçinde yerel kullanıcı yolu ve `git push origin main` dahil geniş izinler var. Repodan çıkarılmalı ve `.gitignore`'a eklenmeli.
- Anna's Archive ve Sci-Hub, kaynak bulma zincirinin birincil kanalı olarak sunuluyor (`iron-rules.md:53`, `techniques/source-hunting.md:25`, `phase-1-topic.md:88`, `sources/README.md`). Demir Kural 3 ("yapay zekâ önce indirir") ile birleşince telif ve kurum politikası riski doğuyor. Üniversitelerde önerilecek bir araç için varsayılan sıra açık erişim (Unpaywall, OpenAlex), kurum erişimi, kütüphaneler arası ödünç, yazardan isteme olmalı.
- `techniques/natural-voice.md` dedektör ölçütlerini (perplexity, burstiness) hedefliyor, ama yapay zekâ kullanım beyanı politikasına bağlı değil.
- `website/` içinde doğrulanamayan "kullanıcı yorumları" ve "0 uydurma atıf" istatistiği var.
- Kabuk komutu enjeksiyonu yok; tüm `subprocess` çağrıları liste argümanıyla yapılıyor. `.env` korunuyor.

## 4. Kullanılabilirlik

README 1.222 satır ve büyük ölçüde İngilizce; kurulum 109. satırda başlıyor. Hiç terminal kullanmamış bir akademisyen şu noktalarda takılır:

1. `git clone` ve `claude` komutlarının ne olduğu, Claude Code'un ücretli abonelik gerektirdiği anlatılmıyor.
2. Ajanlar için `.env` kopyalama, `pip install` ve API anahtarı gerekiyor; `pip install -e .` ise `pyproject.toml:3` içindeki hatalı `build-backend` yüzünden hiç çalışmıyor. Devcontainer da aynı nedenle kırık.
3. `core` paketi, `ocr_pipeline.py` ve `tezatlas_cli.py` pakete dahil değil; `tezatlas-ocr` komutu kurulumdan sonra kırık, `tezatlas` komutu hiç tanımlı değil.
4. OCR için yalnız Linux (`apt`) talimatı var; Windows ve macOS yok.
5. Hatalar ham Python hatası olarak görünüyor. API anahtarı yoksa ajan `"not-needed"` anahtarıyla istek atıp 401 hatasıyla düşüyor; PDF yoksa `FileNotFoundError` çıkıyor.
6. MCP sunucusu `mcp` 1.30'da `ValueError`, 2.3'te `AttributeError` veriyor (`mcp_server/server.py:360,376`). CLAUDE.md'de anlatılan MCP entegrasyonu fiilen çalışmıyor.

Gerçekçi kurulum adım sayısı bugün: Claude Code yolu için 3 adım (iyi), ajan yolu için 6–8 adım ve bir kurulum hatası.

## 5. Eksikler ve benzer araçlar

Aşağıdaki karşılaştırma bilgiye dayalıdır; web erişimi olmadığı için güncel sürümleri doğrulanmadı.

| Araç | TezAtlas'ta olmayan |
|---|---|
| PaperQA2 (FutureHouse) | Pasaj düzeyinde atıf doğrulama, ölçülmüş doğruluk |
| STORM / Co-STORM (Stanford) | Çok bakış açılı soru-cevapla atıflı rapor |
| OpenScholar (AI2) | Açık bilimsel külliyat üzerinde değerlendirilmiş sentez |
| ASReview | Sistematik derleme taramasında aktif öğrenme |
| Zotero + Better BibTeX | Canlı kütüphane senkronizasyonu |
| Connected Papers, ResearchRabbit, Litmaps | Görsel atıf ağı |
| Elicit, SciSpace (kapalı) | Tablo hâlinde veri çıkarımı, web arayüzü |

TezAtlas'ın farkı: faz kapıları, Türkçe ve kurum desteği, öğretici yaklaşım. Ortak eksikler: web arayüzü, gömme tabanlı arama (`core/literature_intel.py` yalnız anahtar sözcük eşleştiriyor), ölçülmüş atıf doğrulama, Zotero senkronizasyonu, maliyet görünürlüğü, ikinci model denetimi.

`DEVELOPMENT_PROPOSALS.md` içindeki 77 önerinin 77'si "Done" işaretli; ama "Done" çoğu zaman yalnız bir markdown düğümü yazıldığı anlamına geliyor (ör. #29 Zotero için kod yok, #50 ortak çalışma alanı için düğüm bile yok).

## 6. Öncelikli iş listesi

Emek: K (birkaç saat), O (1–3 gün), B (bir hafta ve üstü).

### Hızlı kazanımlar (yüksek etki, küçük emek)

| # | İş | Etki | Emek |
|---|---|---|---|
| 1 | `.claude/settings.local.json`'u repodan çıkar, `.gitignore`'a ekle | Güvenlik | K |
| 2 | `RESEARCH_BACKING.md` künyelerini Crossref ile düzelt, DOI ekle, tekrarı sil | Güvenilirlik | K |
| 3 | `pyproject.toml` düzeltmesi: `build-backend`, `core` ve tek dosyalık modüller pakete, `tezatlas` komutu; CI'da tüm testler ve ruff | Kurulum | K |
| 4 | Onboarding yönlendirme tablosu: hibe ve öneri yolları, poster ve teknik rapor, Türkçe tablo | Akış kırığı | K |
| 5 | README'deki sayıları, Python sürümünü ve "API anahtarı gerekmez" ifadesini düzelt; 47 kırık `used_by` yolunu toplu düzelt; CI'a bağlantı denetimi ekle | Güven, bakım | K |
| 6 | `website/` klasörünü ve CI dosyasını kaldır | Sadelik | K |
| 7 | Model adlarını yapılandırmaya taşı, `--model` seçeneği, `timeout`/`max_retries`/`max_tokens` gerçekten uygulansın | Güncellik | K |

### Orta vadeli (yüksek etki, orta emek)

| # | İş | Etki | Emek |
|---|---|---|---|
| 8 | BibTeX üreticisine doğrulama kapısı: Crossref/OpenAlex başlığı PDF metniyle bulanık eşleşmeli; eşleşmezse `% DOĞRULANMADI` ve `@misc`. LaTeX kaçışlama, ASCII ve tekil anahtar. | Uydurma riski | O |
| 9 | Kaynak avcısını API'ye bağla: önce OpenAlex/Crossref araması, model yalnız sıralasın; her DOI doğrulansın | Uydurma riski | O |
| 10 | MCP sunucusunu güncel SDK ile yeniden yaz, sürümü sınırla, duman testi ekle | İşlevsellik | O |
| 11 | Akademik API istemcisi: yapılandırılabilir e-posta, 429 için geri çekilme, görünür hatalar | Sağlamlık | O |
| 12 | Mod dosyalarını tek kanonik dosyada birleştir; dosya adlarını standartlaştır; Demir Kural 8-9'u faz numarasına değil faz rolüne bağla | Tutarlılık | O |
| 13 | Gölge kütüphaneleri varsayılan zincirden çıkar; açık erişim öncelikli zincir | Hukuk, kurum kabulü | O |
| 14 | Yapay zekâ kullanım beyanı şablonu ve politika düğümü; `natural-voice.md`'yi buna bağla; sitedeki yazım master prompt'unu framework'e ekle | Etik | O |
| 15 | Token ve maliyet kaydı (JSONL); "yazar" ve "denetçi" rolleri (Aşama 3'ün temeli) | Çoklu LLM, SaaS | O |
| 16 | Kullanıcı dostu hata mesajları; README'yi 200 satırlık Türkçe/İngilizce girişe indir, ayrıntıları `docs/`'a taşı; Windows/macOS kurulum | Kullanılabilirlik | O |

### Büyük işler

| # | İş | Etki | Emek |
|---|---|---|---|
| 17 | Kurum kurallarını kaynak ve son doğrulama tarihiyle yeniden yaz; üniversite YAML dosyalarını oluştur ya da kaldır | Doğruluk | B |
| 18 | Pasaj düzeyinde atıf doğrulayıcı ve ölçülmüş hata oranı (küçük bir değerlendirme seti) | Ana ilkenin kodda karşılığı | B |
| 19 | Zotero senkronizasyonu, gömme tabanlı arama | Rekabet | B |
| 20 | Her faz için dosya sözleşmesi (girdi/çıktı şeması); SaaS'ın temeli | SaaS | B |

## Karar vermen gereken konular

1. Hızlı kazanımların (1–7) hepsini uygulayayım mı?
2. Anna's Archive ve Sci-Hub: tamamen kaldırılsın mı, yoksa varsayılan zincir dışında isteğe bağlı bir eklentiye mi taşınsın?
3. `website/` klasörü silinsin mi?
4. README'nin ana dili Türkçe mi olsun, İngilizce mi (diğeri ayrı dosyada)?
5. Kurum kurallarını (YÖK, TR Dizin, ÜAK, TÜBİTAK) doğrulamak için web erişimi gerekiyor. Bu oturumda arama kapalı; ya sen bağlantıları verirsin ya da bu maddeler "doğrulanmadı" notuyla kalır.
