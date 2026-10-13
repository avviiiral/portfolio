# Aviral Goyal — Portfolio

Static portfolio site for Aviral Goyal (full-stack development, AI/ML, data analytics).

**Live site:** https://aviral-goyal.netlify.app/

There is no build step: plain HTML, CSS and a little vanilla JavaScript, deployed on Netlify.

## What's in this repo

| Path | Purpose |
|---|---|
| `index.html` | Single-page homepage (about, skills, services, FAQ, projects, contact form) |
| `projects/*.html` | Case-study pages linked from the project cards |
| `articles/*.html` | Short engineering notes on reliability and auditable data workflows |
| `portfolio-refresh.css`, `portfolio.js` | Accessible, low-motion layout refinements and the architecture switcher |
| `thank-you.html` | Redirect target after a Netlify Forms submission (`noindex`) |
| `404.html` | Custom "page not found" page (served automatically by Netlify) |
| `_headers` | Netlify security headers, including the Content-Security-Policy |
| `robots.txt`, `sitemap.xml` | Crawler hints; keep the sitemap in sync with `projects/` |
| `profile.jpg`, `profile.webp` | Portrait (WebP is served first, JPG is the fallback) |
| `og-image.jpg` | 1200×630 social-share image used by Open Graph and Twitter cards |
| `Aviral_Goyal_Resume.pdf` | Downloadable resume |
| `docs/` | Analytics set-up notes and a private-lead-tracker template |
| `scripts/check_site.py` | Offline checks (broken links, sitemap, meta tags, markup) |

## Preview locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Netlify Forms only work once deployed, so the contact form will not submit locally.

## Checks

```bash
python3 scripts/check_site.py
```

The checker validates page titles/descriptions/canonicals, social metadata, markup structure, duplicate IDs, image alt text, safe external links, internal links/anchors, referenced homepage assets, and sitemap consistency. The same script runs in GitHub Actions on every push and pull request (`.github/workflows/site-checks.yml`). It needs only Python 3.

## Search, accessibility and performance

- Keep page titles and descriptions specific to each page, and update canonical/social metadata and `sitemap.xml` together when URLs change.
- Use descriptive case-study content and real screenshots only. Mask any private, financial, client or production details before publishing.
- Preserve keyboard focus visibility, skip navigation, meaningful image alternatives and reduced-motion support.
- The featured-project SVGs are schematic architecture illustrations, not screenshots of a deployed application. Replace or supplement them with approved, redacted product screenshots when available.
- Check the live site with Lighthouse/PageSpeed Insights and at least one narrow mobile viewport before merging changes. Search ranking depends on external indexing and relevance; metadata improvements do not guarantee rankings.

## Architecture and technical notes

The homepage includes an architecture explorer and two technical notes. Keep diagrams aligned with implementation; publish performance figures only when reproducible. The feedback section intentionally avoids fabricated testimonials; add client comments only with permission.

## Adding a project

1. Add a card to `index.html` inside the right group (`Featured work` or `More projects & experiments`) and set `data-category` to any of `fullstack`, `ai`, `data` (space-separated) so the filter buttons work.
2. For a case study, copy an existing file in `projects/`, update its title, description, canonical URL and Open Graph tags, and add the URL to `sitemap.xml`.
3. Run `python3 scripts/check_site.py`.

## Content policy

Only publish results you can back up. Case studies describe scope and design; add accuracy, throughput or business figures only when they come from a reproducible benchmark, and never publish testimonials, client logos or conversion numbers that are not real. Use dummy data in screenshots of anything financial or confidential.

## Deploying

Push to `main`; Netlify publishes the repository root. Check pull requests in a Netlify deploy preview before merging, especially after changing `_headers`.
