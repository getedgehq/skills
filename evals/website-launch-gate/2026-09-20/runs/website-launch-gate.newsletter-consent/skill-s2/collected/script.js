const form = document.querySelector('#subscribe-form');
const email = document.querySelector('#email');
const status = document.querySelector('#form-status');
const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();
if (form) {
  form.addEventListener('submit', (event) => {
    status.classList.remove('error');
    email.removeAttribute('aria-invalid');
    if (!email.validity.valid) {
      event.preventDefault();
      email.setAttribute('aria-invalid', 'true');
      status.classList.add('error');
      status.textContent = email.validity.valueMissing ? 'Enter your email address.' : 'Enter an email address in the format you@company.com.';
      email.focus();
      return;
    }
    if (form.hasAttribute('data-unconfigured') || !form.action) {
      event.preventDefault();
      status.classList.add('error');
      status.textContent = 'Subscriptions are not available yet. Please check back soon.';
      return;
    }
    form.querySelector('button').disabled = true;
    status.textContent = 'Submitting…';
  });
}
