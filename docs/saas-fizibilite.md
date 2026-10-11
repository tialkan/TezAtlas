# TezAtlas'ı web üzerinde sunmak: fizibilite raporu

Tarih: 12 Ekim 2026. Hazırlayan: TezAtlas bakımcısı için yapay zekâ destekli inceleme. Bu belge bir karar belgesidir; aşağıdaki "Karar vermeniz gerekenler" bölümü onaylanmadan kod yazılmaz.

Hukuki notlar hukuki danışmanlık değildir. Kullanım koşulları değişir; aşağıdaki alıntılar belirtilen tarihlerde sağlayıcıların kendi sayfalarından okunmuştur.

## Kısa sonuç

1. **Kullanıcının Claude ya da ChatGPT aboneliğini sitede kullanmak mümkün değil.** İki sağlayıcının koşulları da hesabın başkasına açılmasını ve aboneliğin otomatik ya da programla kullanılmasını yasaklıyor. Abonelik yalnız kullanıcının kendi bilgisayarındaki CLI yolunda (Claude Code, Codex) kullanılabilir.
2. **Site için gerçekçi yol: kullanıcının kendi OpenRouter anahtarı (BYOK) ve küçük, ücretsiz bir pilot hakkı.** Bu, Anlatsın'da zaten çalışan modelin aynısıdır; altyapının büyük kısmı hazır.
3. **8.000 kelimelik, 40 kaynaklı bir makalenin bütün aşamaları yaklaşık 1,7 ile 6,5 USD arasında tutar** (model seçimine göre). Çapraz denetim bunun yalnız 0,3 ile 0,7 USD'lik kısmıdır.
4. **İlk ürün yazdırma değil denetim olmalı.** "Taslağını ve kaynaklarını yükle, iki farklı modelle denetlensin" özelliği en düşük riskli, en çabuk değer veren ve TezAtlas'ın "uydurma atıf yok" ilkesini doğrudan gösteren adımdır. Rehberli yazım ikinci sürüme kalmalı.

## 1. Abonelik mi, API mi?

### Sağlayıcıların koşulları

**Anthropic, Consumer Terms of Service (yürürlük 8 Ekim 2025),** https://www.anthropic.com/legal/consumer-terms

- Yasak kullanımlar arasında: "Except when you are accessing our Services via an Anthropic API Key or where we otherwise explicitly permit it, to access the Services through automated or non-human means, whether through a bot, script, or otherwise."
- Hesap: "You may not share your Account login information, Anthropic API key, or Account credentials with anyone else. You also may not make your Account available to anyone else."

**OpenAI, Kullanım Şartları (ABD dışı, yürürlük 1 Ocak 2026),** https://openai.com/policies/row-terms-of-use/

- "Hesap kimlik bilgilerinizi paylaşamaz veya hesabınızı başkalarının kullanımına açamazsınız."
- Yasak kullanımlar arasında: "Otomatik veya programlı olarak veri veya Çıktıyı dışa aktarma."

### Sonuç

Bir web sitesinin kullanıcının Claude Pro/Max ya da ChatGPT Plus/Pro hesabıyla oturum açıp onun adına istek göndermesi iki koşulla da çelişir: hesap üçüncü tarafa açılmış olur ve hizmet programla kullanılmış olur. Kullanıcının aboneliği yalnız sağlayıcının kendi araçlarında (Claude Code, Codex, sohbet arayüzleri) kullanılabilir.

Bu yüzden sitenin seçenekleri:

| Seçenek | Nasıl | Maliyet kimde |
|---|---|---|
| BYOK, OpenRouter | Kullanıcı kendi OpenRouter anahtarını girer; anahtar yalnız o isteğin süresince kullanılır, saklanmaz | Kullanıcı |
| BYOK, doğrudan sağlayıcı | Kullanıcı Anthropic ya da OpenAI API anahtarını girer | Kullanıcı |
| Site kredisi | Site kendi anahtarıyla çalışır, kullanıcı kredi satın alır | Site (ödeme, fatura, iade yükü de) |
| Ücretsiz pilot | Site kendi anahtarıyla, kişi başı küçük ve günlük toplam tavanlı hak verir | Site (bütçe tavanıyla sınırlı) |

