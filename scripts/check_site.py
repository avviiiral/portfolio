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
    return sorted(p for p in ROOT.rglob("*.html") if not (set(p.relative_to(ROOT).parts) & SKIP_DIRS))

def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return SITE + "/" if rel == "index.html" else f"{SITE}/{rel}"

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
    return target, u.fragment

def main() -> int:
    errors = []
    pages = {p: Page() for p in html_files()}
    ids_by_page = {}
    for p, parser in pages.items():
        parser.feed(p.read_text(encoding="utf-8"))
        parser.close()
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
