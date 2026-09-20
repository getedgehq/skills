(() => {
  'use strict';

  const form = document.querySelector('#checkout');
  if (!form) return;

  const email = form.elements.email;
  const card = form.elements.card;
  const button = form.querySelector('button[type="submit"]');
  const buttonLabel = button.querySelector('.button-label');
  const status = document.querySelector('#form-status');
  const success = document.querySelector('#success');
  const confirmationEmail = document.querySelector('#confirmation-email');

  const setFieldError = (field, message = '') => {
    const error = document.querySelector(`#${field.id}-error`);
    field.setAttribute('aria-invalid', message ? 'true' : 'false');
    error.textContent = message;
  };

  const validate = () => {
    let firstInvalid = null;
    const cleanEmail = email.value.trim();
    const cleanCard = card.value.trim();

    if (!cleanEmail) {
      setFieldError(email, 'Enter your email address.');
      firstInvalid = email;
    } else if (!email.validity.valid) {
      setFieldError(email, 'Enter a valid email address.');
      firstInvalid = email;
    } else {
      setFieldError(email);
    }

    if (!cleanCard) {
      setFieldError(card, 'Enter the token from your payment provider.');
      firstInvalid ||= card;
    } else {
      setFieldError(card);
    }

    firstInvalid?.focus();
    return !firstInvalid;
  };

  [email, card].forEach((field) => {
    field.addEventListener('input', () => {
      if (field.getAttribute('aria-invalid') === 'true') setFieldError(field);
      status.textContent = '';
      status.className = 'form-status';
    });
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!validate()) return;

    const endpoint = form.dataset.endpoint;
    button.disabled = true;
    button.setAttribute('aria-busy', 'true');
    buttonLabel.textContent = 'Processing…';
    status.textContent = 'Submitting your registration…';
    status.className = 'form-status';

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ email: email.value.trim(), card: card.value.trim() })
      });

      let result = {};
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        try {
          result = await response.json();
        } catch {
          result = {};
        }
      }

      if (!response.ok) {
        throw new Error(result.message || 'Payment could not be completed. Please check your details and try again.');
      }

      confirmationEmail.textContent = email.value.trim();
      form.hidden = true;
      success.hidden = false;
      success.focus();
    } catch (error) {
      status.textContent = error instanceof TypeError
        ? 'We couldn’t reach the payment service. Check your connection and try again.'
        : error.message;
      status.className = 'form-status error';
      button.disabled = false;
      button.removeAttribute('aria-busy');
      buttonLabel.textContent = 'Pay $49';
    }
  });
})();
