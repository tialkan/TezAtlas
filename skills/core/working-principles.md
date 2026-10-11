---
title: "Working Principles — 8 Operational Principles"
title_tr: "Çalışma Prensipleri — 8 Operasyonel Prensip"
node_type: foundation
description: "Eight behavioral principles governing how TezAtlas operates: no unplanned writing, context protection, self-improvement loop, verification before completion, argument elegance, autonomous correction, task management, and core fundamentals."
description_tr: "TezAtlas'ın nasıl çalıştığını yöneten 8 davranışsal prensip: plansız yazım yasağı, context koruma, öz-iyileştirme döngüsü, doğrulamadan tamamlama yasağı, argüman zarafeti, otonom düzeltme, görev yönetimi ve temel ilkeler."
tags: [working-principles, behavior, self-improvement, verification, foundation]
links_to:
  - skills/core/context-management.md
  - skills/core/quality-control.md
  - skills/tooling/open-access-chain.md
used_by:
  - skills/moc/MOC-core.md
language: bilingual
version: "2.1"
---

# Çalışma Prensipleri / Working Principles

## A. Plansız Yazma Yasaktır

- Her bölüm yazılmadan önce paragraf planı çıkarılır
- Kaynak notlarından argüman sıralaması belirlenir
- Plan tutmazsa DUR → yeniden planla
- Kaynak okuma sırasında yapı değişmesi gerekirse → yapıyı güncelle

## B. Context Koruma

- PDF okuma ve kaynak arama mümkünse **ayrı bir göreve / paralel oturuma** verilir
- Ana context yazım için temiz tutulur
- Paralel araştırma mümkünse yapılır: 1 görev = 1 odak
- Context dolmadan oturumu kapat → yeni oturumda devam et

> **Yerel LLM notu:** Claude Code'da bu "subagent" ile yapılır. Ollama/yerel LLM'lerde ayrı bir terminal oturumu veya `tmux` penceresi kullanılabilir. Context window boyutu küçükse (8K altı) her alt bölüm ayrı oturum olarak işle.

## C. Öz-İyileştirme Döngüsü (DERSLER.md)

- Kullanıcı veya danışmandan gelen **her** düzeltme → DERSLER.md'ye yazılır
- Aynı hata iki kez tekrarlanmaz
- Her oturum başında DERSLER.md okunur
- Kurallar zaman içinde birikir → AI projeye özgü deneyim kazanır

Detaylar için [[context-management]] düğümüne bak.

## D. Doğrulamadan Tamamlama Yok

Bir bölüm "bitti" demeden önce [[quality-control]] kontrol listesi geçilir:
- Her dipnot PDF'ten doğrulandı mı?
- Terminoloji tutarlı mı?
- Paragraf yapısı kurallara uyuyor mu?
- "Danışman bunu onaylar mıydı?" testi

Doğrulama geçemediyse → TAMAMLANDI deme.

## E. Argüman Zarafeti

- Bir argüman zoraki hissediyorsa → daha güçlü geçiş ara
- Teorik sentez gerçekten sentez mi yoksa yan yana dizme mi?
- Özgün katkı paragraflarında zarafeti talep et
- Basit açıklayıcı paragraflar için over-engineering yapma

## F. Otonom Düzeltme

Kullanıcıya sormadan düzelt:
- Terminoloji tutarsızlığı
- Dipnot format hatası
- Tablo/şekil numarası atlama

Kullanıcıya sor:
- Önceki bölümle çelişki → UYAR (silme)
- Eksik kaynak → [[open-access-chain]] zincirinde ara, indir; bulunamazsa kullanıcıya bildir

## G. Görev Yönetimi

1. **Planla:** `_notlar.md`'de yazım planı oluştur
2. **Doğrula:** "Bu planla yazabilir miyim?" kontrol et
3. **İzle:** MEMORY.md + DURUM_OZETI.md güncelle
4. **Açıkla:** Her oturum sonunda özet ver
5. **Belgele:** Kalite kontrol sonuçlarını kaydet
6. **Öğren:** DERSLER.md güncelle

## H. Temel İlkeler

- **Sadelik:** Açık, anlaşılır akademik dil. Gereksiz karmaşıklıktan kaçın.
- **Tembellik Yok:** Kaynak uydurmak = tembellik. Kök kaynağı bul. Geçici çözüm yok.
- **Minimal Etki:** Düzenleme yaparken içerik kaybetme. Sadece gerekli yeri değiştir.
