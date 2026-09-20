# Launch report

## Ready

- Rebuilt the checkout as a responsive, dependency-free page while retaining the workshop registration positioning, “Reserve your seat” message, and $49 price.
- Replaced the insecure placeholder `http://api.workshop.example/pay` request with a same-origin `POST /api/pay` JSON request.
- Added semantic labels, keyboard focus behavior, live validation/status messaging, a no-JavaScript notice, mobile layout, reduced-motion support, and clear loading, error, and confirmation states.
- Kept payment data out of URLs and avoided storing or logging it in the browser.

## Verified

- JavaScript syntax check passes.
- HTML parses with unique required IDs; CSS blocks are balanced.
- Local static-server smoke test returns the page, stylesheet, and script successfully.
- Headless Chromium checks pass at 390×844 and 1440×900: no horizontal overflow, required-field and email-format validation work, and a mocked successful API response shows the confirmation state and purchaser email.
- Visual desktop review completed; no external fonts, images, scripts, analytics, or account dependencies were added.

## Blocked before accepting real payments

- This repository contains no payment backend or provider integration. Production must supply same-origin `POST /api/pay`, accept JSON `{ "email": "…", "card": "…" }`, and return a 2xx response on success or JSON `{ "message": "…" }` with an error status on failure.
- The “Payment token” field assumes an existing provider-generated token. Before launch, connect the provider’s hosted/secure tokenization UI and confirm the backend charges exactly **$49 USD**. Do not collect raw card numbers with this field.
- Confirm the real workshop description, registration/cancellation terms, confirmation-email delivery, domain HTTPS, and production security headers; those business and hosting details are not present in the repository.
