(() => {
  'use strict';
  const form = document.querySelector('#checkout-form');
  const button = document.querySelector('#submit-button');
  const status = document.querySelector('#form-status');
  const name = document.querySelector('#name');
  const email = document.querySelector('#email');
  document.querySelector('#year').textContent = new Date().getFullYear();

  const setError = (input, message) => {
    const error = document.querySelector(`#${input.id}-error`);
    error.textContent = message;
    input.setAttribute('aria-invalid', message ? 'true' : 'false');
  };
  const validate = () => {
    setError(name, name.value.trim() ? '' : 'Enter your name.');
    setError(email, email.validity.valueMissing ? 'Enter your email address.' : email.validity.typeMismatch ? 'Enter a valid email address.' : '');
    const invalid = form.querySelector('[aria-invalid="true"]');
    if (invalid) invalid.focus();
    return !invalid;
  };
  [name, email].forEach((input) => input.addEventListener('input', () => setError(input, '')));

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    status.className = 'form-status'; status.textContent = '';
    if (!validate()) return;
    button.disabled = true; button.textContent = 'Opening secure checkout…';
    try {
      const response = await fetch('/api/checkout', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify({ name: name.value.trim(), email: email.value.trim() }) });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.checkoutUrl) throw new Error('Checkout is temporarily unavailable. Please try again.');
      const destination = new URL(data.checkoutUrl, window.location.origin);
      if (destination.protocol !== 'https:' || destination.origin === window.location.origin) throw new Error('Checkout is temporarily unavailable. Please try again.');
      window.location.assign(destination.href);
    } catch (error) {
      status.className = 'form-status error'; status.textContent = error.message || 'Checkout is temporarily unavailable. Please try again.';
      button.disabled = false; button.textContent = 'Continue to secure payment — $49';
    }
  });
})();
