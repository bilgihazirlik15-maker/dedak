from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlsplit, unquote, quote
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import json, re, hashlib

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'content'; DATA.mkdir(exist_ok=True)
ASSETS=ROOT/'assets'; ASSETS.mkdir(exist_ok=True)
BASE='https://www.dedak.org/'
def fetch(url):
    url=quote(url,safe=':/?=&%+#@')
    return urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45).read()
def slug(url):
    return unquote(urlsplit(url).path).strip('/') or 'index'
def get_page(item):
    title,url=item
    try:
        raw=fetch(url); s=BeautifulSoup(raw,'html.parser'); m=s.select_one('main') or s
        blocks=[]
        for el in m.select('[data-testid="richTextElement"], .wixui-collapsible-text__text, table'):
            if el.find_parent(attrs={'data-testid':'richTextElement'}): continue
            if not el.get_text(strip=True): continue
            if 'wixui-collapsible-text__text' in el.get('class',[]):
                blocks.extend('<p>'+p.strip()+'</p>' for p in el.get_text('\n').split('\n') if p.strip())
                continue
            for e in el.find_all(True):
                attrs={k:v for k,v in e.attrs.items() if k in ['href','colspan','rowspan']}
                e.attrs=attrs
                if e.name=='a' and e.get('href'): e['href']=urljoin(url,e['href'])
            el.attrs={}
            blocks.append(str(el))
        links=[]
        for a in m.select('a[href]'):
            href=urljoin(url,a['href']); label=a.get_text(' ',strip=True)
            if href.startswith(('http','mailto:')) and label and (label,href) not in links: links.append((label,href))
        imgs=[]
        for img in m.select('img[src]'):
            src=img.get('src'); alt=img.get('alt','')
            if 'static.wixstatic.com/media/' in src:
                src=src.split('/v1/')[0]
                if src not in [i['url'] for i in imgs]: imgs.append({'url':src,'alt':alt})
        result={'title':title,'url':url,'slug':slug(url),'html':'\n'.join(blocks),'text':m.get_text(' ',strip=True),'links':links,'images':imgs}
        (DATA/(hashlib.sha1(url.encode()).hexdigest()[:12]+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(title, len(result['text']),len(links),len(imgs),flush=True)
        return result
    except Exception as e:
        print('ERROR',url,str(e),flush=True); return {'title':title,'url':url,'error':str(e)}

if __name__=='__main__':
    raw=fetch(BASE); s=BeautifulSoup(raw,'html.parser')
    nav=[]
    for a in s.select('nav a[href]'):
        url=a['href']; name=a.get_text(' ',strip=True)
        if name and url.startswith('https://www.dedak.org') and url not in [x[1] for x in nav]: nav.append((name,url))
    (DATA/'navigation.json').write_text(json.dumps(nav,ensure_ascii=False,indent=2),encoding='utf-8')
    with ThreadPoolExecutor(max_workers=6) as pool: pages=list(pool.map(get_page,nav))
    extras={}
    known={slug(u) for _,u in nav}
    for p in pages:
        for label,url in p.get('links',[]):
            if urlsplit(url).netloc=='www.dedak.org' and slug(url) not in known and '.' not in slug(url) and len(slug(url))<100: extras[url]=label
    if extras:
        with ThreadPoolExecutor(max_workers=6) as pool: pages+=list(pool.map(get_page,[(label,url) for url,label in extras.items()]))
    logo=s.select_one('img')['src'].split('/v1/')[0]
    (ASSETS/'dedak-logo.jpg').write_bytes(fetch(logo))
    (DATA/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
