# DEDAK

DEDAK web sitesinin orijinal tasarımına yakın, mobil ekranlara uyarlanmış Türkçe sürümü. Beyaz zemin, mevcut logo, gri yatay menü ve lacivert duyuru alanı korunmuştur.

## Kullanım

- Bilgisayarınızda açmak için depoyu indirin ve `godaddy/index.html` dosyasını tarayıcıda açın.
- Yayına hazır dosyalar: [godaddy](godaddy/)
- GoDaddy’ye yüklenebilir paket: [DEDAK-GoDaddy.zip](DEDAK-GoDaddy.zip)
- Ayrıntılı yönerge: [GoDaddy kurulum rehberi](GODADDY-KURULUM.md)

35 HTML sayfası ve 33 indirilebilir belge içerir. Yayın sürümü veritabanı veya Node.js sunucusu gerektirmez. GoDaddy Web Hosting / cPanel için hazırlanmıştır.

## Kaynaklardan üretme

Python 3.12 veya üzeri ile:

```sh
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/verify.py
python scripts/package.py
```

İsteğe bağlı geliştirme projesi `site-source` klasöründedir:

```sh
cd site-source
npm ci
npm run dev
```

`python scripts/build.py`, içerikleri ve ortak tasarımı hem yayın klasörüne hem geliştirme projesine aktarır. GoDaddy’ye yalnızca `godaddy` klasörünün içeriği veya hazır ZIP yüklenir.

## İçerik ve sınırlar

- İçerikler [dedak.org](https://www.dedak.org/) sitesinin 7 Eylül 2026 tarihindeki Türkçe içeriğinden aktarılmıştır.
- İletişim formu e-posta uygulamasında taslak açar; sunucu üzerinden otomatik gönderim yapmaz.
- Eski galerinin fotoğraflarına erişilemediğinden galeri fotoğrafları dahil değildir.
- Ücretler, toplantı bilgileri ve akreditasyon geçerlilikleri yayına alınmadan önce kurum tarafından kontrol edilmelidir.
- Türkçe karakterler, yerel bağlantılar ve belge dosya biçimleri kontrol edilmiştir. Tarayıcı etkileşim testi ve gerçek GoDaddy sunucu testi yapılmamıştır.

Kurum logosu, belgeler ve kaynak içerikler ilgili hak sahiplerine aittir. Bu depo ayrıca bir yeniden kullanım lisansı vermez.
