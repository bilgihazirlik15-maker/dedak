from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
from html import escape
import json,re,shutil
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'godaddy';OUT.mkdir(exist_ok=True)
ASSET_VERSION='20260917-3'
pages=[p for p in json.loads((ROOT/'content/pages.json').read_text(encoding='utf-8')) if 'error' not in p]
assets=json.loads((ROOT/'content/assets.json').read_text(encoding='utf-8'))
by_slug={p['slug']:p for p in pages}
def ascii_slug(s):
    return s.translate(str.maketrans('çğıöşüÇĞİÖŞÜ','cgiosuCGIOSU')).lower()
def filename(s):return ascii_slug(s)+'.html'
def url(s):return filename(s)
def nav_url(s):return f'{url(s)}?v={ASSET_VERSION}'
def esc(s):return escape(str(s),quote=True)
def title(p):
    fixes={'Idari Kadro':'İdari Kadro','Uyelik':'Üyelik','Iletisim':'İletişim','Diger':'Diğer Belgeler','Dedak Ölçütler':'DEDAK Ölçütleri','Akreditasyon Basvurusu':'Akreditasyon Başvurusu','Kısaca Dedak':'Kısaca DEDAK'}
    return fixes.get(p['title'],p['title'])
def local_link(href):
    if href in assets and 'error' not in assets[href]:return assets[href]['file']
    parsed=urlsplit(href)
    if parsed.netloc in ['dedak.org','www.dedak.org']:
        s=unquote(parsed.path).strip('/') or 'index'
        if s=='akreditasyon-ucretleri':s='akreditasyon-ücretleri'
        if s in by_slug:return url(s)
    return href
def icon(name):
    paths={'book':'<path d="M4 5h6a4 4 0 0 1 4 3v14a5 5 0 0 0-4-2H4zM24 5h-6a4 4 0 0 0-4 3v14a5 5 0 0 1 4-2h6z"/>','file':'<path d="M7 3h10l6 6v16H7zM17 3v7h6M11 15h8M11 19h8"/>','shield':'<path d="M14 3 25 7v7c0 6-7 10-11 12C10 24 3 20 3 14V7zM9 14l3 3 7-7"/>','calendar':'<rect x="4" y="6" width="20" height="19" rx="2"/><path d="M9 3v6M19 3v6M4 12h20M9 17h3M16 17h3"/>'}
    return '<svg viewBox="0 0 28 28" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths.get(name,paths['file'])+'</svg>'
nav=[('index','Ana Sayfa'),('hakkinda','Kurumsal'),('akreditasyon','Akreditasyon'),('belgeler','Belgeler'),('duyurular','Duyurular'),('iletisim','İletişim')]
groups={'Kurumsal':[p['slug'] for p in pages[2:12]]+['uyelik'], 'Akreditasyon':[p['slug'] for p in pages[13:22]],'Belgeler':['about-3','about-3-1','about-3-2','about-3-4','about-3-3','sunumlar-ve-yayınlar'],'DEDAK':['duyurular','galeri','iletisim']}
def group_for(s):
    if s=='hakkinda':return 'Kurumsal'
    if s=='akreditasyon':return 'Akreditasyon'
    if s=='belgeler':return 'Belgeler'
    return next((g for g,slugs in groups.items() if s in slugs),'DEDAK')
