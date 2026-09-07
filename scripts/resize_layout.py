from pathlib import Path

root=Path(__file__).resolve().parent.parent
path=root/'assets/site.css'
css=path.read_text(encoding='utf-8')
changes={
 'width:min(980px,calc(100% - 40px))':'width:min(1176px,calc(100% - 48px))',
 'width:calc(100% - 32px)':'width:calc(100% - 38.4px)',
 'gap:24px;min-height:96px':'gap:24px;min-height:96px;flex-wrap:wrap',
 'justify-content:flex-start;flex:1;background':'justify-content:flex-start;flex:1 1 850px;flex-wrap:wrap;min-width:0;background',
 "font-size:.8rem;font-weight:700;line-height:1.2":"font-size:.96rem;font-weight:700;line-height:1.2",
 'padding:8px 11px':'padding:9.6px 13.2px',
 'padding:5px 5px 5px 0;font-size:.85rem':'padding:6px 6px 6px 0;font-size:1.02rem',
 'font-weight:700;font-size:.8rem':'font-weight:700;font-size:.96rem',
 'width:280px;background':'width:336px;background',
 'right:0;width:200px':'right:0;width:240px',
 'padding:10px 14px;text-decoration:none;font-size:.86rem':'padding:12px 16.8px;text-decoration:none;font-size:1.032rem',
 '.nav{font-size:.76rem}':'.nav{font-size:.912rem}',
 '.nav>a,.nav-group>a{padding:8px}':'.nav>a,.nav-group>a{padding:9.6px}',
 '.more-toggle{font-size:.76rem;padding:8px}':'.more-toggle{font-size:.912rem;padding:9.6px}',
 'justify-content:center;font-size:.88rem':'justify-content:center;font-size:1.056rem',
 '.nav>a,.nav-group>a{padding:10px}':'.nav>a,.nav-group>a{padding:12px}',
 '.more-toggle{font-size:.88rem;padding:10px}':'.more-toggle{font-size:1.056rem;padding:12px}',
 'padding:13px 16px;min-height:44px':'padding:15.6px 19.2px;min-height:52.8px',
 'padding:10px 16px;min-width:44px;min-height:44px':'padding:12px 19.2px;min-width:52.8px;min-height:52.8px',
 'text-align:left;width:100%;font-size:.88rem':'text-align:left;width:100%;font-size:1.056rem',
 '.submenu a{padding:11px 20px}':'.submenu a{padding:13.2px 24px}',
}
for before,after in changes.items():
    if before not in css:raise ValueError('Missing original CSS: '+before)
    css=css.replace(before,after)
path.write_text(css,encoding='utf-8')
print('Expanded content width and outer gutters; scaled navigation typography and padding by 1.2.')
