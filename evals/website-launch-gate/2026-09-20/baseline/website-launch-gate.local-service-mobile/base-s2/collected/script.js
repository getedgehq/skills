const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.site-nav');
menuButton.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  menuButton.querySelector('.sr-only').textContent = isOpen ? 'Open menu' : 'Close menu';
  navigation.classList.toggle('is-open', !isOpen);
});
navigation.addEventListener('click', () => {
  menuButton.setAttribute('aria-expanded', 'false');
  menuButton.querySelector('.sr-only').textContent = 'Open menu';
  navigation.classList.remove('is-open');
});
document.querySelector('#year').textContent = new Date().getFullYear();
document.querySelector('#service-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const subject = encodeURIComponent(`${data.get('service')} request from ${data.get('name')}`);
  const body = encodeURIComponent(`Name: ${data.get('name')}\nEmail: ${data.get('email')}\nService: ${data.get('service')}\n\nDetails:\n${data.get('details')}`);
  document.querySelector('#form-status').textContent = 'Your email app should open now. Send the prepared message to complete your request.';
  window.location.href = `mailto:service@northstarhvac.com?subject=${subject}&body=${body}`;
});