def header(active):
    menu=[('index','Anasayfa',None),('hakkinda','Hakkında','Kurumsal'),('akreditasyon','Akreditasyon','Akreditasyon'),('uyelik','Üyelik',None),('belgeler','Belgeler','Belgeler'),('sunumlar-ve-yayınlar','Sunumlar ve Yayınlar',None),('duyurular','Duyurular',None)]
    menu_slugs={slug for slug,_,_ in menu}
    entries=[]
    for slug,label,group in menu:
        selected=active==slug
        duplicated_top_level={'Kurumsal':{'uyelik'},'Belgeler':{'sunumlar-ve-yayınlar'}}
        children=[s for s in groups.get(group,[]) if s in by_slug and s!=slug and s not in duplicated_top_level.get(group,set())]
        if children:
            drop=''.join(f'<a href="{nav_url(s)}">{esc(title(by_slug[s]))}</a>' for s in children)
            current=selected or (active not in menu_slugs and group_for(active)==group)
            entries.append(f'<div class="nav-group"><button class="submenu-toggle section-toggle" aria-label="{label} alt menüsü" aria-expanded="false" aria-controls="submenu-{slug}"'+(' aria-current="true"' if current else '')+f'><span>{label}</span></button><div class="submenu" id="submenu-{slug}" hidden>{drop}</div></div>')
        else:
            entries.append(f'<a href="{nav_url(slug)}"'+(' aria-current="page"' if selected else '')+f'>{label}</a>')
    more_current=active in {'galeri','iletisim','site-haritasi'}
    entries.append('<div class="nav-group"><button class="more-toggle submenu-toggle" aria-expanded="false" aria-controls="submenu-more"'+(' aria-current="true"' if more_current else '')+f'>Diğer</button><div class="submenu" id="submenu-more" hidden><a href="galeri.html?v={ASSET_VERSION}">Galeri</a><a href="iletisim.html?v={ASSET_VERSION}">İletişim</a><a href="site-haritasi.html?v={ASSET_VERSION}">Site haritası</a></div></div>')
    return f'<a class="skip" href="#main">İçeriğe geç</a><header class="header"><div class="wrap header-inner"><a class="brand" href="index.html?v={ASSET_VERSION}" aria-label="DEDAK ana sayfa"><img src="assets/dedak-logo-transparent.png?v={ASSET_VERSION}" alt="DEDAK — Dil Eğitimi Değerlendirme ve Akreditasyon Kurulu" width="214" height="83"></a><button class="menu-toggle" aria-controls="navigation" aria-expanded="false">Menü ☰</button><nav class="nav" id="navigation" aria-label="Ana menü">'+''.join(entries)+'</nav></div></header>'
def footer():
    return '<footer class="footer"><div class="wrap"><p class="footer-email"><a href="mailto:info@dedak.org">info@dedak.org</a></p><div class="footer-bottom"><span>© 2026 DEDAK</span><a href="site-haritasi.html">Site haritası</a></div></div></footer>'
def shell(t,body,active='index',description='DEDAK dil eğitimi akreditasyonu, değerlendirme ölçütleri, başvuru bilgileri ve kurumsal belgeler.'):
    return f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#102d4c"><title>{esc(t)} | DEDAK</title><meta name="description" content="{esc(description)}"><link rel="stylesheet" href="assets/site.css?v={ASSET_VERSION}"><script src="assets/site.js?v={ASSET_VERSION}" defer></script></head><body>{header(active)}{body}{footer()}</body></html>'
def homepage():
    text=clean_content(by_slug['duyurular'])
    first_paragraph=BeautifulSoup(text,'html.parser').find('p')
    preview=first_paragraph.get_text(' ',strip=True) if first_paragraph else 'Güncel DEDAK duyurularını inceleyin.'
    slides=[('DEDAK Akreditasyon Başvuruları','duyurular')]
    slide_html=''.join(f'<article class="announcement-slide{" is-active" if i==0 else ""}" aria-roledescription="slide" aria-label="{i+1} / {len(slides)}"><h1><a href="{nav_url(slug)}">{esc(label)}</a></h1></article>' for i,(label,slug) in enumerate(slides))
    carousel='<section class="announcement-banner" data-carousel aria-roledescription="carousel" aria-label="Duyuru slaytları"><div class="announcement-track">'+slide_html+'</div><div class="carousel-controls" hidden><button class="carousel-button carousel-prev" type="button" aria-label="Önceki duyuru">‹</button><div class="carousel-dots" aria-label="Duyuru seçimi"></div><button class="carousel-button carousel-next" type="button" aria-label="Sonraki duyuru">›</button><button class="carousel-pause" type="button" aria-label="Slayt gösterisini duraklat">Duraklat</button></div><p class="visually-hidden carousel-status" aria-live="polite"></p></section>'
    announcement_preview=f'<article class="prose home-announcement announcement-preview"><p class="announcement-excerpt">{esc(preview)}</p><a class="announcement-more" href="{nav_url("duyurular")}">Daha fazla göster</a></article>'
    return '<main id="main" class="wrap home">'+carousel+announcement_preview+'</main>'

