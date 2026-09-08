from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import json,zipfile
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
        expected=OUT/('en' if a['hreflang']=='en' else '')/path.name
        actual=(path.parent/unquote(urlsplit(a['href']).path)).resolve()
        if actual!=expected.resolve():errors.append(f'{path}: wrong language counterpart')
    if len(soup.select('.language-switch [aria-current="true"]'))!=1:errors.append(f'{path}: invalid active language')
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
