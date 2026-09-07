from collect import *
raw=fetch('https://www.dedak.org/en')
s=BeautifulSoup(raw,'html.parser')
items=[]
for a in s.select('nav a[href]'):
    href=a['href'];label=a.get_text(' ',strip=True)
    if label and urlsplit(href).netloc=='en.dedak.org' and href not in [u for _,u in items]:items.append((label,href))
with ThreadPoolExecutor(max_workers=6) as pool:pages=list(pool.map(get_page,items))
(DATA/'pages-en.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
