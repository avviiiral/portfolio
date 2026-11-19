#!/usr/bin/env python3
"""Offline sanity checks for this static portfolio. Standard library only.

Run from the repository root:  python3 scripts/check_site.py

Checks (exit code 1 if any fail):
  * every page has <title>, a meta description and an <h1>; indexable pages have a canonical URL
  * HTML tags are balanced and ids are unique
  * every <img> has an alt attribute; target="_blank" links include rel="noopener"
  * internal links and #anchors point at files / ids that exist
  * sitemap.xml lists every indexable page and nothing that does not exist
  * local files referenced from <meta og:image>/<twitter:image> exist
  * JSON-LD script blocks parse as JSON and include a schema context
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://aviral-goyal.netlify.app"
GTM_CONTAINER = "GTM-TT9Q7MHF"
VOID = {"meta", "link", "img", "input", "br", "hr", "source", "area", "base", "col", "embed", "param", "track", "wbr"}
SKIP_DIRS = {".git", "node_modules", ".github"}

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems = [], []
        self.ids, self.links, self.metas, self.imgs_missing_alt = [], [], {}, 0
        self.title, self._in_title, self.h1 = "", False, 0
        self.canonical, self.blank_without_noopener = None, []
        self._ld, self._in_ld = [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
            self._ld.append("")
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.metas[key] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "img":
            if "alt" not in a:
                self.imgs_missing_alt += 1
            for attr in ("src", "srcset"):
                value = a.get(attr, "")
                if value and not value.startswith(("http://", "https://", "data:")):
                    candidate = value.split(",")[0].strip().split()[0]
                    if not (ROOT / candidate.lstrip("/")).is_file():
                        self.problems.append(f"image {attr} points at missing file {candidate}")
        elif tag == "a" and a.get("href") is not None:
            self.links.append(a["href"])
            if a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
                self.blank_without_noopener.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "script" and self._in_ld:
            self._in_ld = False
            self._check_ld(self._ld[-1])
        if tag == "title":
            self._in_title = False
        if tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            top = self.stack[-1] if self.stack else None
            self.problems.append(f"unexpected </{tag}> at line {self.getpos()[0]} (open: {top})")
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self._in_ld:
            self._ld[-1] += data
        if self._in_title:
            self.title += data

    def _check_ld(self, raw):
        try:
            doc = json.loads(raw)
        except ValueError as exc:
            self.problems.append(f"invalid JSON-LD: {exc}")
            return
        if not isinstance(doc, (dict, list)) or (isinstance(doc, dict) and "@context" not in doc):
            self.problems.append("JSON-LD block is missing @context")

def html_files():
    """Return site pages, excluding service-owned verification token documents."""
    pages = []
    for path in ROOT.rglob("*.html"):
        if set(path.relative_to(ROOT).parts) & SKIP_DIRS:
            continue
        # Google Search Console verification files contain a plain token, not a
        # site page. Keep the token deployed, but do not validate or index it.
        try:
            if path.read_text(encoding="utf-8").lstrip().startswith("google-site-verification:"):
                continue
        except OSError as exc:
            print(f"Could not read {path}: {exc}", file=sys.stderr)
            continue
        pages.append(path)
    return sorted(pages)

def url_for(path: Path) -> str:
    """Return the public canonical URL under Netlify Pretty URLs."""
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return f"{SITE}/{rel[:-len('index.html')]}"
    if rel.endswith(".html"):
        return f"{SITE}/{rel[:-5]}"
    return f"{SITE}/{rel}"

def resolve_internal(href: str, page: Path):
    """Return (target_file, fragment) for an internal href, or None for external/ignored links."""
    if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None
    u = urlparse(href)
    if u.scheme in ("http", "https"):
        if u.netloc != urlparse(SITE).netloc:
            return None
        path = u.path
    elif u.scheme or u.netloc:
        return None
    else:
        path = u.path
    if path == "":
        target = page
    elif path.startswith("/"):
        target = ROOT / path.lstrip("/")
    else:
        target = (page.parent / path)
    if target.is_dir() or path.endswith("/") or path == "/":
        target = target / "index.html"
    elif not target.exists() and not target.suffix:
        # Netlify Pretty URLs expose .html files without their suffix.
        html_candidate = target.with_suffix(".html")
        index_candidate = target / "index.html"
        if html_candidate.is_file():
            target = html_candidate
        elif index_candidate.is_file():
            target = index_candidate
    return target, u.fragment

def main() -> int:
    errors = []
    pages = {p: Page() for p in html_files()}
    ids_by_page = {}
    # Keep the homepage a compact navigation hub and ensure the Netlify contact form has one canonical location.
    homepage = ROOT / "index.html"
    if homepage.is_file():
        home_source = homepage.read_text(encoding="utf-8")
        home_sections = re.findall(r'<section\b[^>]*\bid="([^"]+)"', home_source)
        expected_home_sections = {"hero", "home-pathways", "featured-work", "home-writing", "home-contact"}
        if set(home_sections) != expected_home_sections:
            errors.append(f"index.html: expected compact homepage sections {sorted(expected_home_sections)}, found {sorted(set(home_sections))}")
        if not re.search(r'<h1\b[^>]*>\s*Aviral Goyal\s*</h1>', home_source):
            errors.append("index.html: primary heading should identify Aviral Goyal")
        if re.search(r'<form\b', home_source, re.I):
            errors.append("index.html: move the long enquiry form to /contact/ to keep the homepage concise")
    contact_page = ROOT / "contact" / "index.html"
    contact_forms = []
    for page_path in pages:
        page_source = page_path.read_text(encoding="utf-8")
        if re.search(r'<form\b[^>]*\bname=["\']contact["\']', page_source, re.I):
            contact_forms.append(page_path.relative_to(ROOT).as_posix())
    if contact_forms != ["contact/index.html"]:
        errors.append(f"expected one Netlify contact form in contact/index.html, found {contact_forms}")

    # Keep theme behavior consistent across every project and engineering-note detail page.
    detail_pages = [
        "projects/bgliin-ai.html",
        "projects/personal-wealth-monitoring.html",
        "projects/ai-data-analyst-agent.html",
        "articles/multi-camera-monitoring.html",
        "articles/auditable-portfolio-calculations.html",
    ]
    for rel in detail_pages:
        detail_path = ROOT / rel
        if not detail_path.is_file():
            errors.append(f"{rel}: missing detail page")
            continue
        detail_source = detail_path.read_text(encoding="utf-8")
        for marker in (
            'localStorage.getItem("theme") === "dark"',
            'id="modeToggle"',
            'body.classList.toggle("dark")',
            'name="theme-color" content="#f5f3ee"',
        ):
            if marker not in detail_source:
                errors.append(f"{rel}: missing shared theme behavior marker {marker}")

    case_css_path = ROOT / "case-study.css"
    if not case_css_path.is_file():
        errors.append("case-study.css not found")
    else:
        case_css = case_css_path.read_text(encoding="utf-8")
        for marker in ("body.dark", "--case-bg:#121714", ".mode-toggle"):
            if marker not in case_css:
                errors.append(f"case-study.css: missing shared theme rule {marker}")

    # SVG architecture diagrams must fit the responsive card frame instead of being cropped.
    home_css_path = ROOT / "home-index.css"
    projects_css_path = ROOT / "editorial.css"
    if not home_css_path.is_file() or "object-fit: contain;" not in home_css_path.read_text(encoding="utf-8") or "position: absolute;" not in home_css_path.read_text(encoding="utf-8"):
        errors.append("home-index.css: featured project diagrams must use a positioned contain-fit image")
    if not projects_css_path.is_file() or "object-fit:contain;" not in projects_css_path.read_text(encoding="utf-8") or "position:absolute;" not in projects_css_path.read_text(encoding="utf-8"):
        errors.append("editorial.css: catalogue project diagrams must use a positioned contain-fit image")

    # Synthetic project gallery must use the three local, self-contained preview assets.
    project_page = ROOT / "projects" / "index.html"
    if not project_page.is_file():
        errors.append("projects/index.html not found")
    else:
        project_source = project_page.read_text(encoding="utf-8")
        for marker in (
            'id="project-ui-previews"',
            'id="project-preview-dialog"',
            'class="project-gallery-open"',
            'data-caption=',
        ):
            if marker not in project_source:
                errors.append(f"projects/index.html: missing gallery marker {marker}")
        for preview in (
            "assets/previews/pwms-dashboard.svg",
            "assets/previews/bgliin-telemetry.svg",
            "assets/previews/ai-data-analyst.svg",
        ):
            if preview not in project_source:
                errors.append(f"projects/index.html: missing gallery image reference {preview}")
            elif not (ROOT / preview).is_file():
                errors.append(f"projects/index.html: missing gallery image file {preview}")

    # Layout regressions reported from the PR preview: image ratios, catalogue contrast and recruiter portrait sizing.
    gallery_css_path = ROOT / "project-gallery.css"
    if gallery_css_path.is_file():
        gallery_css = gallery_css_path.read_text(encoding="utf-8")
        for marker in (
            ".project-gallery-media {",
            "aspect-ratio: 16 / 9;",
            "height: auto !important;",
            "width: 100% !important;",
            "object-fit: contain;",
            "#project-catalogue .projects-subhead",
            "#project-catalogue .project-links > a.project-btn",
            "color: #17211a !important;",
            "background: #ffffff !important;",
            "body.dark #project-catalogue .project-links > a.project-btn",
        ):
            if marker not in gallery_css:
                errors.append(f"project-gallery.css: missing responsive/theme rule {marker}")
    else:
        errors.append("project-gallery.css: gallery stylesheet not found")

    project_source = (ROOT / "projects" / "index.html").read_text(encoding="utf-8") if (ROOT / "projects" / "index.html").is_file() else ""
    if 'href="/project-gallery.css?v=20261119-3"' not in project_source:
        errors.append("projects/index.html: gallery stylesheet cache-busting version is missing")
    if project_source.count('class="project-gallery-media"') != 3:
        errors.append("projects/index.html: all three gallery screenshots must use the fixed-ratio media wrapper")

    resume_source = (ROOT / "resume" / "index.html").read_text(encoding="utf-8") if (ROOT / "resume" / "index.html").is_file() else ""
    if 'href="/audience-pages.css?v=20261119-3"' not in resume_source:
        errors.append("resume/index.html: portrait stylesheet cache-busting version is missing")

    portrait_css_path = ROOT / "audience-pages.css"
    if portrait_css_path.is_file():
        portrait_css = portrait_css_path.read_text(encoding="utf-8")
        for marker in (
            ".audience-profile img",
            "width: 150px !important;",
            "height: 187.5px !important;",
            "width: 88px !important;",
            "height: 110px !important;",
        ):
            if marker not in portrait_css:
                errors.append(f"audience-pages.css: recruiter portrait ratio rule missing {marker}")
    else:
        errors.append("audience-pages.css not found")

    for rel in ("thank-you.html", "404.html"):
        utility = ROOT / rel
        if not utility.is_file():
            errors.append(f"{rel}: utility page not found")
            continue
        utility_source = utility.read_text(encoding="utf-8")
        for marker in (
            'localStorage.getItem("theme") === "dark"',
            'id="modeToggle"',
            'body.classList.toggle("dark")',
            'name="theme-color" content="#f5f3ee"',
        ):
            if marker not in utility_source:
                errors.append(f"{rel}: missing shared theme behavior marker {marker}")

    for path in ("project-gallery.css", "project-gallery.scss"):
        if not (ROOT / path).is_file():
            errors.append(f"{path}: gallery stylesheet not found")

    for p, parser in pages.items():
        source = p.read_text(encoding="utf-8")
        parser.feed(source)
        parser.close()
        rel = p.relative_to(ROOT).as_posix()
        gtm_script = f"https://www.googletagmanager.com/gtm.js?id={GTM_CONTAINER}"
        if source.count(gtm_script) != 1:
            errors.append(f"{rel}: expected exactly one Google tag script for {GTM_CONTAINER}")
        if "window.dataLayer = window.dataLayer || [];" not in source or "function gtag()" not in source:
            errors.append(f"{rel}: missing Google tag dataLayer initialization")
        if rel == "resume/index.html" and '"@type":"ProfilePage"' not in source:
            errors.append(f"{rel}: missing ProfilePage structured data")
        ids_by_page[p] = set(parser.ids)

    indexable = []
    for p, pg in pages.items():
        rel = p.relative_to(ROOT).as_posix()
        noindex = "noindex" in pg.metas.get("robots", "")
        if not pg.title.strip():
            errors.append(f"{rel}: missing <title>")
        description = pg.metas.get("description", "").strip()
        if not description and not noindex:
            errors.append(f"{rel}: missing meta description")
        elif description and not noindex and not (70 <= len(description) <= 180):
            errors.append(f"{rel}: meta description length {len(description)} is outside 70–180 characters")
        if not noindex:
            for social_key in ("og:title", "og:description", "og:url", "og:image", "twitter:card", "twitter:title", "twitter:description", "twitter:image"):
                if not pg.metas.get(social_key):
                    errors.append(f"{rel}: missing {social_key} metadata")
            if pg.metas.get("twitter:card") != "summary_large_image":
                errors.append(f"{rel}: twitter:card should be summary_large_image")
        if pg.h1 < 1 and rel not in ("thank-you.html", "404.html"):
            errors.append(f"{rel}: no <h1>")
        if pg.h1 > 1:
            errors.append(f"{rel}: {pg.h1} <h1> elements (expected 1)")
        if not noindex:
            indexable.append(p)
            if not pg.canonical:
                errors.append(f"{rel}: missing canonical link")
            elif pg.canonical.rstrip("/") != url_for(p).rstrip("/"):
                errors.append(f"{rel}: canonical {pg.canonical} does not match {url_for(p)}")
        errors += [f"{rel}: {m}" for m in pg.problems]
        if pg.stack:
            errors.append(f"{rel}: unclosed tags: {[t for t, _ in pg.stack]}")
        dup = sorted({i for i in pg.ids if pg.ids.count(i) > 1})
        if dup:
            errors.append(f"{rel}: duplicate ids {dup}")
        if pg.imgs_missing_alt:
            errors.append(f"{rel}: {pg.imgs_missing_alt} <img> without alt")
        for href in pg.blank_without_noopener:
            errors.append(f"{rel}: target=_blank without rel=noopener -> {href}")
        for key in ("og:image", "twitter:image"):
            val = pg.metas.get(key)
            if val and val.startswith(SITE):
                f = ROOT / urlparse(val).path.lstrip("/")
                if not f.is_file():
                    errors.append(f"{rel}: {key} points at missing file {val}")
        for href in pg.links:
            hit = resolve_internal(href, p)
            if hit is None:
                continue
            target, frag = hit
            if not target.exists():
                errors.append(f"{rel}: broken internal link {href}")
            elif frag and target.suffix == ".html":
                tid = ids_by_page.get(target)
                if tid is not None and frag not in tid:
                    errors.append(f"{rel}: link {href} -> missing #{frag} in {target.relative_to(ROOT)}")

    # sitemap <-> files
    sm = ROOT / "sitemap.xml"
    if sm.is_file():
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        listed = {e.text.strip() for e in ET.parse(sm).getroot().findall("s:url/s:loc", ns)}
        wanted = {url_for(p) for p in indexable}
        for missing in sorted(wanted - listed):
            errors.append(f"sitemap.xml: missing {missing}")
        for extra in sorted(listed - wanted):
            errors.append(f"sitemap.xml: lists {extra} but no indexable page matches")
    else:
        errors.append("sitemap.xml not found")

    # Crawler discovery and browser identity assets.
    robots = ROOT / "robots.txt"
    if not robots.is_file():
        errors.append("robots.txt not found")
    else:
        directives = {line.strip() for line in robots.read_text(encoding="utf-8").splitlines()}
        expected_sitemap = f"Sitemap: {SITE}/sitemap.xml"
        if expected_sitemap not in directives:
            errors.append(f"robots.txt: missing {expected_sitemap}")

    idx = ROOT / "index.html"
    favicon = ROOT / "favicon.svg"
    if not favicon.is_file():
        errors.append("favicon.svg not found")
    elif idx.is_file() and 'rel="icon" type="image/svg+xml" href="/favicon.svg"' not in idx.read_text(encoding="utf-8"):
        errors.append('index.html: missing SVG favicon link')

    # Legacy .html URLs should permanently redirect to their clean canonical paths.
    redirects_file = ROOT / "_redirects"
    required_redirects = {
        ("/index.html", "/", "301"),
        ("/projects/index.html", "/projects/", "301"),
        ("/services/index.html", "/services/", "301"),
        ("/resume/index.html", "/resume/", "301"),
        ("/articles/index.html", "/articles/", "301"),
        ("/contact/index.html", "/contact/", "301"),
        ("/projects/bgliin-ai.html", "/projects/bgliin-ai", "301"),
        ("/projects/personal-wealth-monitoring.html", "/projects/personal-wealth-monitoring", "301"),
        ("/projects/ai-data-analyst-agent.html", "/projects/ai-data-analyst-agent", "301"),
        ("/articles/multi-camera-monitoring.html", "/articles/multi-camera-monitoring", "301"),
        ("/articles/auditable-portfolio-calculations.html", "/articles/auditable-portfolio-calculations", "301"),
    }
    if not redirects_file.is_file():
        errors.append("_redirects not found")
    else:
        actual_redirects = set()
        for line in redirects_file.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0] and not parts[0].startswith("#"):
                actual_redirects.add((parts[0], parts[1], parts[2]))
        for source, target, code in sorted(required_redirects - actual_redirects):
            errors.append(f"_redirects: missing permanent redirect {source} -> {target} ({code})")

    # Sitemap URLs should be absolute HTTPS URLs on the configured site.
    if sm.is_file():
        for loc in listed:
            u = urlparse(loc)
            if u.scheme != "https" or u.netloc != urlparse(SITE).netloc:
                errors.append(f"sitemap.xml: unexpected URL {loc}")

    # local assets referenced from index.html
    idx = ROOT / "index.html"
    if idx.is_file():
        for ref in re.findall(r'(?:src|srcset|href)="([^"#?]+\.(?:jpg|jpeg|png|webp|pdf|svg))"', idx.read_text(encoding="utf-8")):
            if ref.startswith(("http://", "https://")):
                continue
            if not (ROOT / ref.lstrip("/")).is_file():
                errors.append(f"index.html: referenced file missing: {ref}")

    if errors:
        print(f"{len(errors)} problem(s) found:")
        for e in errors:
            print(" -", e)
        return 1
    print(f"OK: {len(pages)} page(s) checked, sitemap and internal links consistent.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