OpenRouter tek anahtarla birden çok şirketin modeline eriştiği için çapraz denetimi kullanıcı açısından en basit yoldur. Doğrudan sağlayıcı anahtarı ikinci seçenek olarak desteklenebilir.

## 2. Maliyet modeli

Fiyatlar 11 Ekim 2026'da https://openrouter.ai/api/v1/models listesinden okunmuştur (1 milyon token başına, girdi / çıktı, USD): `google/gemini-3.8-flash` 0,75 / 3,75; `anthropic/claude-sonnet-5.5` 2 / 10; `anthropic/claude-opus-5.5` 4 / 20; `openai/gpt-6.1-sol` 2 / 10; `deepseek/deepseek-v4.1-flash` 0,30 / 1,20.

### Varsayımlar (tipik makale: 8.000 kelime, 40 kaynak)

| Aşama | Ne olur | Girdi token | Çıktı token |
|---|---|---|---|
| Okuma ve not | 40 kaynağın her biri (ortalama ≈ 12.000 token) okunur, her biri için ≈ 1.500 tokenlık not çıkar | 480.000 | 60.000 |
| Sentez ve yapı | Notlardan argüman haritası ve bölüm planı | 80.000 | 8.000 |
| Rehberli yazım | 5 bölüm, her biri için 2 taslak seçeneği, 2 düzeltme turu | 450.000 | 90.000 |
| Çapraz denetim | 5 bölüm, 2 model, 2 tur (10 çalıştırma × ≈ 40.000 girdi) | 400.000 | 25.000 |
| Hakem provası | Bir kez, tam metin | 60.000 | 3.000 |
| **Toplam** | | **≈ 1,47 milyon** | **≈ 186.000** |

### Senaryolar

| Senaryo | Modeller | Tek model, denetimsiz | Çapraz denetim dahil |
|---|---|---|---|
| Ekonomik | Hepsi Gemini 3.8 Flash; denetimde DeepSeek + Gemini | ≈ 1,41 USD | ≈ 1,68 USD |
| Dengeli | Okuma Gemini Flash, sentez ve yazım Claude Sonnet 5.5; denetimde GPT-6.1 Sol + Gemini | ≈ 2,68 USD | ≈ 3,40 USD |
| Premium | Okuma Sonnet, sentez ve yazım Claude Opus 5.5; denetimde GPT-6.1 Sol + Gemini | ≈ 5,79 USD | ≈ 6,51 USD |

Notlar:

- En büyük kalem okuma ve yazımdır. Okuma bir kez yapılır ve notlar yeniden kullanılır; aynı kaynaklarla ikinci bir makalede maliyet belirgin biçimde düşer.
- Sağlayıcıların önbellekleme (prompt caching) indirimi uygulanırsa tekrar eden bağlamın (notlar, sistem istemi) maliyeti düşer. Yukarıdaki tablo bu indirimi hesaba katmaz; yani üst tahmindir.
- Bir doktora tezi (yaklaşık 60.000 kelime, 200 kaynak) kabaca 6 ile 8 katıdır: dengeli senaryoda 20 ile 30 USD aralığında.
- Gerçek değerler ölçülmelidir. Framework artık her ajan çalıştırmasının token kullanımını `.tezatlas/kullanim.jsonl` dosyasına yazıyor (sürüm 1.3.0); ilk kullanıcılardan bu kayıtlarla tablo güncellenir.

## 3. Üç kullanım yolu

| Yol | Kime uygun | Kurulum | Maliyet | Kontrol |
|---|---|---|---|---|
| (a) CLI ve kendi aboneliği | Terminal açabilen, aboneliği olan | Claude Code veya Codex, repo klonu | Abonelik (ek ücret yok); çapraz denetim için küçük API maliyeti ya da ikinci abonelik | Tam: dosyalar kendi bilgisayarında |
| (b) Sitede BYOK | Kurulum istemeyen, kart kullanabilen | Yalnız OpenRouter hesabı ve anahtar | Kullanımı kadar (tablo 2), doğrudan sağlayıcıya | Orta: dosyalar sınırlı süre sitede |
| (c) Sitede kredi | Kart ya da yabancı hizmetle uğraşmak istemeyen | Yok | Site fiyatı (maliyet + işletme) | Düşük |

