(() => {
  'use strict';
  const form = document.querySelector('#checkout');
  const emailInput = document.querySelector('#email');
  const emailError = document.querySelector('#email-error');
  const formMessage = document.querySelector('#form-message');
  const submitButton = document.querySelector('#submit-button');
  document.querySelector('#year').textContent = new Date().getFullYear();

  const setEmailError = (message = '') => {
    emailError.textContent = message;
    emailInput.setAttribute('aria-invalid', String(Boolean(message)));
  };
  const setFormMessage = (message = '') => {
    formMessage.textContent = message;
    formMessage.hidden = !message;
  };
  const setLoading = (loading) => {
    submitButton.disabled = loading;
    submitButton.setAttribute('aria-busy', String(loading));
    submitButton.firstElementChild.textContent = loading ? 'Opening secure checkout…' : 'Continue to payment';
  };
  const validateEmail = () => {
    const value = emailInput.value.trim();
    if (!value) { setEmailError('Enter your email address.'); return false; }
    if (!emailInput.validity.valid) { setEmailError('Enter a valid email address.'); return false; }
    setEmailError();
    return true;
  };

  emailInput.addEventListener('input', () => {
    if (emailInput.getAttribute('aria-invalid') === 'true') validateEmail();
    setFormMessage();
  });
  emailInput.addEventListener('blur', validateEmail);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    setFormMessage();
    if (!validateEmail()) { emailInput.focus(); return; }
    setLoading(true);
    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ email: emailInput.value.trim() })
      });
      const contentType = response.headers.get('content-type') || '';
      const result = contentType.includes('application/json') ? await response.json() : {};
      if (!response.ok) throw new Error(result.message || 'Checkout is temporarily unavailable. Please try again.');
      if (!result.checkoutUrl) throw new Error('Checkout could not be started. Please try again.');
      const checkoutUrl = new URL(result.checkoutUrl, window.location.origin);
      const isSecureDestination = checkoutUrl.protocol === 'https:';
      const isLocalDevelopment = checkoutUrl.protocol === 'http:' && ['localhost', '127.0.0.1'].includes(checkoutUrl.hostname);
      if (!isSecureDestination && !isLocalDevelopment) throw new Error('Checkout returned an invalid destination.');
      window.location.assign(checkoutUrl.href);
    } catch (error) {
      setFormMessage(error instanceof Error ? error.message : 'Checkout is temporarily unavailable. Please try again in a moment.');
      setLoading(false);
    }
  });
})();
