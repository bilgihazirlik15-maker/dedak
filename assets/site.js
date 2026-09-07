const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
function closeMenu(){navigation?.classList.remove('open');menuButton?.setAttribute('aria-expanded','false');}
function closeSubmenus(except){document.querySelectorAll('.submenu-toggle').forEach(button=>{if(button===except)return;button.setAttribute('aria-expanded','false');document.getElementById(button.getAttribute('aria-controls')).hidden=true;});}
document.querySelectorAll('.submenu-toggle').forEach(button=>button.addEventListener('click',()=>{const panel=document.getElementById(button.getAttribute('aria-controls'));const open=panel.hidden;closeSubmenus(button);panel.hidden=!open;button.setAttribute('aria-expanded',String(open));}));
document.addEventListener('keydown',event=>{if(event.key==='Escape'){const button=document.querySelector('.submenu-toggle[aria-expanded="true"]');if(button){closeSubmenus();button.focus();}else if(navigation?.classList.contains('open')){closeMenu();menuButton.focus();}}});
document.addEventListener('click',event=>{if(!event.target.closest('.nav-group'))closeSubmenus();});
menuButton?.addEventListener('click',()=>{const open=navigation.classList.toggle('open');menuButton.setAttribute('aria-expanded',String(open));});
document.addEventListener('click',event=>{if(!event.target.closest('.header'))closeMenu();});
window.matchMedia('(min-width:641px)').addEventListener('change',event=>{if(event.matches){closeMenu();closeSubmenus();}});
document.querySelector('#contact-form')?.addEventListener('submit',event=>{
  event.preventDefault();
  const form=event.currentTarget;
  if(!form.reportValidity())return;
  const data=new FormData(form);
  const body=`Ad Soyad: ${data.get('name')}\nE-posta: ${data.get('email')}\n\n${data.get('message')}`;
  window.location.href=`mailto:info@dedak.org?subject=${encodeURIComponent(data.get('subject'))}&body=${encodeURIComponent(body)}`;
  document.querySelector('#form-status').textContent='E-posta uygulamanızda açılan taslağı kontrol edip gönderin. Uygulama açılmadıysa info@dedak.org adresine doğrudan yazabilirsiniz.';
});
