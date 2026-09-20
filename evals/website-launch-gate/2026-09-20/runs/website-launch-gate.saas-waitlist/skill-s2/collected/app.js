const form = document.querySelector('#waitlist');
const email = document.querySelector('#email');
const status = document.querySelector('#status');
const submit = form.querySelector('button[type="submit"]');
const startedAt = Date.now();
document.querySelector('#year').textContent = new Date().getFullYear();
function setStatus(message, state = '') { status.textContent = message; status.dataset.state = state; }
form.addEventListener('submit', async (event) => {
  event.preventDefault(); setStatus('');
  if (!email.validity.valid) { email.setAttribute('aria-invalid', 'true'); setStatus('Enter a valid work email address.', 'error'); email.focus(); return; }
  email.removeAttribute('aria-invalid'); submit.disabled = true; submit.textContent = 'Joining…';
  try {
    const response = await fetch(form.action, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify({ email: email.value.trim(), website: form.elements.website.value, elapsedMs: Date.now() - startedAt }) });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    form.reset(); setStatus('You’re on the list. We’ll be in touch.', 'success');
  } catch { setStatus('We couldn’t add you right now. Please try again in a moment.', 'error'); }
  finally { submit.disabled = false; submit.textContent = 'Join the waitlist'; }
});
