# Technical SEO audit and implementation plan

Site: https://aviral-goyal.netlify.app/
Hosting: static HTML/CSS/vanilla JavaScript deployed from the repository root on Netlify.

## Audit summary

The site already has useful SEO foundations: unique titles and descriptions, canonical URLs, Open Graph/Twitter metadata, Person/WebSite JSON-LD on the homepage, CreativeWork JSON-LD on project pages, crawlable case studies, robots.txt, sitemap.xml, a custom 404 page, and an offline site-check script.

This branch expands the homepage's search positioning to include software development and web application architecture, activates the previously commented Netlify security headers, defines explicit cache policies, and records a repeatable optimization plan.

This is a repository audit, not a claim that Google rankings or Core Web Vitals have been measured. Run Lighthouse/PageSpeed Insights and Google Search Console after deployment.

## 1. Keyword and search-intent map

| Intent | Topics to target naturally | Best destination |
|---|---|---|
| Branded | Aviral Goyal developer, Aviral Goyal portfolio | Homepage |
| Hiring / evaluation | software developer portfolio, Python developer, full-stack developer, Django Angular developer | Homepage and services/contact |
| AI / ML | machine learning projects, computer vision developer, YOLOv8 OpenCV project | BGLIIN.AI case study |
| Web engineering | Django REST API, Angular application, full-stack web architecture | Case studies |
| BI / analytics | Power BI dashboards, Python data analytics, reporting automation | Homepage and relevant case studies |
| Finance application | personal wealth monitoring system, portfolio analytics application | Wealth Monitoring case study |
| AI-assisted analysis | Python data analyst agent, Streamlit analytics app | AI Data Analyst Agent case study |

Give each page one primary search intent. The homepage describes your breadth; case studies answer specific technical questions. Avoid keyword stuffing and thin pages created only for search terms.

### Metadata examples

Homepage (implemented in index.html):
~~~html
<title>Aviral Goyal | Software Developer, AI/ML &amp; Data Analytics</title>
<meta name="description" content="Aviral Goyal is a software developer working across Python, Django, Angular, AI/ML, computer vision, Power BI dashboards and data analytics. Explore engineering projects and case studies.">
<link rel="canonical" href="https://aviral-goyal.netlify.app/">
~~~

Projects listing: the current #projects URL is an anchor on the homepage, not a separate document. Keep the homepage canonical. If a standalone projects index is built later, it could use:
~~~html
<title>Software Engineering &amp; AI/ML Projects | Aviral Goyal</title>
<meta name="description" content="Explore Aviral Goyal's engineering case studies in Python, Django, Angular, computer vision, machine learning and data analytics.">
<link rel="canonical" href="https://aviral-goyal.netlify.app/projects/">
~~~
Only use that canonical after a real, crawlable /projects/ page exists.

Case-study example:
~~~html
<title>BGLIIN.AI | YOLOv8 Computer Vision &amp; Production Monitoring</title>
<meta name="description" content="Explore an industrial monitoring architecture using RTSP camera capture, YOLOv8 inference, OpenCV, Django APIs and an Angular dashboard.">
<link rel="canonical" href="https://aviral-goyal.netlify.app/projects/bgliin-ai.html">
~~~

Each case study should have its own accurate title, description, canonical URL, social metadata, one descriptive H1 and visible project content. Existing project pages already follow this pattern.

### Heading hierarchy

- One descriptive H1 per document. The homepage's H1 describes web apps, AI tools and data experiences.
- H2 for major sections such as About, Technical Skills, Services, Projects, Architecture, Notes, FAQ and Contact.
- H3 for subsections within a major section; use H4 only for genuine nesting.
- Use headings for content structure, not styling. Mention technologies where they describe actual work, not as a keyword list.

## 2. Netlify technical SEO and delivery

### Headers and caching

The _headers file now activates baseline security headers. The Content Security Policy intentionally permits inline scripts/styles because the current pages use them; this is a compatibility baseline, not a strict CSP. If scripts/styles are externalized, remove inline code and tighten the policy. Test the contact form, Google Fonts, images and theme toggle in a Netlify deploy preview after CSP changes.

CSS/JS receive bounded one-week caching and images 30-day caching; crawler files revalidate hourly. If asset filenames become content-hashed, increase their cache lifetime to public, max-age=31536000, immutable. Avoid one-year immutable caching for unversioned filenames because updated files can remain stale.

Do not add speculative redirects. The current canonical host is aviral-goyal.netlify.app and case studies use explicit .html URLs. Preserve these URLs unless a real custom domain or migration is introduced. If a URL changes, add a one-to-one 301 redirect and update internal links, canonicals and sitemap together.

### robots.txt and sitemap.xml

Keep robots.txt public and allow crawling of public pages. Its Sitemap directive should use the absolute HTTPS sitemap URL. The current sitemap includes the homepage, three project pages and two engineering articles. Add each new public, indexable HTML page and remove deleted pages. Do not include 404.html or the noindex thank-you page. Set lastmod only when a page materially changes.

After deployment, submit https://aviral-goyal.netlify.app/sitemap.xml in Google Search Console and inspect the homepage and each case study. A sitemap aids discovery but does not guarantee indexing.

### Core Web Vitals and assets

Measure mobile and desktop using PageSpeed Insights and Lighthouse. Use the Search Console field report when enough real-user data exists. Good Core Web Vitals thresholds are LCP <= 2.5 seconds, INP <= 200 milliseconds and CLS <= 0.1 at the 75th percentile.

