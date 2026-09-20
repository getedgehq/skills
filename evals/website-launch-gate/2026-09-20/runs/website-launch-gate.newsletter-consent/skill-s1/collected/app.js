const form = document.querySelector('#signup-form');
const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();
if (form) {
  const email = form.querySelector('#email');
  const button = form.querySelector('button');
  const status = form.querySelector('#form-status');
  const endpoint = document.querySelector('meta[name="signup-endpoint"]')?.content.trim();
  const setStatus = (message, kind = '') => { status.textContent = message; status.className = `status ${kind}`.trim(); };
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    email.setAttribute('aria-invalid', String(!email.validity.valid));
    if (email.validity.valueMissing) { setStatus('Enter your email address to subscribe.', 'error'); email.focus(); return; }
    if (email.validity.typeMismatch) { setStatus('Enter a valid email address, such as you@example.com.', 'error'); email.focus(); return; }
    if (!endpoint) { setStatus('Subscriptions are temporarily unavailable. Please try again soon.', 'error'); return; }
    button.disabled = true;
    setStatus('Subscribing…');
    try {
      const response = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: email.value.trim() }) });
      if (!response.ok) throw new Error('Subscription request failed');
      form.reset(); email.removeAttribute('aria-invalid'); setStatus('You’re subscribed. Look out for us on Friday.', 'success');
    } catch { setStatus('We couldn’t subscribe you just now. Please try again.', 'error'); }
    finally { button.disabled = false; }
  });
}
