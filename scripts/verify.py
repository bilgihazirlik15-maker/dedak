from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import json,zipfile
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'godaddy'
errors=[]; count=0; external=set()
for path in OUT.glob('*.html'):
    soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
    if soup.html.get('lang')!='tr':errors.append(f'{path.name}: missing Turkish lang')
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
        if el.name=='img' and not el.get('alt'):errors.append(f'{path.name}: missing image alt')
    if '\ufffd' in soup.get_text():errors.append(f'{path.name}: text encoding damage')
for doc in (OUT/'documents').iterdir():
    raw=doc.read_bytes()
    if doc.suffix=='.pdf' and not raw.startswith(b'%PDF'):errors.append('Invalid PDF '+doc.name)
    if doc.suffix in ['.docx','.pptx'] and not zipfile.is_zipfile(doc):errors.append('Invalid Office document '+doc.name)
report={'pages':len(list(OUT.glob('*.html'))),'local_references_checked':count,'documents':len(list((OUT/'documents').iterdir())),'errors':errors,'external_links':sorted(external),'checks':['Turkish encoding','one primary heading per page','unique IDs','all local links and fragments','local images/scripts/styles','PDF/Office file signatures'],'not_tested':['Browser visual/interaction QA','GoDaddy server configuration','External article availability','Email client handoff']}
(ROOT/'content/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
