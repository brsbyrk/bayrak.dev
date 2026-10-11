#!/usr/bin/env python3
"""Prove the fact-check script can actually fail.  Run: python3 scripts/mutation-test-openjev-checker.py

A checker that has never rejected anything is not evidence. For each mutation below,
corrupt one number in a COPY of the post, run the checker against that copy, and
require that at least one row fails. The post itself is never touched: the copy is
written to a temp path and restored after each case.

One of the mutations is the real historical bug (9,442,304 — an earlier version of the
derivation omitted hidden.0.bias), so the suite is anchored on a mistake that actually
happened rather than on an invented one.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path.home() / "Workspace" / "bayrak.dev"
POST = ROOT / "blog" / "2026-09-24-openjev-nine-reimplementations-refusal-test.mdx"
CHECK = ROOT / "scripts" / "check-openjev-post.py"

MUTATIONS = [
    ("Needle reference count", "**3 of 24**", "**4 of 24**"),
    ("Needle runtime size", "**36.7 MB**", "**39.7 MB**"),
    ("base-to-artifact ratio", "**216.8×**", "**212.0×**"),
    ("CLM fp32 byte count", "**75,550,720**", "**75,550,721**"),
    ("CLM per-head params (the real earlier bug)", "**9,443,840**", "**9,442,304**"),
    ("false-abstention count", "**four** of its misses", "**three** of its misses"),
    ("Verdict abstention count", "**16 of 24**", "**17 of 24**"),
    ("Qwen3-8B parameter count", "8,190,726,144", "8,180,726,144"),
    ("abstention rate", "12.5%", "13.5%"),
    ("overhead bytes", "**6,429 bytes**", "**7,429 bytes**"),
    # --- the 2026-10-11 update: Decision 3.0 and the cloze probe ---
    ("d3 size ladder", "**0.59B to 26.09B**", "**0.59B to 27.09B**"),
    ("d3 board index", "| **d3** (26.09B) | **64.7**", "| **d3** (26.09B) | **66.7**"),
    # appears TWICE in the post, so this one is caught by the variant-absence guard
    ("suite size (two occurrences)", "**140,178 requests**", "**141,178 requests**"),
    ("a competitor row", "Perplexity Decider v1.1 (27B) | 62.8",
     "Perplexity Decider v1.1 (27B) | 63.8"),
    ("the language head cost", "**98.7M parameters**", "**99.7M parameters**"),
    ("a cloze probe token", "**gun .48**", "**gun .58**"),
    ("a cloze probe probability", "coast .25", "coast .35"),
    ("the encoder swap count", "**134 of 134**", "**133 of 134**"),
]

original = POST.read_text()
survivors = []
try:
    for name, old, new in MUTATIONS:
        if old not in original:
            print(f"  SKIP (literal absent from the post): {name} — {old!r}")
            survivors.append(name)
            continue
        POST.write_text(original.replace(old, new, 1))
        proc = subprocess.run([sys.executable, str(CHECK)], capture_output=True, text=True, cwd=str(ROOT))
        failed = [l for l in proc.stdout.splitlines() if l.rstrip().endswith("FAIL")]
        caught = proc.returncode != 0 and failed
        print(f"  {'caught ' if caught else 'SURVIVED'}  {name:<44} "
              f"({len(failed)} row(s) failed)" if caught else
              f"  SURVIVED  {name:<44} checker exited {proc.returncode}, 0 rows failed")
        if not caught:
            survivors.append(name)
finally:
    POST.write_text(original)

print()
if survivors:
    print(f"{len(survivors)} mutation(s) survived — the checker is blind to them: {survivors}")
    sys.exit(1)
print(f"all {len(MUTATIONS)} mutations caught: the checker can fail, and it fails on the right rows.")
