(() => {
  document.querySelectorAll('[data-year]').forEach((n) => { n.textContent = new Date().getFullYear(); });
  const form = document.querySelector('#access-form'); if (!form) return;
  const email = form.querySelector('input[type="email"]'); const message = form.querySelector('#form-message'); const button = form.querySelector('button');
  form.addEventListener('submit', async (event) => {
    event.preventDefault(); message.className = 'form-message';
    if (!email.value.trim() || !email.validity.valid) { message.textContent = email.value.trim() ? 'Enter a valid email address, such as you@company.com.' : 'Enter your work email to continue.'; message.classList.add('error'); email.setAttribute('aria-invalid', 'true'); email.focus(); return; }
    email.removeAttribute('aria-invalid'); button.disabled = true; button.textContent = 'Joining…';
    try { const response = await fetch(form.action, {method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({email:email.value.trim()})}); if (!response.ok) throw new Error('Submission failed'); form.reset(); message.textContent = 'You’re on the list. We’ll be in touch soon.'; message.classList.add('success'); }
    catch { message.textContent = 'We couldn’t save your email. Please try again in a moment.'; message.classList.add('error'); }
    finally { button.disabled = false; button.textContent = 'Start free'; }
  });
})();
