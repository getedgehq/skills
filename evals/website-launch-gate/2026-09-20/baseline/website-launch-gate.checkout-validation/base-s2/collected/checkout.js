(() => {
  'use strict';

  const form = document.querySelector('#checkout');
  const email = document.querySelector('#email');
  const emailError = document.querySelector('#email-error');
  const status = document.querySelector('#status');
  const button = form.querySelector('button[type="submit"]');

  const setEmailError = (message = '') => {
    emailError.textContent = message;
    email.setAttribute('aria-invalid', message ? 'true' : 'false');
  };

  const validateEmail = () => {
    const value = email.value.trim();
    if (!value) { setEmailError('Enter your email address.'); return false; }
    if (!email.validity.valid) { setEmailError('Enter a valid email address.'); return false; }
    setEmailError();
    return true;
  };

  email.addEventListener('input', () => {
    if (email.getAttribute('aria-invalid') === 'true') validateEmail();
    status.textContent = '';
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    status.textContent = '';
    if (!validateEmail()) { email.focus(); return; }

    button.disabled = true;
    button.textContent = 'Opening secure checkout…';

    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.value.trim() })
      });
      if (!response.ok) throw new Error('Checkout service unavailable');

      const data = await response.json();
      if (!data.url || typeof data.url !== 'string') throw new Error('Missing checkout URL');
      const checkoutUrl = new URL(data.url, window.location.origin);
      if (checkoutUrl.protocol !== 'https:' && checkoutUrl.hostname !== 'localhost') throw new Error('Invalid checkout URL');
      window.location.assign(checkoutUrl.href);
    } catch (error) {
      console.error('Checkout failed:', error);
      status.textContent = 'Checkout is temporarily unavailable. Please try again shortly.';
      button.disabled = false;
      button.textContent = 'Continue to secure payment';
    }
  });
})();
