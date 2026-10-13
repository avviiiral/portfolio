# Aviral Goyal — Portfolio

Static portfolio site for Aviral Goyal (full-stack development, AI/ML, data analytics).

**Live site:** https://aviral-goyal.netlify.app/

There is no build step: plain HTML, CSS and a little vanilla JavaScript, deployed on Netlify.

## What's in this repo

| Path | Purpose |
|---|---|
| `index.html` | Single-page homepage (about, skills, services, FAQ, projects, contact form) |
| `projects/*.html` | Case-study pages linked from the project cards |
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

The same script runs in GitHub Actions on every push and pull request (`.github/workflows/site-checks.yml`). It needs only Python 3.

## Adding a project

1. Add a card to `index.html` inside the right group (`Featured work` or `More projects & experiments`) and set `data-category` to any of `fullstack`, `ai`, `data` (space-separated) so the filter buttons work.
2. For a case study, copy an existing file in `projects/`, update its title, description, canonical URL and Open Graph tags, and add the URL to `sitemap.xml`.
3. Run `python3 scripts/check_site.py`.

## Content policy

Only publish results you can back up. Case studies describe scope and design; add accuracy, throughput or business figures only when they come from a reproducible benchmark, and never publish testimonials, client logos or conversion numbers that are not real. Use dummy data in screenshots of anything financial or confidential.

## Deploying

Push to `main`; Netlify publishes the repository root. Check pull requests in a Netlify deploy preview before merging, especially after changing `_headers`.
