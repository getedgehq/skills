const form = document.querySelector('#checkout');
const email = document.querySelector('#email');
const card = document.querySelector('#card');
const terms = document.querySelector('#terms');
const website = document.querySelector('#website');
const submit = document.querySelector('#submit');
const status = document.querySelector('#status');

function setError(input, message) {
  const output = document.querySelector(`#${input.id}-error`);
  input.setAttribute('aria-invalid', String(Boolean(message)));
  if (output) output.textContent = message;
}
function validate() {
  const validEmail = email.validity.valid;
  setError(email, validEmail ? '' : 'Enter a valid email address.');
  setError(card, card.value.trim() ? '' : 'Enter your secure payment token.');
  setError(terms, terms.checked ? '' : 'You must agree before continuing.');
  return validEmail && Boolean(card.value.trim()) && terms.checked;
}
form.addEventListener('submit', async (event) => {
  event.preventDefault(); status.className = 'status'; status.textContent = '';
  if (!validate() || website.value) return;
  submit.disabled = true; submit.textContent = 'Processing…';
  try {
    const response = await fetch('/api/pay', {method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json'}, credentials:'same-origin', body:JSON.stringify({email:email.value.trim(),card:card.value.trim()})});
    if (!response.ok) throw new Error('Payment was not completed.');
    status.className = 'status success'; status.textContent = 'Your seat is reserved. Check your email for confirmation.'; form.reset();
  } catch (_) {
    status.className = 'status failure'; status.textContent = 'We could not complete your payment. Your card was not charged. Please try again.';
  } finally { submit.disabled = false; submit.textContent = 'Pay $49'; }
});
[email,card,terms].forEach((input) => input.addEventListener('input', () => setError(input,'')));
