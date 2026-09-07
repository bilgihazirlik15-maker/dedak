from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
from html import escape
import json,re,shutil
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'godaddy';OUT.mkdir(exist_ok=True)
pages=[p for p in json.loads((ROOT/'content/pages.json').read_text(encoding='utf-8')) if 'error' not in p]
assets=json.loads((ROOT/'content/assets.json').read_text(encoding='utf-8'))
by_slug={p['slug']:p for p in pages}
def ascii_slug(s):
    return s.translate(str.maketrans('çğıöşüÇĞİÖŞÜ','cgiosuCGIOSU')).lower()
def filename(s):return ascii_slug(s)+'.html'
def url(s):return filename(s)
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
ARROW='<span class="arrow" aria-hidden="true">↗</span>'
nav=[('index','Ana Sayfa'),('hakkinda','Kurumsal'),('akreditasyon','Akreditasyon'),('belgeler','Belgeler'),('duyurular','Duyurular'),('iletisim','İletişim')]
groups={'Kurumsal':[p['slug'] for p in pages[2:12]]+['uyelik'], 'Akreditasyon':[p['slug'] for p in pages[13:22]],'Belgeler':['about-3','about-3-1','about-3-2','about-3-4','about-3-3','sunumlar-ve-yayınlar'],'DEDAK':['duyurular','galeri','iletisim']}
def group_for(s):
    if s=='hakkinda':return 'Kurumsal'
    if s=='akreditasyon':return 'Akreditasyon'
    if s=='belgeler':return 'Belgeler'
    return next((g for g,slugs in groups.items() if s in slugs),'DEDAK')
def header(active):
    menu=[('index','Anasayfa',None),('hakkinda','Hakkında','Kurumsal'),('akreditasyon','Akreditasyon','Akreditasyon'),('uyelik','Üyelik',None),('belgeler','Belgeler','Belgeler'),('sunumlar-ve-yayınlar','Sunumlar ve Yayınlar',None),('duyurular','Duyurular',None)]
    entries=[]
    for slug,label,group in menu:
        selected=active==slug
        link=f'<a href="{url(slug)}"'+(' aria-current="page"' if selected else '')+f'>{label}</a>'
        children=[s for s in groups.get(group,[]) if s in by_slug and s!=slug]
        if children:
            drop=''.join(f'<a href="{url(s)}">{esc(title(by_slug[s]))}</a>' for s in children)
            entries.append(f'<div class="nav-group">{link}<button class="submenu-toggle" aria-label="{label} alt menüsü" aria-expanded="false" aria-controls="submenu-{slug}">⌄</button><div class="submenu" id="submenu-{slug}" hidden>{drop}</div></div>')
        else:entries.append(link)
    entries.append('<div class="nav-group"><button class="more-toggle submenu-toggle" aria-expanded="false" aria-controls="submenu-more">Diğer ⌄</button><div class="submenu" id="submenu-more" hidden><a href="galeri.html">Galeri</a><a href="iletisim.html">İletişim</a><a href="site-haritasi.html">Site haritası</a></div></div>')
    return '<a class="skip" href="#main">İçeriğe geç</a><header class="header"><div class="wrap header-inner"><a class="brand" href="index.html" aria-label="DEDAK ana sayfa"><img src="assets/dedak-logo.jpg" alt="DEDAK — Dil Eğitimi Değerlendirme ve Akreditasyon Kurulu" width="214" height="83"></a><button class="menu-toggle" aria-controls="navigation" aria-expanded="false">Menü ☰</button><nav class="nav" id="navigation" aria-label="Ana menü">'+''.join(entries)+'</nav></div></header>'
def footer():
    return '<footer class="footer"><div class="wrap"><p class="footer-email"><a href="mailto:info@dedak.org">e-mail: info@dedak.org</a></p><div class="footer-bottom"><span>© 2026 DEDAK</span><a href="site-haritasi.html">Site haritası</a></div></div></footer>'
def shell(t,body,active='index',description='DEDAK dil eğitimi akreditasyonu, değerlendirme ölçütleri, başvuru bilgileri ve kurumsal belgeler.'):
    return f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#102d4c"><title>{esc(t)} | DEDAK</title><meta name="description" content="{esc(description)}"><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script></head><body>{header(active)}{body}{footer()}</body></html>'
