(() => {
  'use strict';
  const form = document.querySelector('#checkout');
  const emailInput = document.querySelector('#email');
  const emailError = document.querySelector('#email-error');
  const status = document.querySelector('#form-status');
  const submitButton = document.querySelector('#submit-button');
  const buttonLabel = submitButton.querySelector('.button-label');
  const endpoint = document.querySelector('meta[name="checkout-endpoint"]')?.content.trim();

  const setBusy = (busy) => {
    submitButton.disabled = busy;
    form.setAttribute('aria-busy', String(busy));
    buttonLabel.textContent = busy ? 'Opening secure checkout…' : 'Continue to payment';
  };
  const showEmailError = (message) => {
    emailError.textContent = message;
    emailInput.setAttribute('aria-invalid', String(Boolean(message)));
  };
  const validateEmail = () => {
    const email = emailInput.value.trim();
    if (!email) { showEmailError('Enter your email address.'); return false; }
    if (!emailInput.validity.valid) { showEmailError('Enter a valid email address.'); return false; }
    showEmailError(''); return true;
  };

  emailInput.addEventListener('input', () => {
    if (emailError.textContent) validateEmail();
    status.textContent = '';
  });
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    status.textContent = '';
    if (!validateEmail()) { emailInput.focus(); return; }
    if (!endpoint) {
      status.textContent = 'Checkout is temporarily unavailable. Please try again later.';
      return;
    }
    setBusy(true);
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ email: emailInput.value.trim() })
      });
      if (!response.ok) throw new Error(`Checkout request failed: ${response.status}`);
      const payload = await response.json();
      const checkoutUrl = new URL(payload.checkoutUrl, window.location.origin);
      if (checkoutUrl.protocol !== 'https:' || checkoutUrl.username || checkoutUrl.password) {
        throw new Error('Checkout returned an unsafe redirect URL');
      }
      window.location.assign(checkoutUrl.href);
    } catch (error) {
      console.error('Unable to start checkout', error);
      status.textContent = 'We couldn’t open checkout. Please try again.';
      setBusy(false);
    }
  });
})();
