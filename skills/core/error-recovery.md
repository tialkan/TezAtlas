---
title: "Error Recovery — What to Do When Things Go Wrong"
title_tr: "Hata Kurtarma — Bir Şeyler Yanlış Gittiğinde Ne Yaparsın"
node_type: foundation
description: "Recovery protocols for common failure scenarios: lost work, broken context, wrong structure, fabrication temptation, advisor conflict, and tool failures. Covers what to do, not just what not to do."
description_tr: "Sık karşılaşılan hata senaryoları için kurtarma protokolleri: kayıp çalışma, bozuk context, yanlış yapı, uydurma cazibesi, danışman çatışması ve araç arızaları. Ne yapılmaması değil, ne yapılacağı."
tags: [error-recovery, failure-scenarios, recovery, context-loss, git-recovery, foundation]
links_to:
  - skills/tooling/git-workflow.md
  - skills/core/context-management.md
  - skills/core/iron-rules.md
  - skills/core/academic-integrity.md
used_by:
  - skills/moc/MOC-core.md
language: bilingual
version: "2.0"
---

# Hata Kurtarma / Error Recovery

Bir şeyler yanlış giderse dur, paniğe kapılma, bu protokolü uygula.

When something goes wrong: stop, don't panic, apply this protocol.

---

## Senaryo 1: Çalışma Kaybedildi (Git Yok)

**Belirti:** Dosya silindi veya üzerine yazıldı, git yok.

**Kurtarma:**
1. Önce sakin ol — terminalde `ls -lt` ile son değiştirilen dosyalara bak
2. macOS: Time Machine varsa → dosyayı kurtar
3. Editor undo geçmişini kontrol et
4. Kısmi kurtarma mümkünse → önce mevcut halini kaydet, sonra yeniden yaz

**Önleme:** [[iron-rules]] Kural 6 — her oturum sonu git commit. Bu senaryoyu imkansız kılar.

---

## Senaryo 2: Git'te Eski Versiyona Dönmek Gerekiyor

**Belirti:** Danışman "eski hali daha iyiydi" dedi.

**Kurtarma:**
```bash
git log --oneline          # hangi commit'e dönülecek?
git checkout [commit-hash] -- [dosya_yolu]   # sadece o dosyayı geri al
```

Branch kullananlar için:
```bash
git checkout draft         # çalışma branch'ine geç
git revert [commit-hash]   # eski değişikliği geri al, commit oluşturur
```

**Tam detay:** [[git-workflow]]

---

## Senaryo 3: Context Kaybı (Uzun Ara Sonrası)

**Belirti:** Mevcut projeye devam edilecek ama her şey unutulmuş.

**Kurtarma — Sırayla:**
1. `DURUM_OZETI.md` oku → narrative durum (ne yapıldı, ne bekliyor)
2. `MEMORY.md` oku → sayısal ilerleme (kaçıncı bölüm, kaç kelime)
3. `DERSLER.md` oku → birikmiş proje kuralları
4. `tezprotokol.md` oku → proje anayasası
5. Son yazılan bölümün son 3 paragrafını oku → devamlılık

Tam recovery protokolü: [[context-management]]

---

## Senaryo 4: Yanlış Yapı (Faz 6'da Fark Edildi)

**Belirti:** Yazım sırasında yapının yanlış olduğu anlaşıldı.

**Kurtarma:**
1. DURUMU GEÇİCİ KAYDET → git commit "yapı sorunu tespit edildi"
2. Hangi bölüm yanlış? → Argümanlar nasıl yeniden sıralanmalı?
3. [[argument-mapping]] tekniğini uygula → notlardan yeniden yapı çıkar
4. Danışmana danış — büyük yapı değişikliği danışman onayı gerektirir ([[academic-integrity]])
5. Onay sonrası → bölümleri yeniden düzenle → git commit "yapı güncellendi"

**Önemli:** İçerik kaybolmasın — sadece sıralama değişecek.

---

## Senaryo 5: Kaynak Bulunamıyor (Yazım Durdu)

**Belirti:** [[iron-rules]] Kural 1 tetiklendi — kaynak yok, yazım durdu.

**Kurtarma:**
1. O paragrafı şimdilik atla → `[KAYNAK BEKLENİYOR: konu]` etiketi bırak
2. Başka bir paragraf/alt bölümden devam et (kaynağı olanı)
3. Kaynak arama: [[open-access-chain]] → [[source-hunting]] sırasını takip et
4. Kaynak geldiğinde → etiketi kaldır → o paragrafı yaz

**YASAK:** "Kaynak yok ama şimdilik yaz, sonra düzeltirim" — bu [[iron-rules]] Kural 1 ihlalidir.

---

## Senaryo 6: Uydurma Cazibesi

**Belirti:** Kaynak bulunamıyor, sayfa numarası belirsiz, ama "yaklaşık" bir atıf yapma isteği oluştu.

**Kurtarma:**
1. DUR — [[iron-rules]] Kural 4 tetiklenecek
2. O cümleyi kaynak olmadan yazma
3. Seçenekler:
   - Cümleyi kaynak gerektirmeyecek şekilde yeniden yaz (genel yargı olarak)
   - Kaynağı bul (PDF'te gerçek sayfa numarasını tespit et)
   - O iddiayı tezden çıkar

**Hatırlatma:** Turnitin/iThenticate sahte atıfı tespit etmeyebilir — ama jüri sorar. "Bu iddiayı nerede gördünüz?" sorusuna cevap yoksa savunmada çöker.

---

## Senaryo 7: Araç Arızası (kaynak indirme betiği)

**Belirti:** `scripts/find_source.py` çalışmıyor veya hata veriyor.

**Kurtarma:**
1. İnternet bağlantısını ve `TEZATLAS_MAILTO` ayarını kontrol et; API hız sınırına takıldıysa birkaç dakika bekle
2. API anahtarını yenile (kullanıcı kendi hesabından)
3. Elle indirme: DOI ile Unpaywall/OpenAlex'te ya da kurum kütüphanesinde ara, indir
4. Alternatif kanallar: SSRN → arXiv → CORE → Google Scholar "PDF" → kütüphane

**Tam alternatif kanal listesi:** [[open-access-chain]]