def write_home():
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    shutil.copytree(ROOT/'documents',OUT/'documents',dirs_exist_ok=True)
    (OUT/'index.html').write_text(shell('Anasayfa',homepage()),encoding='utf-8')

def resources(p):
    items=[]
    for label,href in p.get('links',[]):
        if href not in assets or 'error' in assets[href]:continue
        meta=assets[href]; name=label
        if re.match(r'^tıkla',label,re.I):name=title(p)
        ext=Path(meta['file']).suffix.lstrip('.').upper()
        size=meta['bytes']/1024
        size_label=f'{size/1024:.1f} MB' if size>1024 else f'{size:.0f} KB'
        items.append(f'<a class="resource" href="{esc(meta["file"])}"><span>{ext}</span><span><b>{esc(name)}</b><small>{size_label} · Aç</small></span></a>')
    return '<div class="resource-list">'+''.join(items)+'</div>' if items else ''

def clean_content(p):
    soup=BeautifulSoup(p.get('html',''),'html.parser')
    for el in list(soup.select('script,style,iframe,input,button,form')):el.decompose()
    for el in list(soup.find_all('span')):el.unwrap()
    for el in list(soup.select('p,h1,h2,h3,h4,h5,h6,div')):
        text=el.get_text(' ',strip=True).replace('\u200b','').strip()
        if not text:el.decompose();continue
        if el.name in ['h1','h4','h5','h6']:el.name='h2'
        if el.name.startswith('h') and text.lower() in [title(p).lower(),p['title'].lower()]:el.decompose()
    for a in soup.select('a[href]'):
        a['href']=local_link(a['href'])
    html=str(soup)
    html=html.replace('17 Kasım 2025 Salı 19:00','17 Kasım 2026 Salı 19:00')
    return html

def without_repeated_accreditation_heading(html):
    soup=BeautifulSoup(html,'html.parser')
    first=soup.find(['h2','p'])
    if first and first.get_text(' ',strip=True).casefold().replace('\u0307','') in {'akreditasyon','accreditation'}:first.decompose()
    return str(soup)

def figures(p):
    return ''.join(f'<figure><a href="{esc(assets[i["url"]]["file"])}" target="_blank" rel="noopener"><img loading="lazy" src="{esc(assets[i["url"]]["file"])}" alt="{esc(i["alt"] or title(p))}"></a><figcaption>{esc(title(p))} — büyütmek için görsele tıklayın.</figcaption></figure>' for i in p.get('images',[]) if i['url'] in assets and 'error' not in assets[i['url']])

def cards(slugs):
    return '<div class="page-cards">'+''.join(f'<a class="page-card" href="{url(s)}"><h2>{esc(title(by_slug[s]))}</h2></a>' for s in slugs if s in by_slug)+'</div>'

def committees():
    s=BeautifulSoup((ROOT/'content/committees-table.html').read_text(encoding='utf-8'),'html.parser')
    sections=[];current=None
    for row in s.select('tbody tr'):
        td=row.find('td')
        if not td:continue
        t=td.get_text(' ',strip=True)
        if not t or t=='DEDAK Kurul/Komisyon ve Üyeleri':continue
        if t.isupper():
            current=[t,[]];sections.append(current)
        elif current:current[1].append(t)
    return '<p>DEDAK kurul, komite ve komisyon üyeleri — 2026.</p>'+''.join('<section><h2>'+esc(h)+'</h2><ul>'+''.join('<li>'+esc(n)+'</li>' for n in names)+'</ul></section>' for h,names in sections)

