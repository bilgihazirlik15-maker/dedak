"""Apply the user's original-design preference to the static generator."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
path=ROOT/'scripts/build.py'
source=path.read_text(encoding='utf-8')
replacements={
'header':'''def header(active):
    menu=[('index','Anasayfa',None),('hakkinda','Hakkında','Kurumsal'),('akreditasyon','Akreditasyon','Akreditasyon'),('uyelik','Üyelik',None),('belgeler','Belgeler','Belgeler'),('sunumlar-ve-yayınlar','Sunumlar ve Yayınlar',None),('duyurular','Duyurular',None)]
    entries=[]
    for slug,label,group in menu:
        selected=active==slug
        link=f'<a href="{url(slug)}"'+(' aria-current="page"' if selected else '')+f'>{label}</a>'
        children=[s for s in groups.get(group,[]) if s in by_slug and s!=slug]
        if children:
            drop=''.join(f'<a href="{url(s)}">{esc(title(by_slug[s]))}</a>' for s in children)
            entries.append(f'<div class="nav-group">{link}<button class="submenu-toggle" aria-label="{label} alt menüsü" aria-expanded="false" aria-controls="submenu-{slug}">⌄</button><div class="submenu" id="submenu-{slug}" hidden>{drop}</div></div>')
        else:entries.append(link)
    entries.append('<div class="nav-group"><button class="more-toggle submenu-toggle" aria-expanded="false" aria-controls="submenu-more">Diğer ⌄</button><div class="submenu" id="submenu-more" hidden><a href="galeri.html">Galeri</a><a href="iletisim.html">İletişim</a><a href="site-haritasi.html">Site haritası</a></div></div>')
    return '<a class="skip" href="#main">İçeriğe geç</a><header class="header"><div class="wrap header-inner"><a class="brand" href="index.html" aria-label="DEDAK ana sayfa"><img src="assets/dedak-logo.jpg" alt="DEDAK — Dil Eğitimi Değerlendirme ve Akreditasyon Kurulu" width="214" height="83"></a><button class="menu-toggle" aria-controls="navigation" aria-expanded="false">Menü ☰</button><nav class="nav" id="navigation" aria-label="Ana menü">'+''.join(entries)+'</nav></div></header>'
''',
'footer':'''def footer():
    return '<footer class="footer"><div class="wrap"><p class="footer-email"><a href="mailto:info@dedak.org">e-mail: info@dedak.org</a></p><div class="footer-bottom"><span>© 2026 DEDAK</span><a href="site-haritasi.html">Site haritası</a></div></div></footer>'
''',
'homepage':'''def homepage():
    text=clean_content(by_slug['duyurular'])
    return '<main id="main" class="wrap home"><section class="announcement-banner" aria-labelledby="announcement-title"><h1 id="announcement-title"><a href="duyurular.html">DEDAK Akreditasyon Başvuruları</a></h1></section><article class="prose home-announcement">'+text+resources(by_slug['akreditasyon-başvurusu'])+'</article></main>'
''',
'inner':'''def inner(p):
    return '<main id="main" class="wrap inner-page"><h1 class="page-title">'+esc(title(p))+'</h1><article class="prose">'+content_for(p)+'</article></main>'
'''
}
tree=ast.parse(source); lines=source.splitlines(keepends=True)
for node in sorted([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in replacements],key=lambda n:n.lineno,reverse=True):
    lines[node.lineno-1:node.end_lineno]=[replacements[node.name]]
path.write_text(''.join(lines),encoding='utf-8')
