const form = document.querySelector('#waitlist');
const emailInput = document.querySelector('#email');
const statusMessage = document.querySelector('#status');
const submitButton = form.querySelector('button[type="submit"]');
const defaultButtonLabel = submitButton.textContent;

document.querySelector('#year').textContent = new Date().getFullYear();

function showStatus(message) {
  statusMessage.textContent = message;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  showStatus('');
  emailInput.removeAttribute('aria-invalid');

  if (!emailInput.validity.valid) {
    emailInput.setAttribute('aria-invalid', 'true');
    showStatus('Enter a valid work email to join.');
    emailInput.focus();
    return;
  }

  if (form.elements.company_website.value) {
    form.reset();
    showStatus('Thanks — you’re on the list.');
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = 'Joining…';

  try {
    const response = await fetch('/api/waitlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: emailInput.value.trim() }),
    });

    if (!response.ok) throw new Error(`Signup failed with status ${response.status}`);

    form.reset();
    showStatus('Thanks — you’re on the list.');
  } catch (error) {
    console.error('Waitlist signup failed:', error);
    showStatus('We couldn’t add you just now. Please try again shortly.');
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = defaultButtonLabel;
  }
});