def application():
    p=by_slug['akreditasyon-başvurusu']
    return '''<div class="notice" id="takvim"><strong>2027 akreditasyon başvuruları</strong><p>Başvuru dönemi: <b>2 Kasım – 1 Aralık 2026</b><br>Kabul edilen programların açıklanması: <b>en geç 4 Ocak 2027</b></p></div><p>Yükseköğretim kurumları bünyesindeki İngilizce hazırlık programları, imzalı ve eksiksiz başvuru formunu son başvuru tarihine kadar <a href="mailto:info@dedak.org">info@dedak.org</a> adresine iletmelidir.</p>'''+resources(p)+'''<h2>Başvuru koşulları</h2><p>Aşağıdaki koşulların başvuru sırasında en az bir yıldır karşılanıyor ve uygulanıyor olması beklenmektedir.</p><ul><li>Programın çıkış seviyesi en az B1+ CEFR düzeyinde olmalıdır. Bu koşul, eğitim dili kısmen İngilizce olan bölümlere yönelik programlar için de geçerlidir.</li><li>Öğrenciler dil seviyelerine göre ayrılmalı; seviyeler arası geçiş, kazanımları ölçen bir değerlendirme sistemiyle yapılmalıdır.</li><li>Bir akademik yılda sınavlar hariç en az 28 hafta ders verilmelidir.</li><li>Programın idari ve akademik birimlerini gösteren bir organizasyon şeması bulunmalıdır.</li><li>Program/materyal geliştirme ve ölçme-değerlendirme birimleri veya komisyonları yapılandırılmış olmalıdır.</li><li>Programın faaliyet süresi en az üç yıl olmalıdır.</li></ul><h2>Değerlendirme ve kabul</h2><p>Başvurular Aralık ayında değerlendirilir. Başvuru sayısı yüksek olduğunda öğrenci sayısı, zorunlu hazırlık oranı ve hazır bulunuşluk gibi formda yer alan bilgilerle önceliklendirme yapılır. İlk 10 program asil, diğer programlar yedek olarak belirlenir.</p><p>Asil programlardan biri çekilirse yedek programlar sıralamaya göre sürece dahil edilir. Aksi halde bir sonraki yılın başvurularında öncelik verilir.</p><h2>Ücretler ve hazırlık belgeleri</h2><p>2027 dönemi ücretlerinin Kasım ayı başında enflasyon oranında güncellenmesi öngörülmektedir. <a href="akreditasyon-ucretleri.html">Ücret bilgilerini</a> ve <a href="akreditasyon-sureci.html">süreç kılavuzlarını</a> inceleyin.</p><h2>Çevrimiçi bilgilendirme toplantısı</h2><p>17 Kasım 2026 Salı, saat 19.00. Zoom toplantı kimliği: <strong>933 1849 4529</strong>.</p><p class="help">Katılım öncesinde toplantı bilgisini DEDAK ile teyit edebilirsiniz.</p><details><summary>Başvuru duyurusunun tam metni</summary><div>'''+clean_content(p)+'''</div></details>'''

def contact():
    return '''<div class="contact-grid"><section class="contact-card"><h2>E-posta</h2><p>Akreditasyon, başvuru ve kurumsal konulardaki sorularınız için:</p><a class="text-link" href="mailto:info@dedak.org">info@dedak.org</a></section><section class="contact-card"><h2>Adres</h2><p>Merkez Mah. Abide-i Hürriyet Cd.<br>Sibel Ap. No:161 Kat:2 Daire:3<br>Şişli / İstanbul</p></section></div><section class="contact-form"><h2>Bize yazın</h2><p>Form, mesajınızı e-posta uygulamanızda taslak olarak açar. Gönderimi açılan uygulamadan tamamlayabilirsiniz.</p><form id="contact-form"><div class="field-row"><div class="field"><label for="name">Ad soyad</label><input id="name" name="name" autocomplete="name" maxlength="120" required></div><div class="field"><label for="email">E-posta adresi</label><input id="email" name="email" type="email" autocomplete="email" maxlength="180" required></div></div><div class="field"><label for="subject">Konu</label><input id="subject" name="subject" maxlength="180" required></div><div class="field"><label for="message">Mesajınız</label><textarea id="message" name="message" maxlength="3000" required></textarea></div><p class="help">Bu form mesajınızı sunucuya kaydetmez. Çalışması için cihazınızda bir e-posta uygulaması tanımlı olmalıdır.</p><button class="button" type="submit">E-posta taslağı oluştur</button><p id="form-status" class="help" role="status" aria-live="polite"></p></form></section>'''

