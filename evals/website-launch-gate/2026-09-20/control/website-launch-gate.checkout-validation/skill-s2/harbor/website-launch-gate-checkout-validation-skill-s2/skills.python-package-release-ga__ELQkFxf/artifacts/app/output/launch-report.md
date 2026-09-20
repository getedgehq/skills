# Launch report

## Status

**Not ready to take payments until the checkout-session endpoint is connected.** The customer-facing page itself is ready to serve as a static site and now fails safely while that dependency is absent.

## Fixed

- Replaced the insecure `http://` payment request and browser-side card/token collection with a secure checkout handoff. The browser now sends only the customer email to a same-origin session endpoint and accepts only an HTTPS checkout URL in response.
- Added email validation, accessible labels and error/status announcements, loading state, retryable failure handling, and a no-JavaScript message.
- Added responsive desktop/mobile styling while retaining the workshop, seat-reservation, and $49 positioning.
- Added page metadata and a restrictive content security policy; no third-party scripts, fonts, trackers, or assets are loaded.

## Verified

- `checkout.js` passes `node --check`.
- Page and stylesheet return HTTP 200 from a local static server.
- Chromium render checked at 1280×720 and 390×844; no horizontal overflow or clipped controls observed.
- Empty, malformed, and valid email paths behave as intended; with no endpoint configured, valid submission fails closed with a clear message and sends no request.
- Browser console is clean on page load.
- Repository scan found no remaining insecure payment URL or raw card-field submission.

## Launch blocker / integration contract

Set the `checkout-endpoint` meta value in `index.html` to a **same-origin** HTTPS path (for example, `/api/checkout-session`) backed by the chosen payment provider. It must:

1. Accept `POST` JSON: `{ "email": "person@example.com" }`.
2. Create a server-side checkout session for **USD $49**; price and product identity must be fixed server-side, not accepted from the browser.
3. Return successful JSON: `{ "checkoutUrl": "https://…" }`.
4. Enforce availability/capacity, idempotency, rate limiting, input validation, and provider webhook verification server-side.
5. Send the promised confirmation email only after verified successful payment.

The production web server should also send the CSP as an HTTP response header (and add `frame-ancestors 'none'` there), plus HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, and an appropriate `Permissions-Policy`. Those host-level settings cannot be implemented in this static-only repository.
