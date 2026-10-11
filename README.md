<div align="center">

# TezAtlas

### Yapay zekâ ajanlarıyla aşama aşama akademik yazım

*[tezatlas.com/makale](https://tezatlas.com/makale)*

[![Lisans: MIT](https://img.shields.io/badge/Lisans-MIT-yellow.svg)](LICENSE)
[![Diller](https://img.shields.io/badge/Diller-TR%20·%20EN-blue)]()
[![Sürüm](https://img.shields.io/badge/sürüm-1.3.0-informational)](CHANGELOG.md)
[![CI](https://github.com/tialkan/TezAtlas/actions/workflows/ci.yml/badge.svg)](https://github.com/tialkan/TezAtlas/actions/workflows/ci.yml)

![TezAtlas ekran görüntüsü](assets/screenshot.png)

</div>

TezAtlas, tez, makale, bildiri ve proje önerisi gibi akademik çalışmaları yapay zekâ ajanlarıyla (Claude Code ve benzerleri) aşama aşama yürütmek için hazırlanmış açık kaynak bir çalışma düzenidir. Sohbet botu değildir; konunun belirlenmesinden savunmaya kadar her aşamanın neyle başlayıp neyle biteceğini, hangi kontrollerden geçileceğini tanımlar.

Temel ilke: **kaynağı diskte olmayan hiçbir cümle yazılmaz, hiçbir atıf uydurulmaz.** Yapay zekâ taslak seçenekleri önerebilir, ama tezin ana iddiası, veri yorumu ve sonuçlar her zaman yazara aittir.

> İngilizce ayrıntılı başvuru belgesi: [docs/README.en.md](docs/README.en.md)

## Kimler için?

- Tez yazan yüksek lisans ve doktora öğrencileri
- Makale, bildiri, kitap bölümü veya proje önerisi hazırlayan akademisyenler
- Yapay zekâyı kullanmak isteyen ama uydurma kaynak riskinden çekinen herkes

## Neler yapar?

| Belge türü | Aşama sayısı | İlk düğüm |
|---|---|---|
| Doktora / yüksek lisans tezi | 9 | `skills/phases/thesis/` |
| Dergi makalesi | 9 | `skills/phases/article/` |
| Konferans bildirisi | 7 | `skills/phases/conference/` |
| Literatür / sistematik derleme | 6 | `skills/phases/lit-review/` |
| Araştırma raporu | 6 | `skills/phases/report/` |
| Kitap bölümü | 6 | `skills/phases/book-chapter/` |
| Hibe teklifi | 6 | `skills/phases/grant-proposal/` |
| Araştırma önerisi | 5 | `skills/phases/research-proposal/` |
| Akademik poster | 3 | `skills/phases/poster/` |
| Teknik rapor | 3 | `skills/phases/technical-report/` |

Her aşama bir "kapı" ile biter: örneğin okuma doygunluğa ulaşmadan yazıma geçilmez. Kapılarda yapay zekâ hakem incelemesi ya da danışman kontrolü yapılır.

## Kullanmanın üç yolu

| Yol | Kimin için | Maliyet |
|---|---|---|
| **1. Claude Code ile** (önerilen) | Terminal açabilen herkes; aşağıdaki adımlar yeterli | Claude aboneliği (Pro veya üstü) ya da Anthropic API kullanımı |
| **2. Başka bir yapay zekâ ajanıyla** (Codex, Gemini CLI vb.) | Başka bir aboneliği olanlar; `AGENTS.md` / `GEMINI.md` kuralları yükler | İlgili aboneliğin ücreti |
| **3. tezatlas.com üzerinden** | Hiç kurulum istemeyenler | Ücretsiz. [Denetle](https://tezatlas.com/denetle) çalışıyor; model ücreti kendi OpenRouter hesabınızdan düşer. Tam iş akışı planlanıyor ([fizibilite](docs/saas-fizibilite.md)) |

Abonelik ücretleri ve kapsamları sık değişir; güncel bilgiyi sağlayıcının sitesinden kontrol edin.

## Kurulum (Claude Code ile, yaklaşık 10 dakika)

Terminal hiç kullanmadıysanız: macOS'ta **Terminal** uygulamasını, Windows'ta **PowerShell**'i açın. Aşağıdaki satırları sırayla kopyalayıp yapıştırın.

1. **Claude Code'u kurun.** Kurulum talimatı: [docs.claude.com/claude-code](https://docs.claude.com/en/docs/claude-code/overview). İlk açılışta Claude hesabınızla giriş yaparsınız.
2. **TezAtlas'ı indirin.**
   ```bash
   git clone https://github.com/tialkan/TezAtlas.git
   cd TezAtlas
   ```
   `git` yüklü değilse GitHub sayfasındaki **Code → Download ZIP** ile indirip klasöre girebilirsiniz.
3. **Başlatın.**
   ```bash
   claude
   ```
   Açılan ekranda şunu yazın:
   ```
   /tezatlas
   ```
4. **Soruları yanıtlayın.** TezAtlas belge türünü, yazım dilini, alanınızı ve çalışma modunu sorar. Her soruda önerilen seçenek ilk sıradadır; "sen karar ver" derseniz öneri seçilir.
5. **Kaynaklarınızı ekleyin.** PDF'leri `sources/` klasörüne koyun. Taranmış PDF'ler için OCR aşağıda.

Bir sonraki oturumda yine `claude` ve `/tezatlas` yazmanız yeterli; TezAtlas `STATUS.md` dosyasından kaldığınız yeri bulur.

### İsteğe bağlı: Python araçları

Kaynakça üretimi, OCR, çoklu model ajanları ve komut satırı araçları için Python 3.11 veya üstü gerekir.

```bash
python3 -m pip install -e ".[all]"
tezatlas --list
```

Taranmış PDF'ler için Tesseract da gerekir: macOS'ta `brew install tesseract tesseract-lang`, Ubuntu'da `sudo apt install tesseract-ocr tesseract-ocr-tur`, Windows'ta [UB Mannheim kurulumu](https://github.com/UB-Mannheim/tesseract/wiki).

```bash
python3 ocr_pipeline.py sources/ --batch --lang tur+eng
```

## Demir Kurallar

Her oturumda, her belge türünde geçerlidir.

1. `sources/` klasöründe kaynağı olmayan hiçbir şey yazılmaz.
2. Kartopu örnekleme zorunludur: dipnotlar ve kaynakçalar izlenir.
3. Yapay zekâ kaynağı önce kendisi, yasal kanallardan bulmaya çalışır; bulamazsa sorar ([yasal edinme zinciri](skills/tooling/open-access-chain.md)).
4. Atıf asla uydurulmaz.
5. Aşama geçişlerinden önce yapay zekâ hakem incelemesi veya danışman kontrolü yapılır.
6. Her oturumun sonunda git commit'i atılır.
7. İlerleme durursa engel hemen bildirilir.
8. Okuma aşaması biterken her argüman için en güçlü destek ve en güçlü karşı görüş yazılır.
9. Yazıma başlamadan bekleyen kaynak havuzu gözden geçirilir.

Ayrıntı: [skills/core/iron-rules.md](skills/core/iron-rules.md)

## Birden fazla model: biri yazar, öteki denetler

Aynı modelin kendi hatasını yakalaması zordur. TezAtlas bu yüzden ikinci bir modeli denetçi olarak kullanmayı önerir. `agents/` klasöründeki üç ajan (kaynak avcısı, yöntem denetçisi, atıf doğrulayıcı) varsayılan olarak farklı sağlayıcıların modellerine atanmıştır.

En kolay yol tek bir [OpenRouter](https://openrouter.ai/keys) anahtarıdır:

```bash
cp .env.example .env          # .env içine OPENROUTER_API_KEY=... yazın
tezatlas-agents --list-providers
tezatlas-agents capraz_denetim --input bolumler/giris.md   # iki model, bulgular yan yana
```

Claude Code içinde aynı işi `/cross-review bolumler/giris.md` yapar. Kurulum istemiyorsanız aynı denetimi tarayıcıda [tezatlas.com/denetle](https://tezatlas.com/denetle) adresinde, kaynak PDF'lerinizle ve kendi OpenRouter anahtarınızla yapabilirsiniz; site hiçbir şey saklamaz. Bir bölümün çapraz denetimi yaklaşık 0,15 USD tutar; rolleri, maliyet tablosunu, Codex ve Gemini CLI tariflerini ve API'siz (iki abonelikle) yolu [docs/coklu-model.md](docs/coklu-model.md) anlatır.

Model adları `agents.yaml` dosyasında durur ve sık değişir; `.env` içinde `OPENROUTER_MODEL=...` gibi satırlarla değiştirilebilir. `.env` dosyası git'e eklenmez.

## Sık kullanılan komutlar

| Komut | Ne yapar |
|---|---|
| `/tezatlas` | Yeni proje başlatır ya da kaldığı yerden sürdürür |
| `/status` | Projenin durumunu gösterir |
| `/review-draft <dosya>` | Taslağı argüman, kaynak, üslup ve literatür açısından inceler |
| `/cross-review <dosya>` | Taslağı başka şirketlerin modelleriyle kör denetletir, bulguları yan yana koyar |
| `/citation-check "<iddia>" <kaynak.pdf>` | Bir iddianın kaynakta geçip geçmediğini denetler |
| `/generate-citations` | Kaynak PDF'lerindeki DOI'lerden Crossref/OpenAlex ile BibTeX üretir (sonucu kontrol edin) |
| `/synthesize`, `/gaps`, `/contradictions` | Kaynaklar arası sentez, boşluk ve çelişki raporları |
| `/latex`, `/compile-pdf`, `/submission-check` | LaTeX'e dönüştürme, PDF ve teslim öncesi kontrol |

Tüm komutlar: [CLAUDE.md](CLAUDE.md)

## Yapay zekâ kullanımı ve etik

- Kurumunuz veya dergi istiyorsa yapay zekâ kullanımını beyan edin. Yapay zekâ yazar olamaz; içerik ve atıfların sorumluluğu yazardadır.
- Yapay zekâ dedektörü puanı bir kalite ölçütü değildir; TezAtlas "tespit edilemez metin" vaat etmez.
- Kaynaklar yalnız yasal kanallardan edinilir. Gölge kütüphaneler varsayılan kurulumda yoktur; isteğe bağlı eklenti olarak ayrı tutulur ([eklentiler/golge-kutuphane](eklentiler/golge-kutuphane/README.md)).
- Yapay zekâyla düzelti için kopyalanabilir yazım kuralları: [tezatlas.com/makale](https://tezatlas.com/makale)

## Sınırlar

TezAtlas güçlü önlemler alır ama yanılmaz değildir. Otomatik araçlar bir künyeyi yanlış esere bağlayabilir, bir modelin "doğrulandı" notu hatalı olabilir. Teslimden önce her atıfı kendiniz kontrol edin. Kurum kuralları (enstitü kılavuzları, TR Dizin, ÜAK) değişir; güncel belgeden doğrulayın.

## Proje yapısı

```
skills/        Aşama, teknik, şablon ve kural düğümleri (Claude Code bunları okur)
.claude/       Claude Code komutları
agents/        Çoklu model ajanları ve agents.yaml yapılandırması
scripts/       Kaynak bulma, okuma takibi, sentez vb. Python betikleri
tools/         BibTeX üretici, LaTeX dönüştürücü, üslup denetçisi
mcp_server/    Semantic Scholar, OpenAlex ve Crossref için MCP sunucusu
eklentiler/    İsteğe bağlı eklentiler
docs/          Ayrıntılı belgeler ve incelemeler
tests/         Testler (pytest)
```

## Katkı

Katkı kuralları: [CONTRIBUTING.md](CONTRIBUTING.md). Değişiklik geçmişi: [CHANGELOG.md](CHANGELOG.md). Tasarımın dayandığı araştırmalar: [RESEARCH_BACKING.md](RESEARCH_BACKING.md).

Geliştiriciler için:

```bash
python3 -m pip install -e ".[all]"
ruff check .
pytest -q
python3 scripts/check_links.py
```

## Lisans

MIT © Tarık İsmet ALKAN