def university_map(lang):
    en=lang=='en'
    locations=json.loads((ROOT/'content/university-map.json').read_text(encoding='utf-8'))
    points=[];popups=[]
    for location in locations:
        name=location['name'];city=location['city_en' if en else 'city_tr'];identifier=location['id']
        x=(location['lon']-25.5)/20*100;y=(43-location['lat'])/9*100
        point_label=(f'Show {name}' if en else f'{name} bağlantısını göster')
        points.append(f'<button class="map-point" type="button" data-map-point data-label="{esc(name)}" aria-label="{esc(point_label)}" aria-expanded="false" aria-controls="map-popup-{identifier}" style="--map-x:{x:.2f}%;--map-y:{y:.2f}%"></button>')
        links=f'<li><a href="{esc(location["url"])}">{esc(name)}</a></li>'
        close_label='Close' if en else 'Kapat'
        popups.append(f'<div class="map-popup" id="map-popup-{identifier}" role="group" aria-label="{esc(name)}" hidden><button class="map-popup-close" type="button" data-map-popup-close aria-label="{close_label}">×</button><h3>{esc(city)}</h3><ul>{links}</ul></div>')
    title='Accredited Universities Map' if en else 'Akredite Üniversiteler Haritası'
    help_text='Select a university point to open its link.' if en else 'Bağlantısını görmek için bir üniversite noktasını seçin.'
    note='Nearby points are spaced apart for readability. Eastern Mediterranean University is shown in Famagusta, Cyprus.' if en else 'Yakın noktalar okunabilirlik için birbirinden ayrılmıştır. Doğu Akdeniz Üniversitesi, Gazimağusa/Kıbrıs noktasında gösterilmiştir.'
    source=('Province boundaries: <a href="https://data.humdata.org/dataset/cod-ab-tur">OCHA/HDX COD-AB-TUR</a> (CC BY-IGO).' if en else 'İl sınırları: <a href="https://data.humdata.org/dataset/cod-ab-tur">OCHA/HDX COD-AB-TUR</a> (CC BY-IGO).')
    close_label='Close map' if en else 'Haritayı kapat'
    return f'<dialog class="university-map-dialog" data-university-map aria-labelledby="university-map-title"><div class="map-dialog-header"><div><span class="map-kicker">DEDAK</span><h2 id="university-map-title">{title}</h2></div><button class="map-dialog-close" type="button" data-map-close aria-label="{close_label}">×</button></div><p class="map-help">{help_text}</p><div class="map-board"><div class="map-stage"><img src="assets/turkey-map.svg?v={ASSET_VERSION}" alt="" aria-hidden="true">'+''.join(points)+'</div><div class="map-popup-layer">'+''.join(popups)+f'</div></div><p class="map-note">{note} {source}</p></dialog>'

