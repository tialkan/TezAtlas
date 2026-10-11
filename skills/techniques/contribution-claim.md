---
title: "Contribution Claim Shield — Originality and Gap Verification Protocol"
title_tr: "Katkı İddiası Kalkanı — Özgünlük ve Boşluk Doğrulama Protokolü"
node_type: technique
description: "Universal protocol for stress-testing a contribution claim before Phase 1 begins. Applies to all document types. Forces the researcher to articulate novelty, map the literature gap, classify contribution type, and pre-empt the strongest counter-argument. Fires at every Phase 0 → Phase 1 gate."
description_tr: "Faz 1 başlamadan önce katkı iddiasını zorlayan evrensel protokol. Tüm belge türleri için geçerlidir. Araştırmacıyı özgünlüğü ifade etmeye, literatür boşluğunu haritalamaya, katkı türünü sınıflandırmaya ve en güçlü karşı argümanı önceden yanıtlamaya zorlar. Her Faz 0 → Faz 1 kapısında tetiklenir."
tags: [contribution-claim, originality, gap-analysis, phase-gate, phase-0, all-document-types, iron-rule-5]
links_to:
  - skills/core/reviewer-mode.md
  - skills/core/iron-rules.md
  - skills/techniques/snowball-sampling.md
  - skills/techniques/argument-evaluation.md
  - skills/techniques/literature-synthesis.md
used_by:
  - skills/phases/thesis/phase-0-identity.md
  - skills/phases/article/phase-0-claim.md
  - skills/phases/conference/phase-0-abstract.md
  - skills/phases/lit-review/phase-0-protocol.md
  - skills/phases/grant-proposal/phase-0-funder-analysis.md
  - skills/phases/research-proposal/phase-0-context.md
language: bilingual
version: "1.0"
---

# Katkı İddiası Kalkanı / Contribution Claim Shield

Özgün olmayan çalışma yayımlanmaz.
"Özgün olduğunu düşünmek" yetmez — kanıtlamak gerekir.

Bu node, Faz 0'dan Faz 1'e geçişi engelleyen kapı protokolüdür.
Tüm belge türlerinde zorunludur.

---

## Neden Bu Protokol Var

Araştırmacıların en sık yaptığı hata: katkı iddiasını baştan netleştirmeden okumaya dalmak.
Haftalar sonra şunu keşfederler: "Bunu zaten biri yapmış."

Kalkan bu hatayı en başta önler.

---

## 1. Katkı Türü Taksonomisi

Çalışmanın hangi tür katkı yaptığını önce sınıflandır.
Bir çalışma birden fazla türde katkı yapabilir ama **birincil türü** netleştirilmeli.

| Katkı Türü | Açıklama | Örnek |
|------------|----------|-------|
| **Kuramsal / Theoretical** | Yeni kavram, çerçeve veya model önerir | Mevcut teorinin sınırlarını genişleten yeni analitik çerçeve |
| **Yöntemsel / Methodological** | Yeni ya da geliştirilmiş araştırma yöntemi | Mevcut ölçeği yeni bağlama uyarlama, yeni ölçüm aracı |
| **Ampirik / Empirical** | Yeni veri: daha büyük örneklem, yeni bağlam, yeni zaman dilimi | Türkiye'de hiç test edilmemiş hipotezi test etmek |
| **Sentez / Synthesis** | Dağınık literatürü birleştiren sistematik derleme | Aynı konuda çelişen bulguları uzlaştıran meta-analiz |
| **Pratik / Practical** | Politika önerisi, uygulama rehberi, sektöre özgü çıktı | Mevzuat boşluğuna çözüm öneren hukuki analiz |

**Claude'a sınıflandırma için prompt:**
```
Bu çalışmanın katkısını beş türden biri veya birkaçıyla sınıflandır:
Kuramsal / Yöntemsel / Ampirik / Sentez / Pratik.
Birincil türü belirt ve neden bu sınıfa girdiğini tek paragrafta gerekçelendir.
```

---

## 2. Dört Soruluk Kalkan (Faz Kapısı)

