from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import json,zipfile
from xml.etree import ElementTree
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'godaddy'
errors=[]; count=0; external=set(); menu_signatures={}
for path in OUT.rglob('*.html'):
    raw_html=path.read_text(encoding='utf-8')
    if not raw_html.lstrip().lower().startswith('<!doctype html>'):errors.append(f'{path.name}: missing HTML doctype or stray content before document')
    soup=BeautifulSoup(raw_html,'html.parser')
    language='en' if path.parent.name=='en' else 'tr'
    if soup.html.get('lang')!=language:errors.append(f'{path.name}: incorrect language')
    choices=soup.select('.language-switch a[hreflang]')
    if {a.get('hreflang') for a in choices}!={'tr','en'}:errors.append(f'{path}: missing language choices')
    for a in choices:
        expected_label='Türkçe' if a['hreflang']=='tr' else 'English'
        if a.get_text(' ',strip=True)!=expected_label:errors.append(f'{path}: unexpected language switch label')
        expected=OUT/('en' if a['hreflang']=='en' else '')/path.name
        actual=(path.parent/unquote(urlsplit(a['href']).path)).resolve()
        if actual!=expected.resolve():errors.append(f'{path}: wrong language counterpart')
    if len(soup.select('.language-switch [aria-current="true"]'))!=1:errors.append(f'{path}: invalid active language')
    if path.name=='akreditasyon-surecinde-olan-kurumlar.html':
        expected=json.loads((ROOT/'content/in-progress-institutions.json').read_text(encoding='utf-8'))
        actual=[(cells[0].get_text(' ',strip=True),cells[1].get_text(' ',strip=True)) for row in soup.select('.institution-table tbody tr') if len(cells:=row.select('td'))==2]
        if actual!=[(name,f'Şubat / February {year}') for name,year in expected]:errors.append(f'{path}: institution table differs from source data')
    if path.name=='akredite-edilen-programlar.html':
        map_heading=soup.select_one('#university-map-title')
        expected_heading='Accredited Universities Map' if language=='en' else 'Akredite Üniversiteler Haritası'
        if not map_heading or map_heading.get_text(' ',strip=True)!=expected_heading:errors.append(f'{path}: incorrect university map heading')
        expected=json.loads((ROOT/'content/programs.json').read_text(encoding='utf-8'))
        rows=soup.select('.program-table tbody tr')
        actual=[(row.select_one('.program-index').get_text(strip=True),row.select_one('.program-identity strong').get_text(' ',strip=True),*[cell.get_text(' ',strip=True) for cell in row.select('td')]) for row in rows]
        if actual!=[(number,name,evaluation,period) for number,name,_,evaluation,period in expected]:errors.append(f'{path}: accredited program table differs from source data')
        if not soup.select_one('details[hidden] > summary'):errors.append(f'{path}: original program list must remain hidden')
        locations=json.loads((ROOT/'content/university-map.json').read_text(encoding='utf-8'))
        source_names={name for _,name,_,_,_ in expected}
        map_names=[a.get_text(' ',strip=True) for a in soup.select('.map-popup a[href]')]
        if set(map_names)!=source_names or len(map_names)!=len(source_names):errors.append(f'{path}: map universities differ from accredited programs')
        if len(soup.select('[data-map-point]'))!=len(locations) or not soup.select_one('[data-map-open]') or not soup.select_one('dialog[data-university-map]'):errors.append(f'{path}: incomplete interactive map')
        for point in soup.select('[data-map-point]'):
            popup=soup.find(id=point.get('aria-controls'))
            if not popup or len(popup.select('a[href]'))!=1:errors.append(f'{path}: each map point must link to one university')
    if path.name=='akreditasyon.html':
        first=soup.select_one('main article').find(['h2','p'])
        if first and first.get_text(' ',strip=True).casefold().replace('\u0307','') in {'akreditasyon','accreditation'}:errors.append(f'{path}: repeated accreditation heading')
    if path.name=='sunumlar-ve-yayinlar.html':
        if soup.select('main h2,main h3,main h4'):errors.append(f'{path}: repeated presentations heading')
        rows=soup.select('.publication-table tbody tr')
        if len(rows)!=12 or len(soup.select('.publication-title-link'))!=11 or len(soup.select('.publication-unavailable'))!=1:errors.append(f'{path}: incomplete presentations table')
    if path.name=='organizasyon-semasi.html':
        if len(soup.select('.org-chart .org-card'))!=8:errors.append(f'{path}: organization chart must contain all eight units')
        direct=soup.select('.org-leadership > .org-direct > .org-branch')
        if [branch.select_one(':scope > .org-card')['class'][-1] for branch in direct]!=['org-card-dak','org-card-committees','org-card-advisory','org-card-enterprise']:errors.append(f'{path}: DAK, committees, advisory board and enterprise must report directly to the management board')
        if len(soup.select('.org-dak > .org-evaluators > .org-card-evaluators'))!=1:errors.append(f'{path}: evaluation team must report to DAK')
        if soup.select('main figure,main figcaption,main .help'):errors.append(f'{path}: old organization image or caption is still visible')
    if path.name=='kisaca-dedak.html':
        if soup.select('main .resource-list,main .resource,main .help'):errors.append(f'{path}: redundant document download or note is still visible')
    nav=soup.select_one('#navigation')
    if not nav:errors.append(f'{path.name}: missing shared navigation')
    else:
        current_items=nav.select('[aria-current]')
        expected_current=0 if path.name=='404.html' else 1
        if len(current_items)!=expected_current:errors.append(f'{path.name}: expected {expected_current} highlighted menu item, found {len(current_items)}')
        normalized=BeautifulSoup(str(nav),'html.parser')
        for node in normalized.select('[aria-current]'):del node['aria-current']
        signature=str(normalized)
        if language not in menu_signatures:menu_signatures[language]=signature
        elif signature!=menu_signatures[language]:errors.append(f'{path.name}: inconsistent shared navigation')
        for link in nav.select('a[href]'):
            if not urlsplit(link['href']).query.startswith('v='):errors.append(f'{path.name}: unversioned navigation link {link["href"]}')
        membership_links=[link for link in nav.select('a[href]') if urlsplit(link['href']).path=='uyelik.html']
        if len(membership_links)!=1 or membership_links[0].parent!=nav:errors.append(f'{path.name}: membership must appear only as a top-level menu item')
        presentations_links=[link for link in nav.select('a[href]') if urlsplit(link['href']).path=='sunumlar-ve-yayinlar.html']
        if len(presentations_links)!=1 or presentations_links[0].parent!=nav:errors.append(f'{path.name}: presentations must appear only as a top-level menu item')
        for parent_slug in ('hakkinda','akreditasyon','belgeler'):
            panel=nav.select_one(f'#submenu-{parent_slug}')
            if panel and any(urlsplit(link['href']).path==f'{parent_slug}.html' for link in panel.select('a[href]')):errors.append(f'{path.name}: {parent_slug} repeats in its submenu')
        accreditation_panel=nav.select_one('#submenu-akreditasyon')
        if accreditation_panel and urlsplit(accreditation_panel.select_one('a[href]')['href']).path!='akreditasyon-faaliyetleri-raporu.html':errors.append(f'{path.name}: accreditation submenu must start with activity report')
    for group in soup.select('.nav-group'):
        toggle=group.find('button',class_='submenu-toggle',recursive=False)
        panel=group.find(class_='submenu',recursive=False)
        if not toggle or not panel:errors.append(f'{path.name}: invalid dropdown menu structure')
        elif toggle.get('aria-controls')!=panel.get('id'):errors.append(f'{path.name}: dropdown control mismatch')
        if group.find('a',recursive=False):errors.append(f'{path.name}: dropdown heading must not navigate')
        if '⌄' in group.get_text() or group.select_one('.menu-caret'):errors.append(f'{path.name}: dropdown arrow must not be visible')
    stylesheet=soup.select_one('link[rel="stylesheet"]');script=soup.select_one('script[src]')
    if not stylesheet or '?v=' not in stylesheet.get('href',''):errors.append(f'{path.name}: unversioned stylesheet')
    if not script or '?v=' not in script.get('src',''):errors.append(f'{path.name}: unversioned menu script')
    if not soup.title or len(soup.select('h1'))!=1:errors.append(f'{path.name}: invalid title/h1')
    if any(symbol in link.get_text(' ',strip=True) for link in soup.select('a') for symbol in ('↗','→')):errors.append(f'{path.name}: decorative arrow in link text')
    if soup.select('a .arrow'):errors.append(f'{path.name}: decorative arrow element inside link')
    for link in soup.select('a[href]'):
        href=urlsplit(link['href'])
        if link.find_parent(class_='header'):
            if link.has_attr('target'):errors.append(f'{path}: header navigation must remain in the same tab: {link["href"]}')
            continue
        if (not href.path and href.fragment) or href.scheme in {'mailto','tel','javascript','data'}:continue
        if link.get('target')!='_blank' or not {'noopener','noreferrer'}.issubset(set(link.get('rel',[]))) or link.has_attr('download'):errors.append(f'{path}: link must open safely in a new tab: {link["href"]}')
    if path.name=='index.html':
        carousel=soup.select_one('[data-carousel]')
        if not carousel or len(carousel.select('.announcement-slide'))<1:errors.append(f'{path}: missing announcement carousel')
        elif not all(carousel.select_one(selector) for selector in ('.carousel-controls','.carousel-prev','.carousel-next','.carousel-dots')):errors.append(f'{path}: missing carousel navigation')
        preview=soup.select_one('.announcement-preview')
        more=preview.select_one('.announcement-more') if preview else None
        expected_more='More' if language=='en' else 'Daha fazla göster'
        if not preview or len(preview.select('.announcement-excerpt'))!=1:errors.append(f'{path}: invalid announcement preview')
        if not more or more.get_text(' ',strip=True)!=expected_more or urlsplit(more.get('href','')).path!='duyurular.html':errors.append(f'{path}: invalid announcements link')
        if preview.select('.resource,details'):errors.append(f'{path}: full announcement content leaked into homepage preview')
    ids=[e['id'] for e in soup.select('[id]')]
    if len(ids)!=len(set(ids)):errors.append(f'{path.name}: duplicate ids')
    for el in soup.select('a[href],img[src],link[href],script[src]'):
        href=el.get('href') or el.get('src'); u=urlsplit(href)
        if u.scheme or u.netloc:
            external.add(href)
            if 'dedak.org' in u.netloc:errors.append(f'{path.name}: unmigrated internal URL: {href}')
            continue
        count+=1; target=(path.parent/unquote(u.path)) if u.path else path
        if not target.exists():errors.append(f'{path.name}: missing {href}')
        if u.fragment and target.suffix=='.html' and target.exists():
            dest=BeautifulSoup(target.read_text(encoding='utf-8'),'html.parser')
            if not dest.find(id=unquote(u.fragment)):errors.append(f'{path.name}: missing fragment {href}')
        if el.name=='img' and not el.get('alt') and el.get('aria-hidden')!='true':errors.append(f'{path.name}: missing image alt')
    if '\ufffd' in soup.get_text():errors.append(f'{path.name}: text encoding damage')
