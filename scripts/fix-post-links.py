#!/usr/bin/env python3
"""Repoint inter-post links at the source files instead of at hardcoded URLs.

A hardcoded /2026/09/22/slug breaks the moment the URL scheme changes — which is
exactly what just happened, and onBrokenLinks: 'throw' caught all four. A
relative link to the .mdx resolves through Docusaurus to whatever URL the target
currently has, so this class of breakage cannot recur.

Strict: aborts if any of the old URLs survive, so a silent no-op is impossible.
"""
import glob
import sys

MAP = {
    "/2026/06/30/carnot-compression-research": "./2026-06-30-carnot-compression-research.mdx",
    "/2026/07/30/carnot-gpu-rans": "./2026-07-30-carnot-gpu-rans.mdx",
    "/2026/09/22/claimaudit-three-ceilings-no-buyer":
        "./2026-09-22-claimaudit-three-ceilings-no-buyer.mdx",
}

touched, replaced = 0, 0
for path in sorted(glob.glob("blog/*.mdx")):
    src = open(path).read()
    new = src
    for old, rep in MAP.items():
        n = new.count("(%s)" % old)
        if n:
            new = new.replace("(%s)" % old, "(%s)" % rep)
            replaced += n
    if new != src:
        open(path, "w").write(new)
        print("  fixed %s" % path)
        touched += 1

print("  %d link(s) in %d file(s)" % (replaced, touched))

# Branch on the result: refuse to continue if a dated link survives anywhere.
leftover = []
for path in sorted(glob.glob("blog/*.mdx")):
    for old in MAP:
        if "(%s)" % old in open(path).read():
            leftover.append((path, old))
if leftover:
    print("ABORT — dated links still present: %s" % leftover, file=sys.stderr)
    sys.exit(1)
print("  verified: no post links to a dated URL any more")