Her soru, Faz 0 → Faz 1 geçişi için zorunludur.
Tatmin edici yanıt verilmeden bir sonraki soruya geçilmez.

---

### Soru 1 — En Yakın Önceki Çalışmalar

> **"Bu iddiayı daha önce tam olarak kim yapmış?**
> **Konuna en yakın üç çalışmayı bul ve listele."**

**Kabul edilebilir yanıt:**
- En az 3 atıf ile birlikte (yazar, yıl, başlık, kısa özet)
- Her birinin senin çalışmandan farkı net biçimde ifade edilmiş

**Kabul edilemez yanıt:**
```
❌ "Bu konuda pek fazla çalışma yok."
❌ "Türkiye'de hiç çalışılmamış." (kaynak olmadan)
❌ "Genel olarak X'e bakılmış ama benim açımdan değil."
```

**Eğer 3 yakın çalışma bulamazsan:**
→ Snowball sampling başlatılmamış demektir. [[techniques/snowball-sampling]] ile devam et; bu soru tekrar sorulur.

---

### Soru 2 — Özgünlük Deltası

> **"Sen ne ekliyorsun ki onlar eklememiş?"**
> **"Farkın tek cümlede ne?"**

Özgünlük deltaları:

```
Bağlam farkı:    "X daha önce A ülkesinde çalışıldı; ben B bağlamında test ediyorum."
Zaman farkı:     "X 2015 öncesi verilere bakıldı; ben 2020 sonrasını kapsıyorum."
Yöntem farkı:    "X nitel yaklaşım kullandı; ben nicel analizle karşılaştırıyorum."
Kuram farkı:     "X A teorisiyle açıkladı; ben B teorisinin açıklayıcı gücünü test ediyorum."
Kapsam farkı:    "X tek sektörü inceledi; ben sektörler arası karşılaştırma yapıyorum."
Sentez farkı:    "X ve Y çelişiyor; ben bu çelişkiyi çözüyorum."
```

**Güçlü yanıt şablonu:**
```
"[En yakın çalışma] X'i [yöntemle] incelemiştir; ancak [bağlam/dönem/değişken]
kapsam dışı kalmıştır. Bu çalışma [eksik olan kısım]ı [nasıl] ele almaktadır."
```

**Zayıf yanıt örnekleri:**
```
❌ "Benim çalışmam daha kapsamlı."
❌ "Türkçe kaynak yoktu."
❌ "Bu konu önemli ama yeterince çalışılmamış."
```

---

### Soru 3 — Önemi ve Kimin İşine Yarayacağı

> **"Bu katkı neden önemli? Kimin umurunda olacak?"**

Önemi ikili düzeyde göster:

**Akademik:** Bu bulgu hangi teorik tartışmayı ilerletiyor? Hangi paradigmayı sorgular veya destekler?

**Pratik / Toplumsal:** Bu bilgiyi kim kullanabilir? Politika yapıcı, uygulayıcı, sektör, birey?

**İyi yanıt şablonu:**
```
"Akademik açıdan: Bu çalışma [hangi tartışmaya / teorik boşluğa] katkı sağlar.
Pratik açıdan: [Kim] bu bulguyu [nasıl] kullanabilir / politika geliştirebilir."
```

**Kabul edilemez:**
```
❌ "Akademik literatüre katkı sağlayacaktır." (boş)
❌ "İlerideki çalışmalara ışık tutacaktır." (boş)
❌ "Önemli bir konu olduğu için." (circular)
```

---

### Soru 4 — En Güçlü Karşı Argüman

> **"Seni en çok zor durumda bırakan itiraz ne?"**
> **"Bir hakem reddetmek istese hangi gerekçeyi kullanır?"**

Bu soru Iron Rule 8'i (Savunma Zırhı) Faz 0'a taşır.

**Doğru yanıt yapısı:**
```
"En güçlü itiraz: [itiraz içeriği]
Bu itiraza cevabım: [yanıt]
Bu yanıtı destekleyen kaynağım: [kaynak — /sources/ klasöründe olmalı]"
```

