# Birden fazla modelle çalışmak: biri yazar, öteki denetler

Bir dil modeli kendi yazdığı metindeki hatayı çoğu zaman göremez: kendi uydurduğu kaynağı "doğru" bulur, kendi abarttığı iddiayı makul sayar. TezAtlas bu yüzden taslağı yazan modelden **farklı bir şirketin** modelini denetçi olarak kullanmayı önerir. Denetçi yazarın gerekçelerini görmez; yalnız taslağa ve sizin kaynak notlarınıza bakar. İki model aynı sorunu bulursa sorun büyük olasılıkla gerçektir. Yalnız birinin bulduğu sorunda karar sizindir.

## Roller

| Rol | Ne yapar | Uygun model sınıfı | Neden |
|---|---|---|---|
| **Yazar** | Rehberli Yazım modunda taslak seçenekleri üretir (Claude Code, Codex ya da Gemini CLI içinde) | Güçlü akıl yürütme, uzun bağlam | Kaynak notlarının tamamını aklında tutup tutarlı metin kurması gerekir |
| **Denetçi** | Kaynak-iddia uyumu, uydurma şüphesi, iddia gücü, bağlam kayması, mantık boşluğu, yapay zekâ kalıpları | Yazardan farklı şirket; güçlü akıl yürütme | Bağımsızlık asıl değerdir; aynı şirketin modelleri benzer hatalar yapar |
| **İkinci denetçi** (çapraz denetim) | Aynı denetimi başka bir modelle yapar; bulgular yan yana konur | Ucuz ve hızlı model yeterli | Ortak bulguları doğrulamak için; pahalı olması gerekmez |
| **Hakem** (isteğe bağlı) | Dergi hakemi gözüyle katkı, literatür, yöntem, yapı | Uzun bağlam, orta fiyat | Göndermeden önce bir prova |
| **Kaynak avcısı** | Kaynak önerir; her öneri Crossref ile doğrulanır | Ucuz ve hızlı | Doğrulama kodda yapıldığı için modelin pahalı olması gerekmez |

**Kural:** Claude Code ile yazıyorsanız denetçi Claude olmasın; Codex ile yazıyorsanız GPT olmasın.

Hiçbir rol tezin ana iddiasını, veri yorumunu ya da sonucunu üretmez. Denetçi metni yeniden yazmaz; sorunu alıntısıyla gösterir.

## Ne kadar tutar?

Tahmin, 11 Ekim 2026'da OpenRouter model listesindeki fiyatlarla yapıldı. Fiyatlar değişir; güncel değerler `agents.yaml` içindeki `fiyatlar` bölümünde tarihli tutulur ve her çalıştırmadan sonra gerçek kullanım `.tezatlas/kullanim.jsonl` dosyasına yazılır.

Varsayımlar: bir bölüm yaklaşık 3.000 kelime (≈ 4.500 token), kaynak notları en fazla 120.000 karakter (≈ 35.000 token), denetçinin cevabı ≈ 2.500 token. Bölüm başına yaklaşık 40.000 girdi ve 2.500 çıktı tokenı.

| Model (OpenRouter adı) | 1M token girdi / çıktı (USD) | Bir bölümün denetimi (USD) |
|---|---|---|
| `openai/gpt-6.1-sol` | 2,00 / 10,00 | ≈ 0,11 |
| `anthropic/claude-sonnet-5.5` | 2,00 / 10,00 | ≈ 0,11 |
| `google/gemini-3.8-flash` | 0,75 / 3,75 | ≈ 0,04 |
| `deepseek/deepseek-v4.1-flash` | 0,30 / 1,20 | ≈ 0,02 |
| `anthropic/claude-haiku-5.5` | 0,10 / 0,50 | ≈ 0,005 |

Örnek: 8.000 kelimelik bir makale (5 bölüm), iki modelle çapraz denetim (`gpt-6.1-sol` + `gemini-3.8-flash`), iki düzeltme turu: 5 × 0,15 × 2 ≈ **1,5 USD**. Bu, yazar modelin maliyetine eklenir. Yazar olarak Claude Code ya da Codex aboneliği kullanıyorsanız yazarın ek ücreti yoktur; yalnız denetçi API'si ücretlenir.

## Kurulum (bir kez)

