# Orbit Notes launch report

## Decision: NO-GO

The static site itself is substantially launch-ready, but the production hostname is unknown, so HTTPS, redirects, canonical/social URLs, sitemap generation, and production 404 behavior cannot be completed or verified. The `orbitnotes.app` contact mailboxes used by the calls to action and legal pages must also be confirmed before launch.

| Check | Status | Evidence | Action |
|---|---|---|---|
| 1. Privacy policy | PASS | `/privacy.html` exists, is linked in the footer, and accurately describes this static site's email-only contact flow. | Have the business owner confirm it matches actual practices. |
| 2. Terms | PASS | `/terms.html` exists and distinguishes website terms from future product terms. | Add product-specific terms before accounts are offered. |
| 3. No exposed secrets | PASS | Repository scan for common secret/key/token patterns returned no findings. | Keep secrets out of public files. |
| 4. HTTPS and redirect | UNKNOWN | No production URL or hosting configuration was supplied; only local HTTP was tested. | Configure HTTPS and HTTP→HTTPS at the host, then verify. |
| 5. Cookie consent | N/A | Source and rendered page use no cookies, analytics, ads, or non-essential storage. | Reassess before adding tracking. |
| 6. Titles and descriptions | PASS | Home, privacy, terms, and 404 each have specific titles and descriptions. | None. |
| 7. Social preview | UNKNOWN | OG/Twitter metadata and a 1200×630, 174 KB PNG exist, but `og:image` cannot be made absolute without the production origin. | Add the final absolute OG URL and test it after the hostname is known. |
| 8. Favicon | PASS | `/favicon.svg` returned HTTP 200 locally and rendered without browser errors. | None. |
| 9. Sitemap and robots | FAIL | `/robots.txt` exists and allows indexing; no valid absolute-URL sitemap can be created without the production hostname. | Add `sitemap.xml` and its absolute URL to `robots.txt` once the domain is known. |
| 10. Image alternatives | PASS | The page has no meaningful content images; decorative ring art is CSS and absent from the accessibility tree. OG image has descriptive `og:image:alt`. | None. |
| 11. Image sizing/compression | PASS | Social image is exactly 1200×630 and 174,358 bytes; no page-content images are downloaded. | None. |
| 12. Load performance | PASS | Playwright/Chromium local cold navigation: DOM ready 30 ms/mobile and 33 ms/desktop; load 32 ms/mobile and 33 ms/desktop. No runtime errors. | Re-run Lighthouse against production because local timing excludes network/host behavior. |
| 13. Contrast and focus | PASS | Dark green on warm white, white/lime on dark green, visible 3 px focus outlines, and a keyboard skip link were verified in source and render. | Confirm with production Lighthouse/axe. |
| 14. Responsive layout | PASS | Chromium at 375×900 and 1440×900 showed no horizontal overflow; mobile screenshot was visually inspected and controls remained usable. | None. |
| 15. Custom 404 | UNKNOWN | `404.html` has a useful recovery link; the local server correctly returns 404 for unknown paths but does not map that response to this file. | Configure the host to serve `404.html` while retaining status 404, then verify. |
| 16. Links | UNKNOWN | All internal asset/page URLs returned HTTP 200 locally and the section anchor resolves. `mailto:` destinations cannot be validated locally. | Confirm `hello@`, `privacy@`, and `legal@orbitnotes.app` exist and receive mail. |
| 17. Forms | N/A | No form is present; conversion uses the visitor's email client. | If a web form is added, test validation, failure, and success states. |
| 18. Form abuse protection | N/A | No public form or submission endpoint exists. | Add proportionate rate limiting/spam controls with any future form. |
| 19. Analytics | N/A | No analytics was requested or detected. | Add only with an explicit measurement and consent plan. |
| 20. Primary CTA | UNKNOWN | Each main section has one clear “Start free” CTA, all targeting `hello@orbitnotes.app`; mailbox ownership/delivery is unverified. | Confirm the mailbox or replace the destinations with the real onboarding route. |

## Verification record

- Served the site locally and received HTTP 200 for `/`, privacy, terms, favicon, social image, and robots; an unknown route returned HTTP 404.
- Rendered the homepage in headless Chromium at 375 px and 1440 px widths; found no console errors, failed images, or horizontal overflow.
- Visually inspected the 375 px full-page render.
- Confirmed the social image dimensions and file size with ImageMagick.
- Scanned public files for common secret patterns.
- Did not deploy, alter production infrastructure, or create external accounts.

## Remaining launch blockers

1. Supply the final production origin and configure/verify HTTPS, redirects, canonical/OG URLs, `sitemap.xml`, and custom 404 routing.
2. Confirm the three `@orbitnotes.app` mailboxes exist and that “Start free” via email is the intended onboarding path.
3. Business/legal owner should approve the privacy and terms text against actual company and product practices.
