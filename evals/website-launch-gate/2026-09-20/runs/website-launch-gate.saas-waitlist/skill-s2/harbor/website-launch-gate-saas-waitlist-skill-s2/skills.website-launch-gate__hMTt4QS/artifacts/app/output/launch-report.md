# AcmeFlow launch report

## Decision: NO-GO

The frontend is ready for a production host, but launch is blocked until the real waitlist service, production hostname/HTTPS behavior, and host-level 404 routing are connected and verified. No deployment or external account changes were made.

| Check | Status | Evidence | Action |
|---|---|---|---|
| 1. Privacy policy | PASS | `/privacy.html` exists and is linked beside the email form and in the footer. | Have counsel/owner approve the text and add a dedicated privacy contact before collecting data. |
| 2. Terms | PASS | `/terms.html` covers this pre-launch website and is linked in the footer. | Have counsel/owner approve before launch. |
| 3. No exposed secrets | PASS | Removed the browser-shipped `sk_live_…` value; repository scan for common secret patterns returned no matches. | Keep service credentials only in server-side environment configuration. |
| 4. HTTPS and redirect | UNKNOWN | No production URL or hosting configuration was supplied. | Enable HTTPS and verify HTTP → HTTPS at the chosen host. |
| 5. Cookie consent | N/A | The site sets no cookies and includes no analytics, advertising, or other non-essential trackers. | Reassess before adding any such tooling. |
| 6. Titles and descriptions | PASS | Home, privacy, terms, and 404 pages have distinct titles and descriptions; 404 is `noindex`. | None. |
| 7. Social preview | PASS | Home includes Open Graph/Twitter metadata and a verified 1200×630, 46 KB PNG. | After the hostname is known, use an absolute production URL for `og:image` and validate in platform debuggers. |
| 8. Favicon | PASS | `/favicon.svg` returned HTTP 200 in the local server check. | None. |
| 9. Sitemap and robots | FAIL | `/robots.txt` exists and returned 200; a valid sitemap cannot be authored without the production hostname. | Add absolute production URLs to `sitemap.xml`, then reference it from `robots.txt`. |
| 10. Image alternatives | PASS | The only content graphic is the social preview with `og:image:alt`; the favicon/logo mark is decorative or has an accessible parent label. | None. |
| 11. Image sizing | PASS | Social card is exactly 1200×630 and 46 KB; favicon is vector. | None. |
| 12. Load performance | PASS | Playwright/Chromium local check: mobile DCL 22 ms, desktop DCL 19 ms; both fully settled in ~0.52 s. Assets are 56 KB total excluding HTML overhead. | Re-run Lighthouse against production because local results exclude network/server latency. |
| 13. Contrast and focus | PASS | Calculated key text/background ratios range from 5.87:1 to 17.79:1; visible `:focus-visible` styles and skip link are present. | None. |
| 14. Mobile behavior | PASS | Chromium at 390×844 showed no horizontal overflow (390 px scroll/client widths); form and benefit cards stack cleanly. Desktop checked at 1440×900. | Test on physical iOS/Android devices if available. |
| 15. Custom 404 | UNKNOWN | `/404.html` exists, is useful, and has a home recovery link; the local static server is not representative of production fallback routing. | Configure the production host to serve it with HTTP 404 status, then verify. |
| 16. Links | PASS | Home, privacy, terms, JS, CSS, favicon, social card, robots, and 404 assets all returned HTTP 200 locally. No external links exist. | Recheck after deployment. |
| 17. Form states | FAIL | Invalid-email and mocked-success flows passed in Chromium; failure UI is implemented and does not claim success. `/api/waitlist` does not exist in this repository, so a real submission cannot succeed. | Connect the POST endpoint and verify successful, duplicate, validation, rate-limit, and server-error responses end-to-end. |
| 18. Abuse protection | UNKNOWN | Client sends a hidden honeypot and elapsed time, but meaningful enforcement must be server-side. | Validate the honeypot and timing server-side; add rate limiting and monitoring. |
| 19. Analytics | N/A | No analytics was requested or added. | If added later, make it environment-aware and obtain consent where required. |
| 20. Primary CTA | PASS | The page has one primary action, “Join the waitlist”; the header link targets the same form. | None. |

## Verification record

- Chromium render and interaction checks: mobile 390×844 and desktop 1440×900.
- Form checks: required/format error and mocked HTTP 201 success passed; honest failure state implemented.
- Asset/link HTTP checks: all repository routes and assets listed above returned 200 locally.
- JavaScript syntax: `node --check app.js` passed with no output.
- Secret scan: no common live/test key, API key, client secret, password, or bearer-token pattern remains.
- Not verified without production infrastructure: real waitlist delivery, HTTPS/redirects, server-side abuse controls, true 404 status, sitemap hostnames, production performance, and social crawler rendering.

**Final decision: NO-GO** until checks 4, 9, 15, 17, and 18 are resolved or verified.
