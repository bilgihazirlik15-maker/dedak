from collect import *
from urllib.parse import parse_qs

pages=json.loads((DATA/'pages.json').read_text(encoding='utf-8'))
if (DATA/'pages-en.json').exists():pages+=json.loads((DATA/'pages-en.json').read_text(encoding='utf-8'))
targets={}
for p in pages:
    for label,url in p.get('links',[]):
        if '/ugd/' in url or urlsplit(url).path.endswith(('.pdf','.docx','.pptx')):
            ext=Path(urlsplit(url).path).suffix
            targets[url]={'label':label,'file':'documents/'+hashlib.sha1(urlsplit(url).path.encode()).hexdigest()[:16]+ext}
    for img in p.get('images',[]):
        url=img['url']; targets[url]={'label':img['alt'] or p['title'],'file':'assets/'+Path(urlsplit(url).path).name}

def download(item):
    url,meta=item; path=ROOT/meta['file']; path.parent.mkdir(exist_ok=True)
    try:
        if not path.exists(): path.write_bytes(fetch(url))
        meta['bytes']=path.stat().st_size; print('OK',meta['file'],meta['bytes'],flush=True)
    except Exception as e: meta['error']=str(e); print('FAIL',url,str(e),flush=True)
    return url,meta
with ThreadPoolExecutor(max_workers=6) as pool: result=dict(pool.map(download,targets.items()))
(DATA/'assets.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