- LCP: identify the actual largest above-the-fold element before optimizing. The hero portrait is already dimensioned, WebP-first with JPG fallback and marked high priority. Do not lazy-load the LCP image. Keep font preconnects limited to origins actually used; consider a system-font fallback or local subset if external font loading is material.
- INP: profile event handlers and third-party scripts; keep interactions lightweight. Defer non-critical scripts and avoid unnecessary analytics/chat widgets.
- CLS: reserve image dimensions/aspect ratios, avoid injecting content above existing content and test font-related shifts.
- Images: use WebP/AVIF where practical with fallbacks, compress thumbnails, specify width and height, and lazy-load below-the-fold images. Do not lazy-load the LCP image.
- CSS/JS: keep the static site lean and remove unused code only after verifying references. Avoid large libraries for simple interactions.
- Third parties: audit fonts, analytics and embeds for performance and privacy impact.

## 3. Structured data

The homepage already has Person and WebSite JSON-LD. Keep official profile links in sameAs and ensure schema details match visible content.

A reusable case-study schema example (the current pages use CreativeWork, a suitable conservative choice for engineering write-ups):
~~~html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "@id": "https://aviral-goyal.netlify.app/projects/bgliin-ai.html#project",
  "name": "BGLIIN.AI",
  "headline": "BGLIIN.AI: Industrial Computer Vision and Production Monitoring",
  "description": "An industrial monitoring case study covering RTSP camera capture, YOLOv8 inference, OpenCV, Django APIs and an Angular dashboard.",
  "url": "https://aviral-goyal.netlify.app/projects/bgliin-ai.html",
  "inLanguage": "en",
  "author": {
    "@type": "Person",
    "@id": "https://aviral-goyal.netlify.app/#person",
    "name": "Aviral Goyal",
    "url": "https://aviral-goyal.netlify.app/"
  },
  "keywords": ["Computer vision", "YOLOv8", "OpenCV", "Django", "Angular", "RTSP"],
  "isPartOf": {
    "@type": "WebSite",
    "@id": "https://aviral-goyal.netlify.app/#website",
    "url": "https://aviral-goyal.netlify.app/",
    "name": "Aviral Goyal — Portfolio"
  }
}
</script>
~~~
Use SoftwareSourceCode only when the page primarily documents a specific source artifact and its repository/language details are accurate. Structured data helps search engines understand a page but does not guarantee rich results or higher rankings. Validate JSON-LD with Schema Markup Validator and the Rich Results Test where applicable.

## 4. Experience, trust and internal linking

Each case study should explain:
1. The problem or workflow being addressed.
2. Your personal contribution.
3. Architecture choices and trade-offs.
4. Failure modes and constraints encountered.
5. How readers can inspect the implementation (repository, demo, diagram or redacted screenshot).
6. What was measured and how.

Distinguish implemented features from planned work. Do not invent client names, testimonials, production metrics, model accuracy, user counts or performance gains. Use redacted diagrams and synthetic data for confidential systems. Keep resume/profile details consistent across the site and social profiles.

Internal links should connect:
- Homepage project cards to their matching case studies.
- Skills to relevant case studies (several skill cards already do this).
- Case studies to related engineering notes and back to projects/contact.
- Articles to related case studies and the homepage.
- Every page to a clear home/portfolio navigation path.

Use descriptive anchor text such as “YOLOv8 multi-camera monitoring case study” rather than repeated “click here.” Avoid thin technology-tag pages unless they contain useful unique content.

## 5. Prioritized rollout

### High
- [x] Update homepage title, description and social copy to represent software development alongside AI/ML and analytics.
- [x] Activate Netlify security headers and explicit cache policies.
- [ ] Deploy a Netlify preview and test CSP compatibility, contact form, theme toggle, fonts and image loading.
- [ ] Run python3 scripts/check_site.py and fix every error before merging.
- [ ] Run mobile/desktop Lighthouse and PageSpeed Insights; record actual LCP, INP diagnostics, CLS, page weight and failed requests.
- [ ] Verify sitemap, robots and canonicals; submit the sitemap in Search Console.

### Medium
- [ ] Add original, approved, privacy-safe screenshots to case studies with descriptive alt text, dimensions and lazy loading where appropriate.
- [ ] Expand case studies with specific contribution, implementation decisions, limitations and reproducible measurements where available.
- [ ] Add related-article links and contextual internal links between case studies.
- [ ] Validate Person and CreativeWork JSON-LD after edits.

### Low
- [ ] Consider a dedicated projects index only if it provides meaningful unique content and stable URLs.
- [ ] Consider local font hosting/subsetting after measuring whether external fonts are a material bottleneck.
- [ ] Consider hashed asset filenames and immutable caching if a build pipeline is introduced.

## Verification

Run locally:
~~~bash
python3 scripts/check_site.py
~~~

After deployment, check:
- https://aviral-goyal.netlify.app/robots.txt
- https://aviral-goyal.netlify.app/sitemap.xml
- Every canonical project/article URL returns HTTP 200.
- /thank-you.html remains noindex and is absent from the sitemap.
- The custom 404 response returns an actual 404 status.
- Security and cache headers are present in DevTools or with curl -I.

Search visibility depends on content usefulness, external signals, competition and search-engine decisions; no implementation can guarantee rankings.