**Öneri: (b) ile başlayın, (a)'yı ana yol olarak koruyun, (c)'yi ölçümden sonra düşünün.**

- (b) için altyapı Anlatsın'da hazır: BYOK başlığı, anahtar doğrulama, anahtarı saklamama, günlük site bütçesi, pilot hakkı, kuyruk benzeri parça parça işleme.
- (c) ödeme altyapısı, fatura, iade, KDV ve kötüye kullanım riski getirir. Gerçek kullanım maliyeti ve talep ölçülmeden fiyat koymak tahmin olur.
- Pilot: ücretsiz kullanıcıya site anahtarıyla küçük bir hak (ör. bir bölümün çapraz denetimi, 12 saatte bir). Anlatsın'daki aynı tavan ve hız sınırı mekanizması.

## 4. Ürün tasarımı

### Sürüm 1: "Denetle" (önerilen ilk ürün)

Kullanıcı bir bölüm taslağı (.docx, .md ya da yapıştırılmış metin) ve o bölümde atıf yaptığı kaynakların PDF'lerini yükler. Site:

1. PDF'lerden metni çıkarır; her kaynak için kısa not üretir (ucuz model). Notları kullanıcıya gösterir, düzeltmesine izin verir.
2. Künyeleri PDF'ten doğrulanmış biçimde üretir (framework'teki doğrulama kapısı); eşleşmeyenleri "doğrulanmadı" diye gösterir.
3. Taslağı iki farklı şirketin modeliyle kör denetler; bulguları yan yana, alıntı ve kaynak bağlantısıyla gösterir. Her bulguda "düzelttim / katılmıyorum (neden)" seçimi.
4. Raporu indirilebilir verir (Markdown, Word). Rapor yapay zekâ kullanım beyanına ek olarak kullanılabilir.

Neden önce bu: metin üretmez, dolayısıyla "yapay zekâ tez yazdı" tartışmasının dışındadır; framework'ün en güçlü ilkesini (kaynak ve atıf doğruluğu) doğrudan gösterir; tek oturumda biter; maliyeti düşüktür (bölüm başına ≈ 0,15 USD).

### Sürüm 2: Proje ve okuma

- Her makale bir proje: kaynak kütüphanesi, notlar, `STATUS` karşılığı bir durum ekranı.
- Kaynak ekleme: PDF yükleme, DOI listesi, BibTeX içe aktarma; DOI ile açık erişim kopyası arama (yasal zincir).
- Okuma aşaması: not şablonu, okuma raporu, doygunluk göstergesi.

### Sürüm 3: Rehberli yazım

