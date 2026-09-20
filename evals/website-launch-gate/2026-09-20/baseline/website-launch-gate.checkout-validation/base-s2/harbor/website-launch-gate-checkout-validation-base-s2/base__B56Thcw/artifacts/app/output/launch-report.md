# Launch report

## Ready

- Rebuilt the page as a responsive, production-friendly single-page checkout while retaining the workshop-seat positioning and $49 price.
- Replaced unsafe card-token collection and the insecure hard-coded HTTP payment URL with a same-origin `POST /api/checkout` handoff to a hosted payment page.
- Added email validation, loading/error states, safe checkout-URL validation, semantic labels, live error announcements, visible focus states, reduced-motion support, mobile layout, page metadata, and crawler rules.
- Added ignore rules for local secrets and common generated files.

## Verified on 2026-09-20

- `index.html`, `checkout.js`, and `robots.txt` serve successfully from a local static HTTP server.
- JavaScript passes `node --check`.
- Smoke checks confirmed the viewport metadata, form controls, email input, accessibility announcements, and reduced-motion styling are present.
- Invalid/missing email is blocked client-side; checkout failures restore the button and show a user-facing retry message.

## Blocked before taking payments

- **Payment backend is not present.** Implement `POST /api/checkout` to accept `{ "email": "…" }` and return `{ "url": "https://…" }` for a hosted checkout session priced at $49. The current static server correctly cannot fulfill this request, so no customer can be charged yet.
- Confirm and add the real workshop name, date/time/time zone, delivery format, organizer/contact details, refund terms, and privacy/terms links. None were supplied, so the page deliberately does not invent them.
- Once the production domain is known, add its canonical URL and social-sharing image, then run a final checkout in the payment provider's test mode and a mobile/desktop browser pass.

No deployment or external account creation was performed.
