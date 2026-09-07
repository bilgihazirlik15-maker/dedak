# DEDAK — GoDaddy’ye aktarım

Hazırlanan site HTML, CSS ve JavaScript dosyalarından oluşur. Veritabanı, Node.js veya ücretli eklenti gerektirmez. Hazır yayın dosyaları `godaddy` klasöründedir; aynı içerik `DEDAK-GoDaddy.zip` paketinde bulunur.

Tasarım, kullanıcının isteğiyle orijinal DEDAK düzenine yaklaştırıldı: beyaz zemin, solda mevcut logo, gri yatay ve alt açılır menüler, lacivert duyuru alanı ve sade metin sayfaları. İlk tasarımdaki tanıtım bölümleri kaldırıldı.

## Bilgisayarınızda açma

`godaddy/index.html` dosyasına çift tıklayın. Sayfalar, belgeler, tasarım ve menü yerel dosyalarla çalışır. İletişim e-posta taslağını cihazınızdaki e-posta uygulamasında açar. Harici yayın bağlantıları internet gerektirir.

## GoDaddy Web Hosting / cPanel

1. GoDaddy hesabınızda **Web Hosting (cPanel)** ürünü bulunduğunu kontrol edin. Bu yönerge cPanel barındırma içindir; yalnızca alan adı sahibi olmak yeterli değildir. Websites + Marketing veya Managed WordPress kullanıyorsanız bu paketin yükleme yöntemi aynı olmayabilir.
2. Ürünlerim → Web Hosting → Yönet → cPanel Admin → File Manager bölümüne girin.
3. Mevcut yayın dosyalarının yedeğini alın. Ana alan adının kök klasörü genellikle `public_html` olur. Ek alan adında cPanel Domains bölümünde belirtilen belge kökünü kullanın.
4. `DEDAK-GoDaddy.zip` dosyasını bu klasöre yükleyip **Extract** ile açın. `index.html`, `assets`, `documents` ve `.htaccess` doğrudan alan adının kökünde olmalıdır. Araya ikinci bir `godaddy` klasörü koymayın.
5. Mevcut bir `.htaccess` varsa kurallarını yedekleyip bu paketteki kurallarla birlikte değerlendirin. Paketteki dosya UTF-8, ana sayfa, eski sayfa/belge bağlantılarının yönlendirmeleri ve sıkıştırma ayarlarını içerir. Diğer uygulamaların kurallarını körlemesine değiştirmeyin.
6. Alan adı doğru hosting hesabına bağlı olduğunda HTTPS ile ana sayfayı, birkaç alt sayfayı ve bir belge indirmeyi kontrol edin. Alan adının halen Wix’e yönelmesi durumunda DNS aktarımı ayrıca yapılmalıdır. Bu çalışma sırasında DNS veya canlı site değiştirilmedi.
7. Son kontrolde iletişim formunun e-posta uygulamasında taslak açtığını ve mobil menünün kullanılabildiğini doğrulayın.

Resmî GoDaddy yönergeleri: [Dosya yükleme](https://www.godaddy.com/en-in/help/upload-files-using-my-web-hosting-cpanel-file-manager-3239), [Web kök klasörü](https://dk.godaddy.com/help/what-is-my-websites-root-directory-in-my-web-hosting-cpanel-account-16187?lc=en-US).

## İçerik düzenleme

Doğrudan `godaddy` içindeki HTML dosyalarını bir metin düzenleyiciyle değiştirebilirsiniz. Ortak tasarım `godaddy/assets/site.css`, menü ve e-posta taslağı davranışı `godaddy/assets/site.js` içindedir. Yönetim paneli yoktur.

Geliştirici için: tekrar üretilebilir kaynaklar `scripts`, `content`, `assets` ve `documents` klasörlerindedir. Python 3.12+ ve `beautifulsoup4` ile `python scripts/build.py`, ardından `python scripts/verify.py` çalıştırılır. Bu işlem doğrudan HTML üzerinde yapılan değişiklikleri kaynaklardan yeniden üretir; kalıcı değişiklikler kaynaklara da işlenmelidir. `site-source` isteğe bağlı Sites geliştirme projesidir; GoDaddy’ye yüklenmez. Burada `npm run build` derleme doğrulaması yapılmıştır.

## Teslim notları

- 70 HTML sayfası (Türkçe ve İngilizce için 35’er sayfa), 53 indirilebilir belge, kurum logosu ve mevcut tablo/şema görselleri pakete dahil edildi.
- Kaynak: [DEDAK](https://www.dedak.org/), 7 Eylül 2026 tarihinde incelendi. Kurul listesi kaynak sitedeki herkese açık 2026 tablosundan aktarıldı.
- İlk arama çıktısında başvuru sayfasının 2026 dönemine ait önbellekli sürümü görünüyordu. Doğrudan site kontrolünde 2027 duyurusu doğrulandı ve yeni sayfalarda bu içerik kullanıldı. Kaynaktaki toplantı başlığı “17 Kasım 2025” yazarken açıklama 17 Kasım 2026 diyordu; yeni sürümde yıl açıklamayla tutarlı hale getirildi. Toplantı bilgisi yayın öncesinde teyit edilmeli.
- Eski Wix galeri bileşeni fotoğraf içeriği döndürmedi; doğrudan kaynak ve tarayıcı incelemesinde de fotoğraflara erişilemedi. Galeri fotoğrafları pakette yoktur. Galeri sayfasında iletişim yönlendirmesi vardır; fotoğraflar sağlandığında gerçek galeri eklenebilir.
- İletişim formu otomatik e-posta göndermez. E-posta uygulamasında taslak oluşturur. Gerçek sunucu üzerinden gönderim için sonradan SMTP veya form servisi entegrasyonu gerekir.
- Kurumsal belgeler ve tablolar kaynak tarihindeki durumlarıyla korunmuştur. Akreditasyon kayıtlarındaki geçmiş dönemler silinmemiştir; Manisa Celal Bayar Üniversitesi’nin iki dönemi ayrı kayıtlardır. Ücretler, program geçerlilikleri ve toplantı bilgileri kurum tarafından yayın öncesinde gözden geçirilmelidir.
- Sol üstteki bayraklı TR/EN anahtarı aynı sayfanın diğer dildeki sürümüne geçer. İngilizce sayfalar `en` klasöründe yer alır. İçerikler kaynak sitenin İngilizce sürümünden aktarıldı; Türkçe kalan metinler çevrildi. Belgeler ve kaynak görseller özgün dillerinde korunmuştur.
- Kontrol: 3.642 yerel sayfa/varlık bağlantısı, 70 sayfanın dil eşleşmeleri ve belge dosya imzaları doğrulandı; JavaScript sözdizimi ve Sites üretim derlemesi başarılı. Tarayıcıda görsel/etkileşim testi ve gerçek GoDaddy sunucu testi yapılmadı. Ayrıntılar `content/validation.json` dosyasındadır.
