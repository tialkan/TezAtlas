---
title: "Session Structure — Start and End Rituals"
title_tr: "Oturum Yapısı — Başlangıç ve Bitiş Ritüelleri"
node_type: technique
description: "The standardized start-of-session (read 6 files, determine target section) and end-of-session (update 4-5 files, git commit) rituals for Phase 6 writing sessions."
description_tr: "Faz 6 yazım oturumları için standart oturum başlangıcı (6 dosya oku, hedef bölümü belirle) ve bitiş (4-5 dosyayı güncelle, git commit) ritüelleri."
tags: [session-structure, ritual, context-management, git, phase-6]
links_to:
  - skills/core/context-management.md
  - skills/core/session-continuity.md
  - skills/tooling/git-workflow.md
  - skills/templates/tpl-status-summary.md
  - skills/templates/tpl-status.md
  - skills/templates/tpl-dashboard.md
  - skills/techniques/paragraph-coherence.md
used_by:
  - skills/phases/thesis/phase-6-writing.md
  - skills/core/context-management.md
language: bilingual
version: "2.1"
---

# Oturum Yapısı / Session Structure

## OTURUM BAŞI

```
╔═══════════════════════════════════════════════════╗
║  0. STATUS.md var mı? → EVET: resume banner sun  ║
║  1. tezprotokol.md oku (projenin anayasası)       ║
║  2. MEMORY.md kontrol et (ilerleme durumu)        ║
║  3. DERSLER.md oku (öğrenilen dersler)            ║
║  4. TERMINOLOJI.md oku (terim tutarlılığı)        ║
║  5. Hedef bölümü belirle                          ║
║  6. SOURCE_MAP.md'den ilgili sourcesı al    ║
╚═══════════════════════════════════════════════════╝
```

## OTURUM SONU

```
╔═══════════════════════════════════════════════════╗
║  1. Bölüm dosyasını kaydet                        ║
║  2. MEMORY.md güncelle                            ║
║     → tamamlanan bölümler, son dipnot, kelime     ║
║  3. DURUM_OZETI.md güncelle                       ║
║     → ne yapıldı, ne bekliyor, sonraki adım       ║
║     → PBK aktarımı (aşağıya bak)                  ║
║  4. STATUS.md güncelle  ← YENİ                    ║
║     → faz, konum, sonraki 3 eylem, engelleyiciler ║
║  5. DASHBOARD.md güncelle  ← YENİ                 ║
║     → ilerleme çubukları, kaynak sayacı, streak   ║
║  6. TERMINOLOJI.md güncelle (varsa yeni terimler) ║
║  7. DERSLER.md güncelle (varsa yeni dersler)      ║
║  8. git commit (STATUS.md + DASHBOARD.md dahil)   ║
╚═══════════════════════════════════════════════════╝
```

### PBK Aktarımı ([[paragraph-coherence]])

Yazım oturumu bitiyorsa ve bölüm tamamlanmadıysa, `DURUM_OZETI.md`'ye şu blok eklenir:

```markdown
## Yazım Bağlamı (Sonraki Oturum İçin)
- Son paragraf (#N): [ana iddia özeti]
- Kullanılan terimler: [liste]
- Açık kalan: [nokta]
- Sonraki paragrafın görevi: [geçiş yönü]
- Argüman İzleyici durumu: [X/Y alt iddia tamamlandı]
```

Sonraki oturum başında AI bu bloğu okur ve PBK'yı yeniden oluşturur.

## Oturum Sınırı Kararları

[[context-management]] oturum sınırı tablosuna bak:

| Durum | Eylem |
|-------|-------|
| Alt bölüm tamamlandı | Kaydet → güncelle → yeni oturum |
| Alt bölüm yarım kaldı | `[DEVAM EDECEK]` etiketi → kaydet |
| Context doluyor | Paragrafta dur → kaydet → yeni oturum |

## MEMORY.md Güncelleme Formatı

```markdown
## Son Güncelleme: [tarih]
- Tamamlanan bölümler: [X/Y]
- Devam eden: [bölüm adı] - [durum]
- Toplam kelime: [X]
- Son dipnot: #[X]
- Sonraki adım: [tam olarak ne yapılacak]
```

## DURUM_OZETI.md Güncelleme

Şablon: [[tpl-status-summary]] — her oturum sonunda bu şablon doldurulur.

Git commit stratejisi için [[git-workflow]] düğümüne bak.
