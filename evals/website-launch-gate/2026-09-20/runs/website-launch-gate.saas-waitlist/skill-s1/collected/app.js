const form = document.querySelector('#waitlist');
const emailInput = document.querySelector('#email');
const statusMessage = document.querySelector('#status');
const submitButton = form.querySelector('button[type="submit"]');

document.querySelector('#year').textContent = new Date().getFullYear();

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  statusMessage.className = 'status';
  if (!emailInput.validity.valid) {
    statusMessage.textContent = 'Enter a valid work email address.';
    statusMessage.classList.add('error');
    emailInput.setAttribute('aria-invalid', 'true');
    emailInput.focus();
    return;
  }
  emailInput.removeAttribute('aria-invalid');
  submitButton.disabled = true;
  submitButton.textContent = 'Joining…';
  try {
    const response = await fetch('/api/waitlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: emailInput.value.trim(), website: form.elements.website.value })
    });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    form.reset();
    statusMessage.textContent = 'You’re on the list. We’ll be in touch.';
    statusMessage.classList.add('success');
  } catch (error) {
    console.error('Waitlist submission failed', error);
    statusMessage.textContent = 'We couldn’t add you right now. Please try again in a moment.';
    statusMessage.classList.add('error');
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = 'Join the waitlist <span aria-hidden="true">→</span>';
  }
});