map_svg=ElementTree.parse(ROOT/'assets/turkey-map.svg').getroot()
cyprus_shape=next((element for element in map_svg.iter() if element.get('id')=='cyprus-island'),None)
if cyprus_shape is None or cyprus_shape.get('d','').count('L')<80:errors.append('Cyprus island outline is incomplete')
for doc in (OUT/'documents').iterdir():
    raw=doc.read_bytes()
    if doc.suffix=='.pdf' and not raw.startswith(b'%PDF'):errors.append('Invalid PDF '+doc.name)
    if doc.suffix in ['.docx','.pptx'] and not zipfile.is_zipfile(doc):errors.append('Invalid Office document '+doc.name)
for path in OUT.glob('*.html'):
    tr=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
    en=BeautifulSoup((OUT/'en'/path.name).read_text(encoding='utf-8'),'html.parser')
    # Navigation must keep exactly the same element slots in both languages.
    def header_shape(soup):
        return [(el.name,tuple(el.get('class',[]))) for el in soup.select('.header-inner *')]
    if header_shape(tr)!=header_shape(en):errors.append(f'{path.name}: different localized header structure')
    for selector in ['.announcement-banner','.notice','.contact-grid','.page-cards','details','form']:
        if len(tr.select(selector))!=len(en.select(selector)):errors.append(f'{path.name}: different layout sections: {selector}')
report={'pages':len(list(OUT.rglob('*.html'))),'local_references_checked':count,'documents':len(list((OUT/'documents').iterdir())),'errors':errors,'external_links':sorted(external),'checks':['Turkish/English language metadata','same-page language switching','one active language','one shared menu per language','exactly one highlighted menu item','dropdown headings and panels','no dropdown arrows','versioned menu assets and navigation links','one primary heading per page','unique IDs','all local links and fragments','local images/scripts/styles','PDF/Office file signatures'],'not_tested':['GoDaddy server configuration','External article availability','Email client handoff']}
(ROOT/'content/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
