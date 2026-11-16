# Portfolio analytics and freelance lead workflow

This guide is intentionally separate from the public homepage. The website includes optional event hooks, but no analytics provider is loaded until the site owner configures an account.

## 1. Configure Google Tag Manager and GA4

The site uses the existing Google Tag Manager web container `GTM-TT9Q7MHF`. Its install snippet is included once in the `<head>` of every HTML page, including project notes and the enquiry confirmation page. The public container ID is not a secret.

1. In Google Tag Manager, open the `GTM-TT9Q7MHF` container and create or select the GA4 Google tag.
2. Set that tag's Measurement ID (format: `G-XXXXXXXXXX`) and use an **All Pages** trigger. The Measurement ID belongs in the GTM workspace; do not add a second Google snippet to the website.
3. To collect the portfolio's existing custom events, create GA4 Event tags and Custom Event triggers for `contact_cta_click` and `outbound_contact_or_project_click`. The site's `gtag()` helper pushes those events to `dataLayer`; GTM must have matching tags/triggers and the container changes must be published.
4. Use GTM Preview / Tag Assistant, then confirm page views and test events in GA4 Realtime. Check the browser console and Network panel for blocked requests.
5. Review the consent and privacy obligations for the audiences you serve before enabling analytics. Do not send contact-form field values, message contents, or other personal information as event parameters.

### Content-Security-Policy

Netlify injects its Real User Monitoring (RUM) script on production pages. The CSP allows Netlify's documented script host and the collection endpoint visible in the browser console. Google Tag Manager and GA4 have a separate, limited allowlist.

The `_headers` policy permits:

- `script-src`: `https://www.googletagmanager.com` and `https://netlify-rum.netlify.app`
- `img-src`: `https://www.googletagmanager.com` and `https://*.google-analytics.com`
- `connect-src`: `https://www.googletagmanager.com`, `https://*.google-analytics.com`, `https://*.google.com`, and `https://ingesteer.services-prod.nsvcs.net`
- `frame-src`: `https://www.googletagmanager.com`

The policy does not add `unsafe-eval`, wildcard hosts, or advertising domains. If you later add Google Ads or other GTM tags, extend the relevant CSP directives only for the hosts those tags actually require. Netlify RUM is production-only; validate its requests on the live deployment, not only on a local preview.

## 2. Configure Google Search Console

1. Add the deployed site as a URL-prefix property: `https://aviral-goyal.netlify.app/`.
2. Complete ownership verification using the method Google provides (HTML file, HTML meta tag, or DNS).
3. Submit `https://aviral-goyal.netlify.app/sitemap.xml`.
4. Inspect the homepage and case-study URLs after deployment. Review indexing, impressions, clicks, and queries over time; results may take days or weeks to appear.

## 3. Test the contact form after deployment

- Submit a test enquiry and confirm it appears in Netlify Forms.
- Confirm the success redirect reaches `/thank-you.html`.
- Confirm notification delivery is configured in Netlify and the notification email arrives.
- Check spam protection and test the form on a phone.
- Do not assume a successful browser redirect means the notification email was delivered; verify both.

## 4. Use the lead tracker safely

Copy `docs/freelance-lead-tracker-template.csv` to a private location (for example, a local spreadsheet or private drive) before entering real prospect information. Do **not** commit a populated tracker to this public repository.

Suggested stages: New, Replied, Discovery, Proposal, Won, Lost, Follow-up. Set a next-follow-up date for every active lead and review it weekly.

## 5. Measure outcomes

Track a small funnel rather than vanity metrics:

- Qualified portfolio visits
- Project/contact CTA clicks
- Completed enquiries
- Discovery conversations booked
- Proposals sent
- Projects won

Compare trends over several weeks before making major design changes. Do not add fabricated testimonials, client logos, conversion rates, or project results.
