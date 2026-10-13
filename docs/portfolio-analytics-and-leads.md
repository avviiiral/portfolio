# Portfolio analytics and freelance lead workflow

This guide is intentionally separate from the public homepage. The website includes optional event hooks, but no analytics provider is loaded until the site owner configures an account.

## 1. Configure analytics

1. Create a Google Analytics 4 property and a web data stream for `https://aviral-goyal.netlify.app`.
2. Copy the Measurement ID (format: `G-XXXXXXXXXX`). This identifier is designed to be public; do not put API secrets or credentials in the frontend.
3. Add the official Google tag snippet to the `<head>` of `index.html`, replacing the placeholder with your real Measurement ID. Do not commit an example or fake ID.
4. Verify the tag with Google Tag Assistant and the GA4 Realtime report.
5. Check that the site's `trackPortfolioEvent()` hook records events after the tag is loaded. Suggested events: `contact_cta_click` and `outbound_contact_or_project_click`.
6. Review consent and privacy obligations for the audiences you serve before enabling analytics. Avoid collecting form field values as analytics event parameters.

### Content-Security-Policy

`_headers` ships a Content-Security-Policy that only allows this site's own files and Google Fonts. Before adding the GA4 snippet, extend the policy in `_headers` or the browser will block the tag silently. Per Google's tag-manager CSP guidance, add:

- `script-src`: `https://*.googletagmanager.com`
- `img-src`: `https://*.google-analytics.com https://*.googletagmanager.com`
- `connect-src`: `https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com`

Deploy to a Netlify preview first and confirm the browser console shows no CSP violations.

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