def program_records(p,lang='tr'):
    records=json.loads((ROOT/'content/programs.json').read_text(encoding='utf-8'))
    en=lang=='en'
    intro=('<p>English preparatory programs accredited by DEDAK and their evaluation periods. To see the universities on a map, <button type="button" class="map-inline-trigger" data-map-open>click here</button>.</p>' if en else '<p>DEDAK tarafından akreditasyon verilen İngilizce hazırlık programları ve değerlendirme dönemleri. Üniversiteleri harita üzerinde görmek için <button type="button" class="map-inline-trigger" data-map-open>tıklayın</button>.</p>')
    translations={'Yabancı Diller Yüksekokulu İngilizce Hazırlık Programı':'School of Foreign Languages English Preparatory Program','Yabancı Diller Yüksekokulu Hazırlık Programı':'School of Foreign Languages Preparatory Program','Temel İngilizce Bölümü':'Department of Basic English','İngilizce Hazırlık Programı':'English Preparatory Program','İngilizce Hazırlık Programı — Lisans':'English Preparatory Program — Undergraduate','Zorunlu İngilizce Hazırlık Programı':'Compulsory English Preparatory Program'}
    items=[]
    for number,name,program,evaluation,period in records:
        label=translations.get(program,program) if en else program
        items.append('<tr><th scope="row"><div class="program-identity"><b class="program-index">'+esc(number)+'</b><div><strong>'+esc(name)+'</strong><small>'+esc(label)+'</small></div></div></th><td data-label="'+('Last evaluation period' if en else 'Son değerlendirme dönemi')+'">'+esc(evaluation)+'</td><td data-label="'+('Accreditation validity' if en else 'Akreditasyon geçerlilik süresi')+'">'+esc(period)+'</td></tr>')
    headings=('<th scope="col">University and program</th><th scope="col">Last evaluation period</th><th scope="col">Accreditation validity</th>' if en else '<th scope="col">Üniversite ve program</th><th scope="col">Son değerlendirme dönemi</th><th scope="col">Akreditasyon geçerlilik süresi</th>')
    table='<div class="program-table-wrap"><table class="program-table"><colgroup><col style="width:51%"><col style="width:19%"><col style="width:30%"></colgroup><thead><tr>'+headings+'</tr></thead><tbody>'+''.join(items)+'</tbody></table></div>'
    summary='View the original program list' if en else 'Orijinal program listesini görüntüle'
    return intro+table+university_map(lang)+'<details hidden><summary>'+summary+'</summary>'+figures(p)+'</details>'

def institutions_table():
    institutions=json.loads((ROOT/'content/in-progress-institutions.json').read_text(encoding='utf-8'))
    rows=''.join('<tr><td>'+esc(name)+'</td><td>Şubat / February '+str(year)+'</td></tr>' for name,year in institutions)
    return '<div class="institution-table-wrap"><table class="institution-table"><colgroup><col style="width:65%"><col style="width:35%"></colgroup><thead><tr><th scope="col">Akreditasyon Sürecinde Olan Kurumlar<br><span>Institutions in the Process of Accreditation</span></th><th scope="col">Süreç Başlangıç Tarihi<br><span>Beginning Date of Process</span></th></tr></thead><tbody>'+rows+'</tbody></table></div>'

def presentation_table(p,lang='tr'):
    en=lang=='en'
    entries=BeautifulSoup(p.get('html',''),'html.parser').select('li')
    assert len(entries)==12, 'Presentation and publication source list changed'
    years=['2023','','','2013','2014','2015','2016','2017','2018','2018','2019','2019']
    rows=[]
    for index,(entry,year) in enumerate(zip(entries,years)):
        name=entry.get_text(' ',strip=True).replace('D irectors','Directors').replace('Octovber','October').replace('20-21October','20-21 October')
        link=entry.find('a',href=True)
        href=link['href'] if link else ''
        if index==11:href='https://link.springer.com/book/10.1007/978-3-030-21421-0'
        if href:href=local_link(href)
        kind=('Publication' if index==11 else 'Presentation' if index<3 else 'Event record') if en else ('Yayın' if index==11 else 'Sunum' if index<3 else 'Etkinlik kaydı')
        label=esc(name)
        title_html=f'<a class="publication-title-link" href="{esc(href)}">{label}</a>' if href else f'<span class="publication-title-text">{label}</span>'
        if href:
            extension=Path(urlsplit(href).path).suffix.upper().lstrip('.')
            action=('Open '+extension if en else extension+' aç') if extension in {'PDF','PPTX'} else ('View page' if en else 'Sayfayı aç')
            action_html=f'<a class="publication-action" href="{esc(href)}">{action}</a>'
        else:action_html='<span class="publication-unavailable">Link not published</span>' if en else '<span class="publication-unavailable">Bağlantı yayımlanmamış</span>'
        rows.append(f'<tr><td data-label="{("Type" if en else "Tür")}"><span class="publication-kind">{kind}</span></td><th scope="row">{title_html}</th><td data-label="{("Year" if en else "Yıl")}">{year or "—"}</td><td data-label="{("Link" if en else "Bağlantı")}">{action_html}</td></tr>')
    headings=('<th scope="col">Type</th><th scope="col">Presentation or publication</th><th scope="col">Year</th><th scope="col">Link</th>' if en else '<th scope="col">Tür</th><th scope="col">Sunum veya yayın</th><th scope="col">Yıl</th><th scope="col">Bağlantı</th>')
    summary=('<p class="publication-summary">12 records. Available files and web pages open in a new tab.</p>' if en else '<p class="publication-summary">12 kayıt. Mevcut dosyalar ve web sayfaları yeni sekmede açılır.</p>')
    return summary+'<div class="publication-table-wrap"><table class="publication-table"><thead><tr>'+headings+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

