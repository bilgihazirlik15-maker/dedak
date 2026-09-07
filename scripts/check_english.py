from pathlib import Path
from bs4 import BeautifulSoup
import re
out=Path(__file__).resolve().parent.parent/'godaddy/en'
for p in out.glob('*.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    texts=[]
    for text in s.select_one('main').stripped_strings:
        if re.search('[ğışĞİŞ]',text) and text not in texts:texts.append(text)
    if texts:print(p.name,texts)
