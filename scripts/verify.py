from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import json,zipfile
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'godaddy'
errors=[]; count=0; external=set()
for path in OUT.rglob('*.html'):
    soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
    language='en' if path.parent.name=='en' else 'tr'
    if soup.html.get('lang')!=language:errors.append(f'{path.name}: incorrect language')
    choices=soup.select('.language-switch a[hreflang]')
    if {a.get('hreflang') for a in choices}!={'tr','en'}:errors.append(f'{path}: missing language choices')
    for a in choices:
        expected=OUT/('en' if a['hreflang']=='en' else '')/path.name
        actual=(path.parent/a['href']).resolve()
        if actual!=expected.resolve():errors.append(f'{path}: wrong language counterpart')
    if len(soup.select('.language-switch [aria-current="true"]'))!=1:errors.append(f'{path}: invalid active language')
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
report={'pages':len(list(OUT.rglob('*.html'))),'local_references_checked':count,'documents':len(list((OUT/'documents').iterdir())),'errors':errors,'external_links':sorted(external),'checks':['Turkish/English language metadata','same-page language switching','one active language','one primary heading per page','unique IDs','all local links and fragments','local images/scripts/styles','PDF/Office file signatures'],'not_tested':['Browser visual/interaction QA','GoDaddy server configuration','External article availability','Email client handoff']}
(ROOT/'content/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
