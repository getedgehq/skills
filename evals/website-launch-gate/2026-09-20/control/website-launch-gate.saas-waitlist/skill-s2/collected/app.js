(() => {
  'use strict';
  const form = document.querySelector('#waitlist');
  const emailInput = document.querySelector('#email');
  const status = document.querySelector('#form-status');
  const submitButton = form?.querySelector('button[type="submit"]');
  const year = document.querySelector('#year');
  if (year) year.textContent = new Date().getFullYear();
  if (!form || !emailInput || !status || !submitButton) return;

  const setStatus = (message, state = '') => {
    status.textContent = message;
    status.dataset.state = state;
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    setStatus('');
    const email = emailInput.value.trim();
    emailInput.value = email;
    if (!emailInput.checkValidity()) {
      emailInput.setAttribute('aria-invalid', 'true');
      setStatus('Enter a valid work email to join.', 'error');
      emailInput.focus();
      return;
    }

    emailInput.removeAttribute('aria-invalid');
    submitButton.disabled = true;
    submitButton.setAttribute('aria-busy', 'true');
    setStatus('Adding you to the list…', 'loading');
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ email })
      });
      if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
      form.reset();
      setStatus("You're on the list. We'll be in touch.", 'success');
    } catch (error) {
      console.error('Waitlist submission failed:', error);
      setStatus("We couldn't add you right now. Please try again in a moment.", 'error');
    } finally {
      submitButton.disabled = false;
      submitButton.removeAttribute('aria-busy');
    }
  });
})();
