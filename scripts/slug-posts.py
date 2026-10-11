#!/usr/bin/env python3
"""Give each dated post an explicit slug, so its URL stops carrying the date.

Why this and not a config option: Docusaurus v3's blog plugin has no `permalink`
(the build rejects it), `routeBasePath` cannot move because the blog IS the
homepage, and a `YYYY-MM-DD-name.mdx` filename makes the plugin expand the date
into the slug — blogUtils.js parseBlogFileName builds `/<date>/<name>`.

So the supported lever is the front-matter `slug` field, one line per post. The
dated FILENAMES stay: they sort the folder chronologically and the date still
renders on the page from front matter. Strict — aborts if a post has no `date:`
line, and skips any post that already carries a slug.
"""
import glob
import os
import re
import sys

changed = 0
for path in sorted(glob.glob("blog/*.mdx")):
    base = os.path.basename(path)[:-4]
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", base)
    if not m:
        print("  skipped (no date prefix): %s" % path)
        continue
    _date, name = m.groups()

    src = open(path).read()
    if re.search(r"^slug:", src, re.M):
        print("  already has a slug: %s" % path)
        continue

    new, n = re.subn(r"^(date: .*)$", r"\1\nslug: /blog/%s" % name,
                     src, count=1, flags=re.M)
    if n != 1:
        print("ABORT — no date: line in %s" % path, file=sys.stderr)
        sys.exit(1)

    open(path, "w").write(new)
    print("  %-58s -> /blog/%s" % (path, name))
    changed += 1

print("  %d post(s) updated" % changed)

# Verify by reading the files back rather than trusting the writes.
bad = []
for path in sorted(glob.glob("blog/*.mdx")):
    head = open(path).read().split("---")[1] if "---" in open(path).read() else ""
    if not re.search(r"^slug: /blog/", head, re.M):
        bad.append(path)
if bad:
    print("ABORT — these posts still have no slug: %s" % bad, file=sys.stderr)
    sys.exit(1)
print("  verified: every dated post now carries a slug")