**Kabul edilemez:**
```
❌ "Ciddi bir itiraz göremiyorum."
❌ "Metodoloji güçlü, sorun yok."
❌ "Hakem anlamayabilir ama ben haklıyım."
```

---

## 3. Literatür Boşluğu Haritası

Katkı iddiasını destekleyen boşluğu üç türden biri ile tanımla:

| Boşluk Türü | Tanım | Nasıl Gösterilir |
|-------------|-------|-----------------|
| **Ampirik boşluk** | Veri yok, test edilmemiş | "X bağlamında hiç ölçülmemiş" → kaynak + yokluğun kanıtı |
| **Teorik boşluk** | Açıklayıcı çerçeve eksik | "A ve B teorisi bu durumu açıklamıyor" → her iki kaynakta da yokluğu göster |
| **Metodolojik boşluk** | Mevcut yöntemler yetersiz | "Önceki çalışmalar X yüzünden yanıltıcı" → metodoloji eleştirisi kaynakla |

**Claude'a boşluk doğrulama için prompt:**
```
Şu katkı iddiasını analiz et: "[iddia]"
1. Boşluk türünü sınıflandır (ampirik / teorik / metodolojik)
2. Bu boşluğun var olduğunu kanıtlayan en az 3 kaynaktan alıntı ver
3. Bu kaynakların her birinin boşluğu nasıl doğruladığını bir cümleyle açıkla
```

---

## 4. Katkı İddiası Tek Cümle Testi

Kalkanı geçtikten sonra katkı iddiasını tek cümleye indir.
Bu cümle tüm çalışma boyunca kuzey yıldızındır.

**Şablon:**
```
"Bu [belge türü], [bağlam/dönem/örneklem] üzerinde [yöntem] kullanarak
[katkı] sağlamakta ve böylece [hangi boşluk]u doldurmaktadır."
```

**Örnekler:**

✅ Güçlü:
```
"Bu makale, 2019-2023 dönemi Türkiye banka verilerini panel analizi ile
inceleyerek CBDC'nin kredi genişlemesi üzerindeki etkisini ilk kez ölçmekte
ve mevcut teorik modellerin döviz kuru kanalını ihmal ettiğini göstermektedir."
```

❌ Zayıf:
```
"Bu tez dijital para birimlerini kapsamlı biçimde inceleyerek
Türkiye için öneriler sunmaktadır."
```

---

## 5. Kalkan Geçiş Kriterleri

Faz 1'e geçmeden önce aşağıdakilerin tamamı işaretlenmeli:

```
[ ] Katkı türü sınıflandırıldı (kuramsal/yöntemsel/ampirik/sentez/pratik)
[ ] En yakın 3 önceki çalışma listelendi (kaynak + fark açıklaması)
[ ] Özgünlük deltası tek cümlede netleştirildi
[ ] Akademik + pratik önem somut biçimde ifade edildi
[ ] En güçlü karşı argüman ve yanıtı formüle edildi
[ ] Boşluk türü sınıflandırıldı ve en az 3 kaynakla doğrulandı
[ ] Katkı iddiası tek cümleye indirildi — "tek cümle testi" geçildi
```

Reviewer Mode açıksa → Claude bu kriterleri Kıdemli Hakem rolüyle sorgular.
Standart modda → danışman onayından önce bu liste tamamlanır.

---

## EN — Quick Reference

**The four shield questions:**
1. Who has done this before? List the three closest prior works.
2. What do you add that they didn't? State your novelty delta in one sentence.
3. Why does it matter? Name the academic debate and the practical beneficiary.
4. What is the strongest counter-argument and how do you answer it?

**Contribution claim one-sentence template:**
```
"This [document type] uses [method] on [context/sample/period] to [contribution],
thereby filling the [gap type] gap in the literature on [topic]."
```

**Minimum to pass the gate:**
- 3 prior works identified with clear differentiation
- 1 sentence novelty delta
- 1 sentence academic significance + 1 sentence practical significance
- 1 counter-argument with answer and source
- Contribution claim reduced to 1 sentence
