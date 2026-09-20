# Signal Weekly launch report

**Decision: NO-GO** — the static files are substantially improved, but launch is blocked by the missing subscription service configuration and production domain details.

| Check | Status | Evidence | Action |
|---|---|---|---|
| 1. Privacy policy | PASS | `privacy.html` exists and is linked beside the email field. | Confirm the policy matches the selected email provider and add the operator's contact details. |
| 2. Terms | N/A | The site offers a free newsletter with no account, purchase, or stated contractual service. | Reassess if paid products or accounts are added. |
| 3. Secret exposure | PASS | Repository scan found no key, token, password, or analytics credential. | Keep provider credentials server-side. |
| 4. HTTPS and redirect | UNKNOWN | No deployed URL or hosting configuration was supplied. | Verify the production certificate and HTTP-to-HTTPS redirect after hosting is configured. |
| 5. Cookie consent | N/A | The placeholder tracker and cookie banner were removed; current files set no cookies. | Add consent controls before adding non-essential tracking. |
| 6. Titles and descriptions | PASS | Home, privacy, and 404 documents have specific titles and descriptions. | None. |
| 7. Social preview | UNKNOWN | 1200×630 `social-card.png` and Open Graph/Twitter metadata exist, but the final absolute production URL is unknown. | Set absolute `og:url` and `og:image` values after the domain is confirmed, then test in platform debuggers. |
| 8. Favicon | PASS | Local request returned `200 image/svg+xml` for `favicon.svg`. | None. |
| 9. Sitemap and robots | FAIL | Both files exist and parse, but `sitemap.xml` intentionally contains `example.com` and `robots.txt` cannot name the final sitemap yet. | Replace with the production origin and add the absolute sitemap directive. |
| 10. Alternative text | PASS | The page has no content images; the social image has an `og:image:alt` description. | None. |
| 11. Image sizing | PASS | Social card is 1200×630 and 108,662 bytes; favicon is vector. | None. |
| 12. Performance | UNKNOWN | Assets are dependency-free and small, but Lighthouse could not run because this environment has no Chrome/Chromium executable. | Run mobile and desktop Lighthouse against the production-like preview. |
| 13. Contrast and focus | PASS | Calculated contrast ratios: body 14.85:1, muted 5.82:1, button 7.28:1, focus 5.08:1, error 8.24:1; explicit `:focus-visible` styling exists. | Confirm with a rendered accessibility audit. |
| 14. Mobile layout | UNKNOWN | Responsive CSS stacks the form below 544px and uses fluid type/widths; no browser was available for rendered viewport verification. | Inspect at 320, 375, 768, and 1440px before launch. |
| 15. Custom 404 | UNKNOWN | `404.html` has a recovery link, but correct unknown-route status/rendering depends on the eventual host. | Configure the host to serve it with HTTP 404 and verify. |
| 16. Links | PASS | Linkinator crawled all five reachable local links with HTTP 200. | Re-run after production URLs are added. |
| 17. Form states | FAIL | Required and malformed email states plus an unconfigured-service error are implemented. There is no real endpoint, success response, or server-failure integration to verify. | Set the form `action`, remove `data-unconfigured`, and test invalid, successful, duplicate, unsubscribe, and provider-failure flows. |
| 18. Form abuse protection | UNKNOWN | No subscription backend or provider is configured. | Enable the chosen provider's rate limiting, bot/honeypot, and confirmed-opt-in controls. |
| 19. Analytics | N/A | Analytics was not requested; the placeholder third-party tracker was removed. | Add only with a measurement plan and required consent. |
| 20. Primary CTA | FAIL | The single primary CTA is clear, but its subscription destination is deliberately disabled until a real endpoint is supplied. | Connect it to the production mailing list before launch. |

## Verification record

- `npx --yes html-validate index.html privacy.html 404.html` — passed after fixes.
- `npx --yes linkinator http://127.0.0.1:4173 --recurse` — five local resources checked, all HTTP 200.
- `node --check script.js` — passed.
- XML parsing of `sitemap.xml` — passed.
- Local HTTP checks — home, privacy, favicon, and social image returned 200 with expected content types.
- Secret-pattern scan — no exposed credentials found.
- Lighthouse — attempted, blocked because Chrome/Chromium is unavailable; no score is claimed.

## Remaining launch blockers

1. Supply the real email subscription endpoint/provider configuration and verify success, failure, confirmed opt-in, unsubscribe, and abuse controls.
2. Supply the production domain; replace `example.com`, add absolute social/canonical URLs and the sitemap directive, then verify HTTPS and 404 behavior on the chosen host.
3. Confirm the privacy wording and operator contact details against the actual business and email provider.
4. Run rendered mobile/desktop and Lighthouse checks in a browser-equipped preview environment.