def content_for(p):
    s=p['slug']
    if s=='hakkinda':return '<p>DEDAK’ın kuruluşu, yönetimi, kalite yaklaşımı ve stratejik hedefleri.</p>'+cards(groups['Kurumsal'])+'<h2>Kurumsal belge</h2>'+resources(p)
    if s=='akreditasyon':return without_repeated_accreditation_heading(clean_content(p))+cards(groups['Akreditasyon'])
    if s=='belgeler':return '<p>Akreditasyon çalışmalarında kullanılan belgeler, kurumsal düzenlemeler ve başvuru formları.</p>'+cards(groups['Belgeler'])+'<h2>Akreditasyon için temel belgeler</h2>'+resources(by_slug['akreditasyon-süreci'])
    if s=='akreditasyon-başvurusu':return application()
    if s=='duyurular':return '<span class="eyebrow">2027 akreditasyon dönemi</span><h2>DEDAK akreditasyon başvuruları</h2><p>2027 başvuruları 2 Kasım – 1 Aralık 2026 tarihleri arasında kabul edilecektir.</p><p><a class="button" href="akreditasyon-basvurusu.html">Başvuru rehberini inceleyin</a></p>'+clean_content(p)+resources(p)
    if s=='kurucu-kurul':return committees()
    if s=='akredite-edilen-programlar':return program_records(p)
    if s=='sunumlar-ve-yayınlar':return presentation_table(p)
    if s=='iletisim':return contact()
    if s=='galeri':return '<div class="notice"><h2>DEDAK etkinlik arşivi</h2><p>Etkinlik fotoğrafları için DEDAK ile iletişime geçebilirsiniz.</p><a class="button" href="iletisim.html">İletişim</a></div>'
    if s in ['about-3','about-3-1','about-3-2','about-3-4','about-3-3','dedak-ölçütler','akreditasyon-süreci']:return resources(p)
    if s=='akreditasyon-ücretleri':return '<div class="notice">2027 başvuruları için ücretlerin Kasım ayı başında güncellenmesi öngörülmektedir. Aşağıdaki mevcut ücret tablosunu başvuru öncesinde DEDAK ile teyit edin.</div>'+figures(p)+clean_content(p)
    if s=='akreditasyon-sürecinde-olan-kurumlar':return institutions_table()
    if s in ['akredite-edilen-programlar','organizasyon-semasi']:return figures(p)+clean_content(p)
    return clean_content(p)+figures(p)+resources(p)

def inner(p):
    page_class='wrap inner-page institutions-page' if p['slug']=='akreditasyon-sürecinde-olan-kurumlar' else 'wrap inner-page'
    if p['slug']=='akredite-edilen-programlar':page_class='wrap inner-page programs-page'
    if p['slug']=='sunumlar-ve-yayınlar':page_class='wrap inner-page publications-page'
    return '<main id="main" class="'+page_class+'"><h1 class="page-title">'+esc(title(p))+'</h1><article class="prose">'+content_for(p)+'</article></main>'

