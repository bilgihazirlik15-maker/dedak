(() => {
  const link=document.querySelector('.certificate-page figure a');
  if(!link)return;
  const english=document.documentElement.lang==='en';
  const dialog=document.createElement('dialog');
  dialog.className='certificate-preview';
  dialog.setAttribute('aria-label',english?'Registration certificate — enlarged view':'Tescil belgesi — büyütülmüş görünüm');
  const bar=document.createElement('div');bar.className='certificate-preview-bar';
  const zoom=document.createElement('button');zoom.type='button';
  zoom.textContent=english?'Zoom in':'Yakınlaştır';zoom.setAttribute('aria-pressed','false');
  const close=document.createElement('button');close.type='button';close.textContent=english?'Close ×':'Kapat ×';
  const viewport=document.createElement('div');viewport.className='certificate-preview-image';
  const image=document.createElement('img');image.src=link.href;
  image.alt=english?'DEDAK registration certificate':'DEDAK tescil belgesi';
  viewport.append(image);bar.append(zoom,close);dialog.append(bar,viewport);document.body.append(dialog);
  let previousOverflow='';
  link.setAttribute('aria-haspopup','dialog');
  link.addEventListener('click',event=>{
    if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
    event.preventDefault();
    previousOverflow=document.body.style.overflow;document.body.style.overflow='hidden';
    dialog.showModal();close.focus();
  });
  zoom.addEventListener('click',()=>{
    const enlarged=viewport.classList.toggle('is-zoomed');
    zoom.setAttribute('aria-pressed',String(enlarged));
    zoom.textContent=enlarged?(english?'Fit to screen':'Ekrana sığdır'):(english?'Zoom in':'Yakınlaştır');
  });
  close.addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
  dialog.addEventListener('close',()=>{
    document.body.style.overflow=previousOverflow;
    viewport.classList.remove('is-zoomed');viewport.scrollTo(0,0);
    zoom.setAttribute('aria-pressed','false');zoom.textContent=english?'Zoom in':'Yakınlaştır';link.focus();
  });
})();