def homepage():
    text=clean_content(by_slug['duyurular'])
    return '<main id="main" class="wrap home"><section class="announcement-banner" aria-labelledby="announcement-title"><h1 id="announcement-title"><a href="duyurular.html">DEDAK Akreditasyon Başvuruları</a></h1></section><article class="prose home-announcement">'+text+resources(by_slug['akreditasyon-başvurusu'])+'</article></main>'

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
        items.append(f'<a class="resource" href="{esc(meta["file"])}" download><span>{ext}</span><span><b>{esc(name)}</b><small>{size_label} · İndir</small></span>{ARROW}</a>')
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

def figures(p):
    return ''.join(f'<figure><a href="{esc(assets[i["url"]]["file"])}" target="_blank" rel="noopener"><img loading="lazy" src="{esc(assets[i["url"]]["file"])}" alt="{esc(i["alt"] or title(p))}"></a><figcaption>{esc(title(p))} — büyütmek için görsele tıklayın.</figcaption></figure>' for i in p.get('images',[]) if i['url'] in assets and 'error' not in assets[i['url']])

def cards(slugs):
    return '<div class="page-cards">'+''.join(f'<a class="page-card" href="{url(s)}"><h2>{esc(title(by_slug[s]))}</h2>{ARROW}</a>' for s in slugs if s in by_slug)+'</div>'

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
    return '''<div class="contact-grid"><section class="contact-card"><h2>E-posta</h2><p>Akreditasyon, başvuru ve kurumsal konulardaki sorularınız için:</p><a class="text-link" href="mailto:info@dedak.org">info@dedak.org ↗</a></section><section class="contact-card"><h2>Adres</h2><p>Merkez Mah. Abide-i Hürriyet Cd.<br>Sibel Ap. No:161 Kat:2 Daire:3<br>Şişli / İstanbul</p></section></div><section class="contact-form"><h2>Bize yazın</h2><p>Form, mesajınızı e-posta uygulamanızda taslak olarak açar. Gönderimi açılan uygulamadan tamamlayabilirsiniz.</p><form id="contact-form"><div class="field-row"><div class="field"><label for="name">Ad soyad</label><input id="name" name="name" autocomplete="name" maxlength="120" required></div><div class="field"><label for="email">E-posta adresi</label><input id="email" name="email" type="email" autocomplete="email" maxlength="180" required></div></div><div class="field"><label for="subject">Konu</label><input id="subject" name="subject" maxlength="180" required></div><div class="field"><label for="message">Mesajınız</label><textarea id="message" name="message" maxlength="3000" required></textarea></div><p class="help">Bu form mesajınızı sunucuya kaydetmez. Çalışması için cihazınızda bir e-posta uygulaması tanımlı olmalıdır.</p><button class="button" type="submit">E-posta taslağı oluştur ↗</button><p id="form-status" class="help" role="status" aria-live="polite"></p></form></section>'''

def program_records(p):
    records=json.loads((ROOT/'content/programs.json').read_text(encoding='utf-8'))
    intro='<p>DEDAK tarafından akreditasyon verilen İngilizce hazırlık programları ve değerlendirme dönemleri.</p><div class="notice">Liste geçmiş dönem kayıtlarını da içerir. Her programın akreditasyon geçerlilik tarihini ilgili kayıttan kontrol edin.</div>'
    items=[]
    for number,name,program,evaluation,period in records:
        items.append(f'<section class="program-record"><span class="eyebrow">Program {esc(number)}</span><h2>{esc(name)}</h2><p>{esc(program)}</p><dl><div><dt>Son değerlendirme dönemi</dt><dd>{esc(evaluation)}</dd></div><div><dt>Akreditasyon geçerlilik süresi</dt><dd>{esc(period)}</dd></div></dl></section>')
    return intro+''.join(items)+'<details><summary>Orijinal program listesini görüntüle</summary>'+figures(p)+'</details>'

