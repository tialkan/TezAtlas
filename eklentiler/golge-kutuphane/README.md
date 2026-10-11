# Gölge kütüphane eklentisi (isteğe bağlı)

Bu eklenti TezAtlas'ın varsayılan kurulumunda **yoktur**. Varsayılan kaynak edinme sırası yalnız yasal kanallardan oluşur: `skills/tooling/open-access-chain.md`.

Anna's Archive, Sci-Hub ve benzeri sitelerin kullanımı birçok ülkede ve üniversitede telif hukukuna ya da kurum politikasına aykırıdır. Bu eklentiyi kurmadan önce kendi ülkenizin mevzuatını ve kurumunuzun kurallarını kontrol edin. Kurulum ve kullanım tümüyle kullanıcının sorumluluğundadır.

## Kurulum

```bash
python3 scripts/install_plugin.py eklentiler/golge-kutuphane
```

Eklenti `skills/community/golge-kutuphane/` altına kopyalanır. Bu klasör git'e eklenmez.

## Kaldırma

`skills/community/golge-kutuphane/` klasörünü silmeniz yeterlidir.

## Not

Eski sürümlerin sözünü ettiği `scripts/annas_archive_helper.sh` betiği bu repoda hiç bulunmadı; düğüm elle arama adımlarını anlatır.
