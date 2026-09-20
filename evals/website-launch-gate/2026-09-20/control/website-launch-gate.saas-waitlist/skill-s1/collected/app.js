(() => {
  "use strict";
  const form = document.querySelector("#waitlist");
  const email = document.querySelector("#email");
  const status = document.querySelector("#form-status");
  const button = form?.querySelector("button[type='submit']");
  const year = document.querySelector("#year");
  if (year) year.textContent = new Date().getFullYear();
  if (!form || !email || !status || !button) return;
  const setStatus = (message, type = "") => { status.textContent = message; status.dataset.type = type; };
  form.addEventListener("submit", async (event) => {
    event.preventDefault(); setStatus("");
    if (!email.validity.valid) { email.setAttribute("aria-invalid", "true"); setStatus("Enter a valid work email to continue.", "error"); email.focus(); return; }
    email.removeAttribute("aria-invalid"); button.disabled = true; button.setAttribute("aria-busy", "true");
    const originalLabel = button.innerHTML; button.textContent = "Sending…";
    try {
      const response = await fetch(form.action, { method: "POST", headers: { "Accept": "application/json", "Content-Type": "application/json" }, body: JSON.stringify({ email: email.value.trim() }) });
      if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
      form.reset(); setStatus("You're on the list. We'll be in touch.", "success");
    } catch (error) {
      console.error("Waitlist submission failed:", error); setStatus("We couldn't submit that right now. Please try again in a moment.", "error");
    } finally { button.disabled = false; button.removeAttribute("aria-busy"); button.innerHTML = originalLabel; }
  });
  email.addEventListener("input", () => { email.removeAttribute("aria-invalid"); if (status.dataset.type === "error") setStatus(""); });
})();