- Aşama sihirbazı (framework'teki faz kapılarıyla aynı), bölüm başına A/B taslak seçenekleri, akademik yazım notu.
- Her aşamada **maliyet önizlemesi** ("bu aşama yaklaşık 0,40 USD") ve kullanıcının koyduğu **bütçe tavanı**; tavan aşılacaksa iş başlamaz.
- Dışa aktarma: Word, LaTeX, BibTeX.

## 5. Güvenlik, gizlilik ve hukuk

- **Anahtar:** BYOK anahtarı tarayıcıdan yalnız istek başlığıyla gelir, sunucu belleğinde o isteğin süresince kullanılır, veritabanına, loga ve hata kaydına yazılmaz. İsteğe bağlı "bu tarayıcıda hatırla" yalnız kullanıcının tarayıcısında. Sağlayıcıda anahtara harcama sınırı konması önerilir. (Anlatsın'daki uygulama.)
- **Veri saklama:** Yüklenen PDF ve taslaklar varsayılan olarak 24 saat sonra, kullanıcı isterse hemen silinir. Hesaplı kullanımda proje süresince saklanır ve tek tıkla tamamen silinir.
- **Model sağlayıcıları:** İsteklerde verinin eğitimde kullanılmamasını ve sıfır veri saklamayı (ZDR) destekleyen uç noktalar istenir. ZDR her model için desteklenmeyebilir; desteklenmiyorsa kullanıcıya gösterilir, sessizce kaldırılmaz.
- **KVKK:** Aydınlatma metni gerçek veri envanterinden; yurt dışına aktarım (OpenRouter ve model sağlayıcıları ABD'de olabilir) için açık rıza, ön işaretsiz kutu. Taslakta kişisel veri (katılımcı bilgisi, yayımlanmamış veri) varsa yüklememesi gerektiği yükleme ekranında yazılı.
- **Telif:** Kullanıcı yalnız erişim hakkı olduğu kaynakları yükler; site gölge kütüphanelerden kaynak çekmez.
- **Yapay zekâ kullanım beyanı:** Her raporun sonunda, kurumların beyan formlarına uyarlanabilir kısa bir şablon: hangi araç, hangi aşamada, ne amaçla; karar ve sorumluluğun yazarda olduğu.
- **Kötüye kullanım:** IP özeti başına hız sınırı, günlük site tavanı, istek ve dosya boyutu sınırı, eşzamanlılık sınırı; ödev ya da tez "yazdırma" isteğine sürüm 1 zaten açık değildir.

## 6. Teknik plan

Site reposunda (`tezatatlascom`) Anlatsın modülünün yanına yeni bir modül: `src/yaz/` ve `tezatlas.com/yaz` (sürüm 1 için "Denetle" ekranı).

| Gerekli parça | Anlatsın'da var mı | Not |
|---|---|---|
| PortalShell ve tasarım dili | Var | Aynı kabuk ve belirteçler |
| PostgreSQL, Drizzle, migration | Var | Yeni şema `yaz` |
| Anonim pilot, IP özeti, 12 saat kuralı | Var | Hak birimi "bölüm denetimi" |
| BYOK başlığı, anahtar doğrulama, saklamama | Var | Aynen |
| Günlük site bütçesi, maliyet kaydı | Var | Aynen |
| PDF metin çıkarma | Var (unpdf) | Kaynak başına sınır |
| Uzun iş için parça parça işleme | Kısmen (ses parçaları) | Kaynak notları için iş tablosu + istemcinin ilerleme sorgusu; her istekte zaman aşımı |
| Künye doğrulama kapısı | Framework'te (Python) | TypeScript'e taşınır ya da küçük bir Python servisi; ilk sürümde TypeScript'e taşımak daha basit |
| Denetçi istemleri ve karşılaştırma | Framework'te | İstem dosyaları tek kaynaktan paylaşılır (framework reposundan sürümlü kopya) |
| Word dışa aktarma | Yok | `docx` paketiyle sunucuda |

**Sürüm 1 kapsamı (tahmini 2 ila 3 hafta):** yükleme ekranı (taslak + en fazla 10 PDF, pilotta 3), kaynak notları, künye doğrulama, iki modelle denetim, yan yana rapor ve kararlar, Markdown/Word indirme, 24 saatlik silme, BYOK ve pilot. Hesap yok.

**Sonraki sürümler:** hesap ve proje (Better Auth, Anlatsın'da hazır ama kapalı), okuma aşaması, rehberli yazım, danışman paylaşım bağlantısı, kredi sistemi (ölçümden sonra).

## Karar vermeniz gerekenler

1. **İlk ürün:** Sürüm 1 "Denetle" ile mi başlayalım (önerilen), yoksa doğrudan proje ve rehberli yazımla mı?
2. **Pilot hakkı:** Ücretsiz kullanıcıya kaç bölüm denetimi, hangi sıklıkla? Öneri: 12 saatte bir, en fazla 3 kaynaklı bir bölüm; site günlük bütçesi 5 USD.
3. **Varsayılan modeller:** Denetimde GPT-6.1 Sol + Gemini 3.8 Flash (dengeli) mi, DeepSeek + Gemini (ekonomik) mi? Öneri: pilotta ekonomik, BYOK'ta kullanıcı seçsin, varsayılan dengeli.
4. **Adres:** `tezatlas.com/yaz` mı, `tezatlas.com/denetle` mi? Sürüm 1 yalnız denetlediği için `/denetle` daha dürüst bir ad olabilir.
5. **Kredi satışı:** Şimdilik yok (öneri). Ölçüm sonrası yeniden değerlendirilir.