def open_content_links_in_new_tabs():
    for path in OUT.rglob('*.html'):
        soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
        for link in soup.select('a[href]'):
            href=link['href'];parsed=urlsplit(href)
            if link.find_parent(class_='language-switch') or (not parsed.path and parsed.fragment) or parsed.scheme in {'mailto','tel','javascript','data'}:continue
            link['target']='_blank'
            link['rel']=sorted(set(link.get('rel',[]))|{'noopener','noreferrer'})
            link.attrs.pop('download',None)
        path.write_text(str(soup),encoding='utf-8')

def build_all():
    write_home()
    for p in pages:
        if p['slug']=='index':continue
        active={'Kurumsal':'hakkinda','Akreditasyon':'akreditasyon','Belgeler':'belgeler'}.get(group_for(p['slug']),p['slug'])
        if p['slug'] in ['uyelik','sunumlar-ve-yayınlar']:active=p['slug']
        desc=BeautifulSoup(p.get('html',''),'html.parser').get_text(' ',strip=True)[:160] or title(p)+' — DEDAK kurumsal web sitesi.'
        (OUT/filename(p['slug'])).write_text(shell(title(p),inner(p),active,desc),encoding='utf-8')
    sitemap_content='<main id="main" class="wrap section"><h1>Site haritası</h1>'
    for g,slugs in groups.items():sitemap_content+=f'<h2>{g}</h2>'+cards(slugs)
    sitemap_content+='</main>'
    (OUT/'site-haritasi.html').write_text(shell('Site haritası',sitemap_content,'site-haritasi'),encoding='utf-8')
    notfound='<main class="wrap section" id="main"><h1>Bu sayfa bulunamadı.</h1><p>Aradığınız içeriğe ana sayfadan veya site haritasından ulaşabilirsiniz.</p><a class="button" href="index.html">Ana sayfaya dön</a></main>'
    (OUT/'404.html').write_text(shell('Sayfa bulunamadı',notfound,''),encoding='utf-8')
    ht=['# GoDaddy Linux / cPanel Apache hosting','DirectoryIndex index.html','AddDefaultCharset UTF-8','ErrorDocument 404 /404.html','<IfModule mod_rewrite.c>','RewriteEngine On']
    for p in pages:
        if p['slug']=='index':continue
        variants={p['slug'],ascii_slug(p['slug'])}
        for v in sorted(variants):ht.append('RewriteRule ^'+re.escape(v)+'/?$ '+filename(p['slug'])+' [R=301,L,NE]')
    for href,meta in assets.items():
        if '/_files/ugd/' in href and 'error' not in meta:ht.append('RewriteRule ^'+re.escape(unquote(urlsplit(href).path.lstrip('/')))+'$ '+meta['file']+' [R=301,L,NE]')
    ht+=['</IfModule>','<IfModule mod_deflate.c>','AddOutputFilterByType DEFLATE text/html text/css application/javascript','</IfModule>']
    (OUT/'.htaccess').write_text('\n'.join(ht)+'\n',encoding='utf-8')
    urls=[f'https://www.dedak.org/{filename(p["slug"])}' for p in pages]+['https://www.dedak.org/site-haritasi.html']
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{esc(u)}</loc></url>' for u in urls)+'</urlset>',encoding='utf-8')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://www.dedak.org/sitemap.xml\n',encoding='utf-8')
    from bilingual import add_languages
    add_languages(OUT,globals())
    open_content_links_in_new_tabs()
    app=ROOT/'site-source/app'
    if app.exists():
        html=BeautifulSoup((OUT/'index.html').read_text(encoding='utf-8'),'html.parser')
        (app/'home-content.ts').write_text('export const homeContent = '+json.dumps(html.body.decode_contents(),ensure_ascii=False)+';\n',encoding='utf-8')
        (app/'globals.css').write_text((ROOT/'assets/site.css').read_text(encoding='utf-8'),encoding='utf-8')
        shutil.copytree(OUT,ROOT/'site-source/public',dirs_exist_ok=True)
    print(f'Built {len(list(OUT.rglob("*.html")))} HTML pages. Assets: {len(assets)}.')

if __name__=='__main__':build_all()