def content_for(p):
    s=p['slug']
    if s=='hakkinda':return '<p>DEDAK’ın kuruluşu, yönetimi, kalite yaklaşımı ve stratejik hedefleri.</p>'+cards(groups['Kurumsal'])+'<h2>Kurumsal belge</h2>'+resources(p)
    if s=='akreditasyon':return clean_content(p)+cards(groups['Akreditasyon'])
    if s=='belgeler':return '<p>Akreditasyon çalışmalarında kullanılan belgeler, kurumsal düzenlemeler ve başvuru formları.</p>'+cards(groups['Belgeler'])+'<h2>Akreditasyon için temel belgeler</h2>'+resources(by_slug['akreditasyon-süreci'])
    if s=='akreditasyon-başvurusu':return application()
    if s=='duyurular':return '<span class="eyebrow">2027 akreditasyon dönemi</span><h2>DEDAK akreditasyon başvuruları</h2><p>2027 başvuruları 2 Kasım – 1 Aralık 2026 tarihleri arasında kabul edilecektir.</p><p><a class="button" href="akreditasyon-basvurusu.html">Başvuru rehberini inceleyin ↗</a></p>'+clean_content(p)+resources(p)
    if s=='kurucu-kurul':return committees()
    if s=='akredite-edilen-programlar':return program_records(p)
    if s=='iletisim':return contact()
    if s=='galeri':return '<div class="notice"><h2>DEDAK etkinlik arşivi</h2><p>Etkinlik fotoğrafları için DEDAK ile iletişime geçebilirsiniz.</p><a class="button" href="iletisim.html">İletişim ↗</a></div>'
    if s in ['about-3','about-3-1','about-3-2','about-3-4','about-3-3','dedak-ölçütler','akreditasyon-süreci']:return resources(p)
    if s=='akreditasyon-ücretleri':return '<div class="notice">2027 başvuruları için ücretlerin Kasım ayı başında güncellenmesi öngörülmektedir. Aşağıdaki mevcut ücret tablosunu başvuru öncesinde DEDAK ile teyit edin.</div>'+figures(p)+clean_content(p)
    if s in ['akredite-edilen-programlar','akreditasyon-sürecinde-olan-kurumlar','organizasyon-semasi']:return figures(p)+clean_content(p)
    return clean_content(p)+figures(p)+resources(p)

def inner(p):
    return '<main id="main" class="wrap inner-page"><h1 class="page-title">'+esc(title(p))+'</h1><article class="prose">'+content_for(p)+'</article></main>'

def build_all():
    write_home()
    for p in pages:
        if p['slug']=='index':continue
        active={'Kurumsal':'hakkinda','Akreditasyon':'akreditasyon','Belgeler':'belgeler'}.get(group_for(p['slug']),p['slug'])
        if p['slug'] in ['uyelik','sunumlar-ve-yayınlar']:active=p['slug']
        desc=BeautifulSoup(p.get('html',''),'html.parser').get_text(' ',strip=True)[:160] or title(p)+' — DEDAK kurumsal web sitesi.'
        (OUT/filename(p['slug'])).write_text(shell(title(p),inner(p),active,desc),encoding='utf-8')
    sitemap_content='<main id="main" class="wrap section"><span class="eyebrow">DEDAK</span><h1>Site haritası</h1>'
    for g,slugs in groups.items():sitemap_content+=f'<h2>{g}</h2>'+cards(slugs)
    sitemap_content+='</main>'
    (OUT/'site-haritasi.html').write_text(shell('Site haritası',sitemap_content,''),encoding='utf-8')
    notfound='<main class="wrap section" id="main"><span class="eyebrow">404</span><h1>Bu sayfa bulunamadı.</h1><p>Aradığınız içeriğe ana sayfadan veya site haritasından ulaşabilirsiniz.</p><a class="button" href="index.html">Ana sayfaya dön →</a></main>'
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
    app=ROOT/'site-source/app'
    if app.exists():
        html=BeautifulSoup((OUT/'index.html').read_text(encoding='utf-8'),'html.parser')
        (app/'home-content.ts').write_text('export const homeContent = '+json.dumps(html.body.decode_contents(),ensure_ascii=False)+';\n',encoding='utf-8')
        (app/'globals.css').write_text((ROOT/'assets/site.css').read_text(encoding='utf-8'),encoding='utf-8')
        shutil.copytree(OUT,ROOT/'site-source/public',dirs_exist_ok=True)
    print(f'Built {len(list(OUT.glob("*.html")))} HTML pages. Assets: {len(assets)}.')

if __name__=='__main__':build_all()