1. https://openrouter.ai/keys adresinden bir anahtar oluşturun. Anahtara harcama sınırı koyun.
2. Repo klasöründe:
   ```bash
   cp .env.example .env        # .env içine OPENROUTER_API_KEY=... yazın
   python3 -m pip install -e ".[all]"
   tezatlas-agents --list-providers
   ```
3. İsterseniz `agents.yaml` içinde `denetci`, `hakem` ve `capraz_denetim` modellerini değiştirin. Yazar modelinizle aynı şirketin modelini seçmeyin.

## Kullanım

```bash
# Tek denetçi (agents.yaml: denetci)
tezatlas-agents denetci --input bolumler/giris.md

# Hakem simülasyonu
tezatlas-agents hakem --input makale.md --document-type article

# Çapraz denetim: iki model, bulgular yan yana, rapor bolumler/giris_DENETIM.md
tezatlas-agents capraz_denetim --input bolumler/giris.md

# Yalnız belirli kaynakların notlarıyla
tezatlas-agents capraz_denetim --input bolumler/giris.md --kaynak Smith_2020 --kaynak BIS_2021
```

Kaynak notları projedeki `notes/` ya da `notlar/` klasöründen okunur. Not yoksa denetçi kaynak-iddia uyumunu denetleyemez; bu durumda uyarı verilir.

Raporda her bulgu için "alıntı taslakta" bilgisi vardır. Model taslakta olmayan bir cümleden söz ediyorsa bu "hayır" görünür; önce onu kontrol edin. Her bulgunun altında karar satırı vardır: düzelttim ya da katılmıyorum (nedeniyle). Bu satırlar danışman görüşmesinde ve yapay zekâ kullanım beyanında işinize yarar.

## Araçlara göre tarifler

### Claude Code ile yazıyorsanız

- Yazar: Claude Code (aboneliğiniz). Başlatma: `claude`, sonra `/tezatlas`.
- Denetim: `/cross-review bolumler/giris.md`. Komut çapraz denetimi çalıştırır ve raporu sizinle birlikte gözden geçirir. Varsayılan denetçiler GPT ve Gemini'dir; Claude değildir.

### Codex ile yazıyorsanız

- Codex repo kökündeki `AGENTS.md` dosyasını okur; o dosya TezAtlas kurallarına yönlendirir. Başlatmak için Codex'e: "`.claude/commands/tezatlas.md` dosyasını oku ve uygula" deyin. Diğer komutlar için de aynı biçimde ilgili dosyayı okutun (ör. `/review-draft` için `.claude/commands/review-draft.md`).
- Denetim: `agents.yaml` içinde `denetci` ve `capraz_denetim` listesinden OpenAI modellerini çıkarın (ör. Claude ve Gemini kullanın), sonra `tezatlas-agents capraz_denetim --input ...`.

### Gemini CLI ile yazıyorsanız

- Gemini CLI repo kökündeki `GEMINI.md` dosyasını okur; o da aynı kurallara yönlendirir.
- Denetim: `capraz_denetim` listesinden Gemini'yi çıkarın.

### API anahtarı olmadan, iki abonelikle

İkinci bir aboneliğiniz varsa (ör. Claude ve ChatGPT) API ücreti ödemeden de çapraz denetim yapabilirsiniz:

1. Taslağı birinci araçla yazın.
2. İkinci aracı aynı repo klasöründe açın ve şunu söyleyin: "`agents/prompts/denetci.md` dosyasındaki talimatla `bolumler/giris.md` taslağını `notlar/` klasöründeki kaynak notlarına göre denetle. Yazarın notlarına bakma. Sonucu `bolumler/giris_DENETIM_<araç>.md` dosyasına yaz."
3. İki aracın raporunu yan yana okuyun; ortak bulgulardan başlayın.

Bu yol yavaştır ve maliyet kaydı tutulmaz, ama ek ücret gerektirmez.

## Sınırlar

- Denetçi de bir dil modelidir; yanlış alarm verebilir ve sorun kaçırabilir. Rapor bir kontrol listesidir, hüküm değildir.
- Denetçi kaynakların kendisini değil sizin notlarınızı okur. Notta olmayan bir şeyi "kaynakta yok" diye işaretleyebilir. Kesin karar için kaynağın kendisine bakın (`/citation-check`).
- Kişisel veri, yayımlanmamış veri ya da gizli belge içeren taslakları dış bir modele göndermeden önce kurumunuzun kurallarını kontrol edin. OpenRouter hesabınızda veri saklamayan sağlayıcılarla sınırlama ayarı vardır.
