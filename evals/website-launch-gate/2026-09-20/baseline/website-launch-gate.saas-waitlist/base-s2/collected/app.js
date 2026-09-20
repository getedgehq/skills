const form = document.querySelector('#waitlist');
const emailInput = document.querySelector('#email');
const status = document.querySelector('#form-status');
const submitButton = form.querySelector('button[type="submit"]');

document.querySelector('#year').textContent = new Date().getFullYear();

function setStatus(message = '', type = '') {
  status.textContent = message;
  status.className = `form-status ${type}`.trim();
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  setStatus();
  if (!emailInput.checkValidity()) {
    emailInput.setAttribute('aria-invalid', 'true');
    setStatus('Enter a valid work email to continue.', 'error');
    emailInput.focus();
    return;
  }
  emailInput.removeAttribute('aria-invalid');
  submitButton.disabled = true;
  submitButton.setAttribute('aria-busy', 'true');
  setStatus('Sending…');
  try {
    const response = await fetch(form.action, {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body: JSON.stringify({email: emailInput.value.trim()})});
    if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
    form.reset();
    setStatus('You’re on the list. We’ll be in touch soon.', 'success');
  } catch (error) {
    console.error('Waitlist submission failed:', error);
    setStatus('We couldn’t submit your request. Please try again in a moment.', 'error');
  } finally {
    submitButton.disabled = false;
    submitButton.removeAttribute('aria-busy');
  }
});
