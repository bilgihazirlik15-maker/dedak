"""Generate parallel static language pages; no browser translation service required."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
from bs4.element import Doctype
import json,re

SOURCE_MAP={'about-3':'about-3-2','tuzuk':'about-3'}
UI={
 'Anasayfa':'Home','Ana Sayfa':'Home','Hakkında':'About','Kurumsal':'About DEDAK','Akreditasyon':'Accreditation','Üyelik':'Membership','Belgeler':'Documents','Sunumlar ve Yayınlar':'Presentations and Publications','Duyurular':'Announcements','Diğer':'More','Galeri':'Gallery','İletişim':'Contact','Site haritası':'Site map','Menü ☰':'Menu ☰','İçeriğe geç':'Skip to content','Ana menü':'Main navigation','DEDAK ana sayfa':'DEDAK home',
 'DEDAK Akreditasyon Başvuruları':'DEDAK Accreditation Applications','DEDAK akreditasyon başvuruları':'DEDAK accreditation applications','2027 akreditasyon dönemi':'2027 accreditation cycle','Başvuru rehberini inceleyin ↗':'Read the application guide ↗','Kurumsal belge':'Institutional document','Akreditasyon için temel belgeler':'Essential accreditation documents',
 'DEDAK’ın kuruluşu, yönetimi, kalite yaklaşımı ve stratejik hedefleri.':'DEDAK’s foundation, governance, approach to quality and strategic objectives.',
 'Akreditasyon çalışmalarında kullanılan belgeler, kurumsal düzenlemeler ve başvuru formları.':'Documents, institutional regulations and application forms used in the accreditation process.',
 'DEDAK kurul, komite ve komisyon üyeleri — 2026.':'DEDAK board and committee members — 2026.',
 'YÖNETİM KURULU':'EXECUTIVE BOARD','DEĞERLENDİRME VE AKREDİTASYON KURULU (DAK)':'EVALUATION AND ACCREDITATION BOARD (DAK)','DEDAK ÖLÇÜT İZLEME VE UYGUNLUK KOMİTESİ':'DEDAK STANDARDS MONITORING AND COMPLIANCE COMMITTEE','TUTARLILIK KOMİTESİ':'CONSISTENCY COMMITTEE','EĞİTİM KOMİSYONU':'TRAINING COMMITTEE','SÜREKLİ İYİLEŞTİRME KOMİTESİ':'CONTINUOUS IMPROVEMENT COMMITTEE','ADAY BELİRLEME KOMİTESİ':'NOMINATION COMMITTEE',
 'DEDAK tarafından akreditasyon verilen İngilizce hazırlık programları ve değerlendirme dönemleri.':'English preparatory programs accredited by DEDAK and their evaluation periods.',
 'Liste geçmiş dönem kayıtlarını da içerir. Her programın akreditasyon geçerlilik tarihini ilgili kayıttan kontrol edin.':'This list also includes historical records. Check the accreditation validity dates in each program’s record.',
 'Son değerlendirme dönemi':'Last evaluation period','Akreditasyon geçerlilik süresi':'Accreditation validity period','Orijinal program listesini görüntüle':'View the original program list',
 'İngilizce Hazırlık Programı':'English Preparatory Program','İngilizce Hazırlık Programı — Lisans':'Undergraduate English Preparatory Program','Zorunlu İngilizce Hazırlık Programı':'Compulsory English Preparatory Program','Temel İngilizce Bölümü':'Basic English Department','Yabancı Diller Yüksekokulu İngilizce Hazırlık Programı':'School of Foreign Languages English Preparatory Program','Yabancı Diller Yüksekokulu Hazırlık Programı':'School of Foreign Languages Preparatory Program',
 'DEDAK etkinlik arşivi':'DEDAK event archive','Etkinlik fotoğrafları için DEDAK ile iletişime geçebilirsiniz.':'Please contact DEDAK for event photographs.','İletişim ↗':'Contact ↗',
 'E-posta':'Email','Adres':'Address','Bize yazın':'Write to us','Ad soyad':'Full name','E-posta adresi':'Email address','Konu':'Subject','Mesajınız':'Your message','E-posta taslağı oluştur ↗':'Create an email draft ↗',
 'Akreditasyon, başvuru ve kurumsal konulardaki sorularınız için:':'For questions about accreditation, applications or institutional matters:',
 'Form, mesajınızı e-posta uygulamanızda taslak olarak açar. Gönderimi açılan uygulamadan tamamlayabilirsiniz.':'This form opens your message as a draft in your email application. You can review and send it from there.',
 'Bu form mesajınızı sunucuya kaydetmez. Çalışması için cihazınızda bir e-posta uygulaması tanımlı olmalıdır.':'This form does not store your message on a server. An email application must be configured on your device.',
 'Bu sayfa bulunamadı.':'Page not found.','Aradığınız içeriğe ana sayfadan veya site haritasından ulaşabilirsiniz.':'You can find the content you need from the home page or site map.','Ana sayfaya dön →':'Return to home →',
 'DEDAK — Dil Eğitimi Değerlendirme ve Akreditasyon Kurulu':'DEDAK — Evaluation and Accreditation of Language Education',
 'İdari ve Mali İşler Yöneticisi: Banu Mete Zor':'Administrative and Financial Affairs Manager: Banu Mete Zor',
 'Akbank İstanbul Sultanbeyli TEM Şubesi':'Akbank Istanbul Sultanbeyli TEM Branch','Şube kodu : 0728':'Branch code: 0728','Hesap numarası: 0150737':'Account number: 0150737',
 '2027 akreditasyon başvuruları':'2027 accreditation applications','Başvuru dönemi:':'Application period:','2 Kasım – 1 Aralık 2026':'2 November – 1 December 2026','Kabul edilen programların açıklanması:':'Announcement of accepted programs:','en geç 4 Ocak 2027':'no later than 4 January 2027',
 'Yükseköğretim kurumları bünyesindeki İngilizce hazırlık programları, imzalı ve eksiksiz başvuru formunu son başvuru tarihine kadar':'English preparatory programs within higher education institutions must send their signed and complete application form by the deadline to','adresine iletmelidir.':'.',
 'Başvuru koşulları':'Application requirements','Aşağıdaki koşulların başvuru sırasında en az bir yıldır karşılanıyor ve uygulanıyor olması beklenmektedir.':'The following conditions are expected to have been met and implemented for at least one year at the time of application.',
 'Programın çıkış seviyesi en az B1+ CEFR düzeyinde olmalıdır. Bu koşul, eğitim dili kısmen İngilizce olan bölümlere yönelik programlar için de geçerlidir.':'The program’s exit level must be at least CEFR B1+. This also applies to programs serving departments where instruction is partly in English.',
 'Öğrenciler dil seviyelerine göre ayrılmalı; seviyeler arası geçiş, kazanımları ölçen bir değerlendirme sistemiyle yapılmalıdır.':'Students must be grouped according to language proficiency, with progression between levels based on an assessment system that measures learning outcomes.',
 'Bir akademik yılda sınavlar hariç en az 28 hafta ders verilmelidir.':'At least 28 weeks of instruction, excluding examinations, must be provided each academic year.',
 'Programın idari ve akademik birimlerini gösteren bir organizasyon şeması bulunmalıdır.':'An organizational chart showing the program’s administrative and academic units must be available.',
 'Program/materyal geliştirme ve ölçme-değerlendirme birimleri veya komisyonları yapılandırılmış olmalıdır.':'Units or committees for program/materials development and testing and assessment must be established.',
 'Programın faaliyet süresi en az üç yıl olmalıdır.':'The program must have been operating for at least three years.',
 'Değerlendirme ve kabul':'Review and acceptance',
 'Başvurular Aralık ayında değerlendirilir. Başvuru sayısı yüksek olduğunda öğrenci sayısı, zorunlu hazırlık oranı ve hazır bulunuşluk gibi formda yer alan bilgilerle önceliklendirme yapılır. İlk 10 program asil, diğer programlar yedek olarak belirlenir.':'Applications are reviewed in December. If there are many applicants, prioritization considers information in the form such as student numbers, the proportion of compulsory preparatory students and readiness. The first ten programs are accepted as primary applicants and the others placed on the reserve list.',
 'Asil programlardan biri çekilirse yedek programlar sıralamaya göre sürece dahil edilir. Aksi halde bir sonraki yılın başvurularında öncelik verilir.':'If a primary program withdraws, reserve programs join the process in order. Otherwise, reserve programs receive priority in the following year’s applications.',
 'Ücretler ve hazırlık belgeleri':'Fees and preparation documents','2027 dönemi ücretlerinin Kasım ayı başında enflasyon oranında güncellenmesi öngörülmektedir.':'Fees for the 2027 cycle are expected to be updated in early November in line with inflation.','Ücret bilgilerini':'Fee information','ve':'and','süreç kılavuzlarını':'process guides','inceleyin.':'are available for review.',
 'Çevrimiçi bilgilendirme toplantısı':'Online information meeting','17 Kasım 2026 Salı, saat 19.00. Zoom toplantı kimliği:':'Tuesday, 17 November 2026, at 19:00. Zoom meeting ID:','Katılım öncesinde toplantı bilgisini DEDAK ile teyit edebilirsiniz.':'You can confirm the meeting details with DEDAK before attending.','Başvuru duyurusunun tam metni':'Full application announcement',
 '2027 başvuruları 2 Kasım – 1 Aralık 2026 tarihleri arasında kabul edilecektir.':'Applications for the 2027 cycle will be accepted from 2 November to 1 December 2026.',
 '2027 başvuruları için ücretlerin Kasım ayı başında güncellenmesi öngörülmektedir. Aşağıdaki mevcut ücret tablosunu başvuru öncesinde DEDAK ile teyit edin.':'Fees for 2027 applications are expected to be updated in early November. Confirm the current fee table below with DEDAK before applying.',
 'DEDAK’ın 2025–2030 Stratejik Planı, Türkiye ve Kuzey Kıbrıs’taki yükseköğretim kurumlarında yabancı dil eğitiminin kalitesini artırmak amacıyla yapılandırılmış, katılımcı bir planlama süreci sonucunda oluşturulmuştur.':'DEDAK’s 2025–2030 Strategic Plan was developed through a structured, participatory planning process to improve the quality of foreign language education in higher education institutions in Türkiye and Northern Cyprus.',
 'Stratejik plan, DEDAK’ın misyonu, vizyonu ve temel değerleri doğrultusunda üç öncelikli alana odaklanmaktadır:':'In line with DEDAK’s mission, vision and core values, the strategic plan focuses on three priority areas:',
 'Kalite Gelişimini Yaygınlaştırmak:':'Promoting Quality Improvement:',
 'DEDAK, yükseköğretimde İngilizce hazırlık programlarına yönelik yüz yüze ve çevrim içi eğitimler, danışmanlıklar ve destek hizmetleri sunarak alanda kalite kültürünü teşvik etmeyi sürdürmektedir.':'DEDAK continues to promote a culture of quality by providing face-to-face and online training, consultancy and support services for English preparatory programs in higher education.',
 'Model Bir Akreditasyon Kuruluşu Olmak:':'Becoming a Model Accreditation Agency:',
 "DEDAK, şeffaf ve uluslararası standartlarla uyumlu ölçütleri, alanında deneyimli değerlendirici havuzu ve sistematik izleme süreçleriyle Türkiye'de örnek bir akreditasyon yapısı oluşturmayı amaçlamaktadır.":'DEDAK aims to establish a model accreditation framework in Türkiye through transparent criteria aligned with international standards, a pool of experienced evaluators and systematic monitoring processes.',
 'Kurumsal ve Mali Sürdürülebilirliği Sağlamak:':'Ensuring Institutional and Financial Sustainability:',
 'Ücretli eğitimler, proje destekleri ve düzenli gelir kaynakları ile mali sürdürülebilirlik sağlanmakta; profesyonel ve gönüllü kadroların gelişimi desteklenmektedir.':'Financial sustainability is supported through fee-based training, project funding and regular income sources, while the development of professional and volunteer staff is encouraged.',
 'Plan, çevresel analizler, paydaş anketleri ve uzman katkılarıyla şekillenmiş olup; somut eylem adımları, başarı ölçütleri ve performans göstergeleri içermektedir. DEDAK’ın stratejik planı, 1 Temmuz 2025 itibarıyla uygulamaya alınacaktır.':'The plan was shaped by environmental analyses, stakeholder surveys and expert input, and includes specific actions, success criteria and performance indicators. The plan’s stated implementation date is 1 July 2025.',
}

def translate_tree(soup,mapping):
    def convert(text):
        stripped=text.strip()
        if stripped in mapping:return text.replace(stripped,mapping[stripped])
        return text.replace('(Başkan Yardımcısı)','(Vice Chair)').replace('(Başkan)','(Chair)').replace(' — büyütmek için görsele tıklayın.',' — click the image to enlarge.').replace(' · İndir',' · Download')
    for node in list(soup.find_all(string=True)):
        if isinstance(node,Doctype):continue
        if node.parent.name not in ['script','style']:node.replace_with(convert(str(node)))
    for node in soup.find_all(True):
        for attr in ['aria-label','alt','title','placeholder']:
            if attr in node.attrs:
                val=node[attr]
                if val.endswith(' alt menüsü'):val=mapping.get(val[:-11],val[:-11])+' submenu'
                node[attr]=convert(val)

def controls(soup,name,lang,version):
    en=lang=='en'; prefix='../' if en else ''
    links=[('tr','Türkçe',prefix+name,'tr'),('en','English',name if en else 'en/'+name,'gb')]
    html='<div class="wrap language-bar"><nav class="language-switch" aria-label="'+('Language' if en else 'Dil seçimi')+'">'
    for code,label,href,flag in links:
        current=' aria-current="true" class="selected"' if code==lang else ''
        html+=f'<a href="{href}?v={version}" lang="{code}" hreflang="{code}" aria-label="{label}"{current}><img src="{prefix}assets/flag-{flag}.svg" alt="" width="24" height="16" aria-hidden="true"><span>{"TR" if code=="tr" else "EN"}</span><span class="language-name">{label}</span></a>'
    html+='</nav></div>'
    soup.select_one('.header').insert(0,BeautifulSoup(html,'html.parser'))
    for code,_,href,_ in links:
        tag=soup.new_tag('link',rel='alternate',hreflang=code,href=href);soup.head.append(tag)

def add_languages(out,b):
    root=out.parent
    english=json.loads((root/'content/pages-en.json').read_text(encoding='utf-8'))
    assert not any('error' in p for p in english), 'English content retrieval failed'
    localized={SOURCE_MAP.get(p['slug'],p['slug']):p for p in english}
    titles={s:p['title'] for s,p in localized.items()}
    titles.update({'dedak-paydaş-tablosu':'DEDAK Stakeholders','akreditasyon-sürecinde-olan-kurumlar':'Programs Undergoing Accreditation','about-3':'Charter of DEDAK','about-3-2':'Directives'})
    mapping=dict(UI)
    for p in b['pages']:mapping[b['title'](p)]=titles[p['slug']]
    for p in b['pages']:mapping[p['title']]=titles[p['slug']]
    mapping.update(UI)
    en_dir=out/'en';en_dir.mkdir(exist_ok=True)
    filename=b['filename'];assets=b['assets']

    def clean(p):
        html=b['clean_content'](p)
        soup=BeautifulSoup(html,'html.parser')
        for a in soup.select('a[href]'):
            href=a['href'];u=urlsplit(href)
            if href in assets:a['href']=assets[href]['file']
            elif u.netloc=='en.dedak.org':
                slug=unquote(u.path).strip('/').rstrip('.') or 'index'
                slug=SOURCE_MAP.get(slug,slug)
                if slug=='akreditasyon-ucretleri':slug='akreditasyon-ücretleri'
                if slug in b['by_slug']:a['href']=filename(slug)
        return str(soup)

    def docs(p):
        soup=BeautifulSoup(b['resources'](p),'html.parser')
        translate_tree(soup,{'İndir':'Download'})
        return str(soup)

    def english_article(slug,current):
        p=localized[slug]
        if slug in ['iletisim','kurucu-kurul','akredite-edilen-programlar','galeri']:return current
        if slug=='akreditasyon-başvurusu':
            template=BeautifulSoup(current,'html.parser')
            template.select_one('details > div').replace_with(BeautifulSoup('<div>'+clean(p)+'</div>','html.parser'))
            template.select_one('.resource-list').replace_with(BeautifulSoup(docs(p),'html.parser'))
            return str(template)
        if slug=='duyurular':return '<span class="eyebrow">2027 accreditation cycle</span><h2>DEDAK accreditation applications</h2><p>Applications for the 2027 cycle will be accepted from 2 November to 1 December 2026.</p><p><a class="button" href="akreditasyon-basvurusu.html">Read the application guide ↗</a></p>'+clean(p)+docs(p)
        if slug=='akreditasyon-ücretleri':return '<div class="notice">Fees for 2027 applications are expected to be updated in early November. Confirm the current fee table below with DEDAK before applying.</div>'+b['figures'](p)+clean(p)
        if slug in ['organizasyon-semasi','akreditasyon-sürecinde-olan-kurumlar']:return b['figures'](p)+clean(p)
        if slug=='hakkinda':return '<p>DEDAK’s foundation, governance, approach to quality and strategic objectives.</p>'+b['cards'](b['groups']['Kurumsal'])+'<h2>Institutional document</h2>'+docs(p)
        if slug=='belgeler':return '<p>Institutional regulations, application forms and accreditation guides.</p>'+b['cards'](b['groups']['Belgeler'])+'<h2>Essential accreditation documents</h2>'+docs(localized['akreditasyon-süreci'])
        if slug=='akreditasyon':return clean(p)+b['cards'](b['groups']['Akreditasyon'])
        if slug in ['about-3','about-3-1','about-3-2','about-3-4','about-3-3','dedak-ölçütler','akreditasyon-süreci']:return docs(p)
        if slug=='index':return clean(localized['duyurular'])+docs(localized['akreditasyon-başvurusu'])
        return clean(p)+b['figures'](p)+docs(p)

    for path in sorted(out.glob('*.html')):
        name=path.name;slug=next((p['slug'] for p in b['pages'] if filename(p['slug'])==name),None)
        tr=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
        en=BeautifulSoup(str(tr),'html.parser')
        en.html['lang']='en'
        if slug:
            en.title.string=titles[slug]+' | DEDAK'
            h1=en.select_one('h1')
            if slug!='index':h1.string=titles[slug]
            article=en.select_one('article.prose')
            current=article.decode_contents()
            article.clear();article.append(BeautifulSoup(english_article(slug,current),'html.parser'))
            if article.select('figure,.resource'):
                for document,note_text in [(en,'Downloads and source images are provided in their original language.'),(tr,'İndirilebilir belgeler ve kaynak görseller özgün dillerinde sunulmaktadır.')]:
                    note=document.new_tag('p',attrs={'class':'help'});note.string=note_text;document.select_one('article.prose').append(note)
        else:
            en.title.string=('Site map' if name=='site-haritasi.html' else 'Page not found')+' | DEDAK'
        translate_tree(en,mapping)
        en.select_one('meta[name="description"]')['content']='DEDAK: language education accreditation, application information, standards and institutional documents.'
        for el in en.select('[href],[src]'):
            attr='href' if el.has_attr('href') else 'src';v=el[attr]
            if v.startswith(('assets/','documents/')):el[attr]='../'+v
        for caption in en.select('figcaption'):
            caption.string='Source image — click to enlarge.'
        controls(tr,name,'tr',b['ASSET_VERSION']);controls(en,name,'en',b['ASSET_VERSION'])
        path.write_text(str(tr),encoding='utf-8')
        (en_dir/name).write_text(str(en),encoding='utf-8')
    xml=out/'sitemap.xml'
    original=xml.read_text(encoding='utf-8')
    extra=''.join('<url><loc>https://www.dedak.org/en/'+filename(p['slug'])+'</loc></url>' for p in b['pages'])
    xml.write_text(original.replace('</urlset>',extra+'</urlset>'),encoding='utf-8')
