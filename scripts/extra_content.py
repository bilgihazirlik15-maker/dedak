from collect import *
s=BeautifulSoup((DATA/'gallery-source.html').read_text(encoding='utf-8'),'html.parser')
j=json.loads(s.select_one('#wix-viewer-model').text)
router=j['siteFeaturesConfigs']['router']['pagesMap']
names={p['pageUriSEO']:p['pageJsonFileName'] for p in router.values()}
for slug_name in ['galeri','kurucu-kurul']:
    name=names[slug_name]
    for base in ['https://pages.parastorage.com/','https://staticorigin.wixstatic.com/sites/','https://www.dedak.org/']:
        u=base+name+'.json'
        try:
            raw=fetch(u); data=json.loads(raw)
            (DATA/(slug_name+'-raw.json')).write_bytes(raw)
            print('OK',slug_name,u,len(raw),flush=True); break
        except Exception as e:print('FAIL',u,str(e),flush=True)
