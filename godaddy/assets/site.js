const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
let directNavigationTimer;
function clearPendingNavigation(){navigation?.classList.remove('direct-link-pending');navigation?.querySelectorAll('.is-pending').forEach(link=>link.classList.remove('is-pending'));}
function markPendingNavigation(link){clearPendingNavigation();navigation?.classList.add('direct-link-pending');link.classList.add('is-pending');}
navigation?.querySelectorAll(':scope > a[href]').forEach(link=>{
  link.addEventListener('pointerdown',()=>markPendingNavigation(link));
  link.addEventListener('pointercancel',clearPendingNavigation);
  link.addEventListener('click',event=>{
    if(event.defaultPrevented||event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
    event.preventDefault();
    markPendingNavigation(link);
    clearTimeout(directNavigationTimer);
    directNavigationTimer=setTimeout(()=>window.location.assign(link.href),80);
  });
});
window.addEventListener('pageshow',()=>{clearTimeout(directNavigationTimer);clearPendingNavigation();});
function closeMenu(){navigation?.classList.remove('open');menuButton?.setAttribute('aria-expanded','false');}
function syncSubmenuState(){navigation?.classList.toggle('submenu-open',Boolean(document.querySelector('.submenu-toggle[aria-expanded="true"]')));}
function closeSubmenus(except){document.querySelectorAll('.submenu-toggle').forEach(button=>{if(button===except)return;button.setAttribute('aria-expanded','false');document.getElementById(button.getAttribute('aria-controls')).hidden=true;});syncSubmenuState();}
document.querySelectorAll('.submenu-toggle').forEach(button=>button.addEventListener('click',()=>{const panel=document.getElementById(button.getAttribute('aria-controls'));const open=panel.hidden;closeSubmenus(button);panel.hidden=!open;button.setAttribute('aria-expanded',String(open));syncSubmenuState();}));
document.addEventListener('keydown',event=>{if(event.key==='Escape'){const button=document.querySelector('.submenu-toggle[aria-expanded="true"]');if(button){closeSubmenus();button.focus();}else if(navigation?.classList.contains('open')){closeMenu();menuButton.focus();}}});
document.addEventListener('click',event=>{if(!event.target.closest('.nav-group'))closeSubmenus();});
menuButton?.addEventListener('click',()=>{const open=navigation.classList.toggle('open');menuButton.setAttribute('aria-expanded',String(open));});
document.addEventListener('click',event=>{if(!event.target.closest('.header'))closeMenu();});
window.matchMedia('(min-width:641px)').addEventListener('change',event=>{if(event.matches){closeMenu();closeSubmenus();}});

document.querySelectorAll('[data-carousel]').forEach(carousel=>{
  const slides=[...carousel.querySelectorAll('.announcement-slide')];
  const controls=carousel.querySelector('.carousel-controls');
  if(slides.length<2){controls.hidden=true;return;}
  const dots=carousel.querySelector('.carousel-dots');
  const status=carousel.querySelector('.carousel-status');
  const pauseButton=carousel.querySelector('.carousel-pause');
  const english=document.documentElement.lang==='en';
  const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let current=0;
  let timer;
  let paused=reducedMotion;
  const dotButtons=slides.map((slide,index)=>{
    slide.setAttribute('aria-label',`${index+1} / ${slides.length}`);
    const button=document.createElement('button');
    button.type='button';
    button.className='carousel-dot';
    button.setAttribute('aria-label',english?`Show announcement ${index+1}`:`${index+1}. duyuruyu göster`);
    button.addEventListener('click',()=>show(index,true));
    dots.append(button);
    return button;
  });
  function show(index,announce=false){
    current=(index+slides.length)%slides.length;
    slides.forEach((slide,i)=>{
      const active=i===current;
      slide.classList.toggle('is-active',active);
      slide.setAttribute('aria-hidden',String(!active));
    });
    dotButtons.forEach((button,i)=>button.setAttribute('aria-current',i===current?'true':'false'));
    if(announce)status.textContent=english?`Announcement ${current+1} of ${slides.length}`:`${slides.length} duyurudan ${current+1}. duyuru`;
    restart();
  }
  function restart(){clearInterval(timer);if(!paused)timer=setInterval(()=>show(current+1),6500);}
  function setPaused(value){
    paused=value;
    pauseButton.textContent=paused?(english?'Play':'Oynat'):(english?'Pause':'Duraklat');
    pauseButton.setAttribute('aria-label',paused?(english?'Play slideshow':'Slayt gösterisini oynat'):(english?'Pause slideshow':'Slayt gösterisini duraklat'));
    restart();
  }
  carousel.querySelector('.carousel-prev').addEventListener('click',()=>show(current-1,true));
  carousel.querySelector('.carousel-next').addEventListener('click',()=>show(current+1,true));
  pauseButton.addEventListener('click',()=>setPaused(!paused));
  carousel.addEventListener('mouseenter',()=>clearInterval(timer));
  carousel.addEventListener('mouseleave',restart);
  carousel.addEventListener('focusin',()=>clearInterval(timer));
  carousel.addEventListener('focusout',event=>{if(!carousel.contains(event.relatedTarget))restart();});
  controls.hidden=false;
  show(0);
  setPaused(paused);
});

document.querySelector('#contact-form')?.addEventListener('submit',event=>{
  event.preventDefault();
  const form=event.currentTarget;
  if(!form.reportValidity())return;
  const data=new FormData(form);
  const english=document.documentElement.lang==='en';
  const body=`${english?'Full name':'Ad Soyad'}: ${data.get('name')}\n${english?'Email':'E-posta'}: ${data.get('email')}\n\n${data.get('message')}`;
  window.location.href=`mailto:info@dedak.org?subject=${encodeURIComponent(data.get('subject'))}&body=${encodeURIComponent(body)}`;
  document.querySelector('#form-status').textContent=english?'Review and send the draft in your email application. If no application opened, email info@dedak.org directly.':'E-posta uygulamanızda açılan taslağı kontrol edip gönderin. Uygulama açılmadıysa info@dedak.org adresine doğrudan yazabilirsiniz.';
});
