#!/usr/bin/env python3
"""Post-build verification for the OpenJEV post.  Run: python3 scripts/verify-openjev-build.py

Rule 3: a successful build is necessary but not sufficient. This checks the RENDERED HTML,
which is where a post that compiles can still be wrong.

Every matcher here is written the way the failures taught us, because a false negative
sends you editing a page that is already correct:

  * minified HTML drops attribute quotes (`href=/path`), so match paths, not quoted attrs;
  * Docusaurus emits `<title data-rh=true>`, so every tag matcher is `<tag[^>]*>`;
  * a double-quoted attribute value can contain an apostrophe, so capture the opening
    quote and match to the same character -- this post's description says "TypeSafe's";
  * never match a bare word a framework class also contains -- searching for `truncate`
    matched Docusaurus's own `text--truncate` navbar class and reported a leak that did
    not exist. Match the delivered string.

Lives in the repo rather than /tmp on purpose: /tmp is reaped, and this must survive to be
re-run after every edit to a living post.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POST = ROOT / "blog" / "2026-09-24-openjev-nine-reimplementations-refusal-test.mdx"

# The path is DERIVED the way the blog plugin derives it: routeBasePath + the post's slug.
# Both halves are read, because reading only one was wrong twice -- once when the URL still
# carried a date, and once when routeBasePath moved to /blog while the slug stopped carrying
# the /blog/ prefix. A hardcoded path here reports on a page that no longer holds the article.
_cfg = (ROOT / "docusaurus.config.js").read_text()
_m = re.search(r"^slug:\s*(\S+)\s*$", POST.read_text(), re.M)
_r = re.search(r"routeBasePath:\s*['\"]([^'\"]+)['\"]", _cfg)
if not _m or not _r:
    print("ABORT — cannot derive the page path: need both a `slug:` and a blog routeBasePath")
    sys.exit(2)
_slug = _m.group(1).strip("/")
_base = _r.group(1).strip("/")
PAGE = ROOT / "build" / _base / _slug / "index.html"
print(f"routeBasePath='/{_base}'  slug='/{_slug}'  ->  {PAGE.relative_to(ROOT)}")

if not PAGE.exists():
    print(f"no built page at {PAGE}\nrun `npm run build` first")
    sys.exit(2)

html = PAGE.read_text()
fails: list[str] = []


def ok(cond: bool, what: str, detail: str = "") -> None:
    print(f"  {'ok  ' if cond else 'FAIL'}  {what}" + (f"   {detail}" if detail else ""))
    if not cond:
        fails.append(what)


print(f"page: {PAGE}  ({len(html):,} bytes)")

# --- the page must be the article, not a redirect stub ----------------------------
ok(len(html) > 10_000, "page is the article, not a redirect stub", f"{len(html):,} bytes")
ok("http-equiv" not in html[:600].lower(), "page is not a client-side redirect")

# --- head -------------------------------------------------------------------------
ok(re.search(r"<title[^>]*>[^<]*OpenJEV", html) is not None, "rendered title mentions OpenJEV")
ok("Option That Did Not Help" in html, "title text survived")
desc = re.search(r'<meta[^>]*name=description[^>]*content=(?P<q>["\'])(?P<v>.{40,}?)(?P=q)', html)
ok(desc is not None, "description meta present", f"{len(desc.group('v'))} chars" if desc else "")
ok(desc is not None and "falsified" in desc.group("v"), "description carries the argument")
ok(desc is not None and "leaderboard" in desc.group("v"), "description carries the 10-11 update")
ok(desc is not None and "conformal" in desc.group("v"), "description carries the 10-18 update")
ok("og:title" in html, "open graph title present")

# --- the measured core ------------------------------------------------------------
ok("3 of 24" in html and "16 of 24" in html, "the headline refusal counts rendered")
ok("216.8×" in html, "the derived ratio rendered")
ok("36.7" in html and "75,557,149" in html, "the derived sizes rendered")
ok(html.count("<table") >= 8, "tables rendered as <table>", f"{html.count('<table')} tables")

# --- the 2026-10-11 update --------------------------------------------------------
for s in ("A Month Later, the Field Has a Leaderboard", "The Line to Interrogate",
          "Can These Models Emit a Word at All?", "Decision 3.0", "140,178",
          "Perplexity Decider", "Fastino GLiDE", "Torchcast", "without generating text",
          "98.7M parameters", "134 of 134", "trust_remote_code", "Updated 2026-10-11"):
    ok(s in html, f"update rendered: {s}")

# --- the 2026-10-18 update --------------------------------------------------------
for s in ("The Conformal Set That Abstains on Everything", "conformal set",
          "22 of 24", "38 of 38", "0.030", "Updated 2026-10-18"):
    ok(s in html, f"conformal update rendered: {s}")

# --- the marker must not leak, and the index must list the post --------------------
ok("{/* truncate */}" not in html, "the truncate marker is not emitted as text")
home = (ROOT / "build" / "index.html")
ok(home.exists() and "openjev" in home.read_text().lower(),
   "post title appears on the homepage")
listing = (ROOT / "build" / "blog" / "index.html")
ok(listing.exists() and "openjev-nine-reimplementations-refusal-test" in listing.read_text(),
   "post is linked from /blog/")
sitemap = ROOT / "build" / "sitemap.xml"
ok(sitemap.exists() and "openjev-nine-reimplementations-refusal-test" in sitemap.read_text(),
   "post is in the sitemap")

print()
if fails:
    print(f"{len(fails)} check(s) failed: {fails}")
    sys.exit(1)
print("all post-build checks passed")
