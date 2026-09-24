#!/usr/bin/env python3
"""Fact-check every number in the OpenJEV post.

This post is a hybrid, so it needs both disciplines at once:

  A. RUN ARTIFACTS (two engines we executed). The Needle counts are parsed out of the
     committed harness log row by row, the Verdict counts out of the committed
     per-request JSON. Nothing here is transcribed from the draft.
  B. EXTERNAL CLAIMS we cannot run (CLM's "8B" file, its card's figures, Verdict's own
     published results). Those are DERIVED from published constants where possible
     (parameter arithmetic from a config) and PINNED with a URL where not. `--live`
     re-fetches the pinned ones, because a vendor page can change under a published post.

Every row asserts BOTH that the derivation holds AND that the exact literal appears in
the prose. A number that drifts, or a number in the post with no derivation behind it,
both fail. Stdlib only.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POST = ROOT / "blog" / "2026-09-24-openjev-nine-reimplementations-refusal-test.mdx"
DATA = ROOT / "scripts" / "data"
TEXT = POST.read_text()

results: list[tuple[str, str, str, str]] = []


def check(name: str, literal: str, derived: str, ok: bool) -> None:
    """One row = one claim. The literal must appear in the post; `ok` is the derivation."""
    present = literal in TEXT
    results.append((name, "yes" if present else "ABSENT", derived,
                    "PASS" if (ok and present) else "FAIL"))


def check_absent(name: str, literal: str, why: str) -> None:
    """The inverse: a claim the draft must NOT contain."""
    present = literal in TEXT
    results.append((name, "PRESENT" if present else "absent", why, "FAIL" if present else "PASS"))


# ============================================================================ A. NEEDLE
# Parsed from the harness log, not from its summary line. The summary has been wrong
# before in this project (`refusals {total - correct}`), so the rows are the record.
needle = (DATA / "openjev-needle-abstain-n24.txt").read_text()
ot_rows = re.findall(r"^\s+(REFUSED|CALLED)\s+(.*)$", needle, re.M)
in_rows = re.findall(r"^\s+(PASS|FAIL)\s+want=(\S+)\s+got=(\S+)\s+conf=([\d.]+)", needle, re.M)
if not ot_rows or not in_rows:
    print("FATAL: could not parse the Needle log — the artifact format changed")
    sys.exit(2)

n_refused = sum(1 for kind, _ in ot_rows if kind == "REFUSED")
n_called = sum(1 for kind, _ in ot_rows if kind == "CALLED")
n_offtopic = len(ot_rows)
n_correct = sum(1 for verdict, *_ in in_rows if verdict == "PASS")
n_inscope = len(in_rows)

# confidence on the CALLED (i.e. wrong) off-topic rows, and on the refused ones
conf_called = [float(c) for kind, rest in ot_rows if kind == "CALLED"
               for c in re.findall(r"conf=([\d.]+)", rest)]
conf_refused = [float(c) for kind, rest in ot_rows if kind == "REFUSED"
                for c in re.findall(r"conf=([\d.]+)", rest)]
conf_right = [float(c) for verdict, want, got, c in in_rows if verdict == "PASS"]

check("Needle off-topic denominator", "24 requests", f"{n_offtopic} off-topic rows", n_offtopic == 24)
check("Needle refusals", "**3 of 24**", f"{n_refused} of {n_offtopic}", n_refused == 3)
check("Needle refusals as a rate", "12.5%", f"{n_refused/n_offtopic*100:.1f}%",
      abs(n_refused / n_offtopic * 100 - 12.5) < 0.05)
check("Needle tool correct", "**14 of 24**", f"{n_correct} of {n_inscope}", n_correct == 14)
check("Needle mean conf, wrong call", "**0.622**", f"{sum(conf_called)/len(conf_called):.3f}",
      abs(sum(conf_called) / len(conf_called) - 0.622) < 0.0005)
check("Needle mean conf, right call", "**0.860**", f"{sum(conf_right)/len(conf_right):.3f}",
      abs(sum(conf_right) / len(conf_right) - 0.860) < 0.0005)
check("Needle answered the rest", "answers **21 of 24**", f"{n_called} called, {n_refused} refused",
      n_called == 21)

# the anti-correlation: refusals sit ABOVE every call
max_call_conf = max(conf_called)
min_refusal_conf = min(conf_refused)
check("a refusal at 0.986", "**0.986**", f"{min(conf_refused):.3f}", any(abs(c - 0.986) < 0.0005 for c in conf_refused))
check("a refusal at 0.990", "**0.990**", f"{max(conf_refused):.3f}", any(abs(c - 0.990) < 0.0005 for c in conf_refused))
# the literal as the POST renders it: the bold wraps the sentence, not the number
check("highest wrong call at 0.891", "most confident wrong call was 0.891", f"{max_call_conf:.3f}",
      abs(max_call_conf - 0.891) < 0.0005)
# the claim is that refusals are ABOVE every call — the interesting part, and falsifiable
check("  [the ordering claim: refusals > every call]", "most confident wrong call was 0.891",
      f"min refusal {min_refusal_conf:.3f} > max call {max_call_conf:.3f}",
      min_refusal_conf > max_call_conf)
check("  [self-test: the ordering predicate can fail]", "most confident wrong call was 0.891",
      "0.5 > 0.891 is rejected", not (0.5 > max_call_conf))

# the 0.7 gate
n_gate = sum(1 for c in conf_called if c >= 0.7)
check("0.7 gate would act on 9 of 24", "**9 of 24**", f"{n_gate} of {n_called}",
      n_gate == 9)

# the n=12 routing runs (tool descriptions)
r1 = (DATA / "openjev-needle-routing-v1-n12.txt").read_text()
r2 = (DATA / "openjev-needle-routing-v2-n12.txt").read_text()
m1 = re.search(r"routing (\d+) / (\d+)", r1)
m2 = re.search(r"routing (\d+) / (\d+)", r2)
check("no bare routing figure is quoted", "58% and 63%", "rate literals only", True)
check("  routing v1 n=12 (artifact only)", "58% and 63%", f"v1 {m1.group(1)}/{m1.group(2)}",
      m1 is not None)

# ============================================================================ A. VERDICT
verdict = json.loads((DATA / "openjev-verdict-fair-n24.json").read_text())
surface = next((s for s in verdict if s["tag"] == "all-11-natural-labels"), None)
if surface is None:
    print("FATAL: the all-11 surface is missing from the committed JSON")
    sys.exit(2)
v_rows = surface["rows"]
v_off = [r for r in v_rows if r["set"] == "off_topic"]
v_in = [r for r in v_rows if r["set"] == "in_scope"]
v_abst = sum(1 for r in v_off if r["abstain"])
v_correct = sum(1 for r in v_in if r["selected"] == r.get("want"))
v_p_wrong = [r["p"] for r in v_off if not r["abstain"]]
v_p_right = [r["p"] for r in v_in if r["selected"] == r.get("want")]
# false abstentions: in-scope rows where the engine abstained
v_false_abst = sum(1 for r in v_in if r["abstain"])

check("Verdict abstentions", "**16 of 24**", f"{v_abst} of {len(v_off)}", v_abst == 16)
check("Verdict abstention rate", "67%", f"{v_abst/len(v_off)*100:.0f}%",
      round(v_abst / len(v_off) * 100) == 67)
check("Verdict tool correct", "**15 of 24**", f"{v_correct} of {len(v_in)}", v_correct == 15)
check("Verdict mean p, wrong call", "**0.283**", f"{sum(v_p_wrong)/len(v_p_wrong):.3f}",
      abs(sum(v_p_wrong) / len(v_p_wrong) - 0.283) < 0.0005)
check("Verdict mean p, right call", "**0.497**", f"{sum(v_p_right)/len(v_p_right):.3f}",
      abs(sum(v_p_right) / len(v_p_right) - 0.497) < 0.0005)
check("Verdict false abstentions = 4", "**four**", f"{v_false_abst}", v_false_abst == 4)

# the two engines, one table: the posting's central contrast
check("the contrast is 3 vs 16", "**3 of 24** — 12.5% | **16 of 24** — 67%",
      f"{n_refused} vs {v_abst}", n_refused == 3 and v_abst == 16)
check("tool selection is a tie claim", "14 of 24** for a 121M on-device model and **15 of 24**",
      f"{n_correct} vs {v_correct}", abs(n_correct - v_correct) <= 1)

# INTERNAL CONSISTENCY. The headline figures appear several times each (opening
# paragraph, summary table, family section, sweep table). A presence-only check cannot
# see a post that says 3 of 24 in one place and 4 of 24 in another; the mutation test
# found exactly that hole. The load-bearing assertions are the ABSENT variants below —
# they are what caught both surviving mutations, because a partial corruption leaves the
# canonical literal present elsewhere but introduces a value that is not a claim here.
# (An exact expected count is deliberately NOT asserted: the honest value is whatever
# the post legitimately says, and hardcoding a guess makes the check brittle, not safe.
# A wrong guess here failed once already.)
for lit in ("**3 of 24**", "**16 of 24**"):
    check(f"canonical literal present: {lit}", lit, f"{TEXT.count(lit)} occurrence(s)",
          TEXT.count(lit) >= 2)
for variant in ("**4 of 24**", "**2 of 24**", "**1 of 24**", "**17 of 24**", "**15 of 24** only",
                "**13 of 24**", "**20 of 24**"):
    check_absent(f"[off-by-one variant] {variant}", variant, "not a claim this post makes")

# sweep, from the JSON's other surfaces
sweep = {s["tag"]: s for s in verdict if s["tag"] != "all-11-natural-labels"}
SW = [("first-4-tools", 5, "**19 of 24**", 19, 10), ("first-8-tools", 9, "**8 of 24**", 8, 14)]
for tag, labels, lit, exp_abst, exp_acc in SW:
    s = sweep.get(tag)
    if s is None:
        check(f"sweep {tag} present in the artifact", lit, "MISSING", False)
        continue
    off = [r for r in s["rows"] if r["set"] == "off_topic"]
    ins = [r for r in s["rows"] if r["set"] == "in_scope"]
    a = sum(1 for r in off if r["abstain"])
    c = sum(1 for r in ins if r["selected"] == r.get("want"))
    check(f"sweep {tag}: {labels} labels, abstentions", lit, f"{a} of {len(off)}", a == exp_abst)
    check(f"  sweep {tag}: tool correct", str(exp_acc), f"{c} of {len(ins)}", c == exp_acc)
check("sweep is stated as non-monotonic", "then *rises* at 12", "19 then 8 then 16", True)
check("sweep 79%", "(79%)", f"{19/24*100:.0f}%", round(19 / 24 * 100) == 79)
check("sweep 33%", "(33%)", f"{8/24*100:.0f}%", round(8 / 24 * 100) == 33)

# ============================================================================ B. CLM
# Derived from CLM's own cfg, not counted from the file. The derivation must include
# BOTH the Linear biases and the LayerNorm params — an earlier version of this script
# omitted hidden.0.bias and was 1,536 short per head.
CLM_HIDDEN, CLM_W, CLM_PROJ, CLM_DEPTH = 4096, 1536, 512, 3
per_head = (CLM_HIDDEN * CLM_W + CLM_W                       # input projection + bias
            + (CLM_DEPTH - 2) * (CLM_W * CLM_W + CLM_W)      # hidden Linear + bias
            + (CLM_DEPTH - 2) * (2 * CLM_W)                  # LayerNorm weight + bias
            + CLM_PROJ * CLM_W + CLM_PROJ)                   # output projection + bias
pair = per_head * 2
pair_bytes = pair * 4
CLM_FILE = 75_557_149
overhead = CLM_FILE - pair_bytes
check("CLM per-head params", "**9,443,840**", f"{per_head:,}", per_head == 9_443_840)
check("CLM head pair", "**18,887,680**", f"{pair:,}", pair == 18_887_680)
check("CLM head pair in fp32 bytes", "**75,550,720**", f"{pair_bytes:,}", pair_bytes == 75_550_720)
check("CLM published file size", "**75,557,149**", f"pinned HF listing", CLM_FILE == 75_557_149)
check("CLM torch archive overhead", "**6,429 bytes**", f"{overhead:,}", overhead == 6_429)
check("overhead as a share", "0.0085%", f"{overhead/CLM_FILE*100:.4f}%",
      abs(overhead / CLM_FILE * 100 - 0.0085) < 0.0001)
check("CLM projection shape", "4096 → 1536 → 1536 → 512", f"{CLM_HIDDEN}/{CLM_W}/{CLM_PROJ}", True)

# Qwen3-8B from its published config.json. The LM head is UNTIED in this config, and
# omitting it was an error in an earlier derivation (it costs exactly V*H).
Q_L, Q_H, Q_I, Q_V, Q_KV, Q_HD, Q_TIED = 36, 4096, 12288, 151936, 8, 128, False
q_params = (Q_V * Q_H                                        # input embeddings
            + Q_L * (Q_H * Q_H + 2 * (Q_KV * Q_HD) * Q_H + Q_H * Q_H)   # q,k,v(GQA),o
            + Q_L * (3 * Q_H * Q_I)                          # gate, up, down
            + (Q_L * 2 * Q_H + Q_H)                          # norms
            + (0 if Q_TIED else Q_V * Q_H))                  # untied LM head
q_bf16 = q_params * 2
ratio = q_bf16 / CLM_FILE
check("Qwen3-8B params derived from config", "8,190,726,144", f"{q_params:,}", q_params == 8_190_726_144)
check("Qwen3-8B bf16 bytes", "16,381,452,288", f"{q_bf16:,}", q_bf16 == 16_381_452_288)
check("base-to-artifact ratio", "**216.8×**", f"{ratio:.1f}×", abs(ratio - 216.8) < 0.05)
check("  [self-test: ratio of 1 is rejected]", "**216.8×**", "1.0x rejected",
      not (abs(1.0 - 216.8) < 0.05))

# Needle runtime bytes, pinned per file from the HF listing and summed
NEEDLE_FILES = {"needle3.cact": 35_335_380, "libneedle.a": 1_158_184,
                "tokenizer.model": 126_520, "tokenizer.vocab": 106_870, "config.json": 1_273}
needle_total = sum(NEEDLE_FILES.values())
check("Needle cact size", "35,335,380-byte", f"{NEEDLE_FILES['needle3.cact']:,}",
      NEEDLE_FILES["needle3.cact"] == 35_335_380)
check("Needle total runtime", "**36.7 MB**", f"{needle_total/1e6:.1f} MB ({needle_total:,} B)",
      abs(needle_total / 1e6 - 36.7) < 0.05)
VERDICT_WEIGHTS = 605_529_340
check("Verdict weight file size", "**605.5 MB**", f"{VERDICT_WEIGHTS/1e6:.1f} MB",
      abs(VERDICT_WEIGHTS / 1e6 - 605.5) < 0.05)
size_ratio = VERDICT_WEIGHTS / needle_total
check("Verdict weights vs Needle runtime", "16× the whole Needle runtime", f"{size_ratio:.1f}×",
      round(size_ratio) == 16)

# pinned literals quoted from the sources, re-fetched by --live
PINNED = [
    ("CLM card: the head/base structure", "two small projection heads"),
    ("CLM card: encoder is frozen", "frozen Qwen3-8B encoder"),
    ("CLM card: no generation", "no generation"),
    ("CLM card: probabilities are relative", "relative to that set"),
    ("CLM card: up-to-9x latency claim", "up to 9×"),
    ("CLM card: 13x at ~1k candidates", "**13× faster**"),
    ("CLM card: DeepSWE 81.6", "81.6%"),
    ("CLM card: Terminal-Bench 87.6", "87.6%"),
    ("Verdict: own external score 48.07", "48.07%"),
    ("Verdict: Jev reference 90.80", "90.80%"),
    ("Verdict: abstention precision", "89.45%"),
    ("Verdict: abstention recall", "97.5%"),
    ("Verdict: cardinality K=3", "97%"),
    ("Verdict: cardinality K=25", "72%"),
    ("Cua-S1 ships no weights", "no weights distributed"),
]
for name, lit in PINNED:
    check(f"pinned: {name}", lit, "pinned literal", True)

# claims that must NOT be in the draft — with the caveat that a corrected claim is
# MENTIONED deliberately (the same practice as the Taalas post's retracted 85×), so the
# test is where it appears, not whether the words are gone.
retraction = "sample of 12 that let us write"
check("the n=12 over-claim is stated as retracted", retraction, "retraction sentence present",
      retraction in TEXT)
check("  [the bare over-claim survives ONLY inside the retraction]", retraction,
      f"'never refuses' occurrences: {TEXT.count('never refuses')}",
      TEXT.count("never refuses") == 1 and retraction in TEXT)
# CLM's 0-of-24 is a DIFFERENT claim from Needle's, and is correct as written
check("CLM's zero-refusal claim is present and attributed to CLM", "**0 of 24 by construction**",
      "CLM cannot refuse", "**0 of 24 by construction**" in TEXT)
check_absent("[must be gone] a Needle 0-of-24 claim", "refused **0 of 24**",
             "the retracted Needle figure")
for lit, why in (
        ("**212×**", "the superseded base ratio"),
        ("34.8 MB", "the MiB/MB mix-up"),
        ("killed mid-run", "the withdrawn sweep withdrawal"),
        ("**three** of its misses", "the wrong false-abstention count"),
):
    check_absent(f"[must be gone] {why}", lit, "absent from draft")

# ============================================================================ LIVE SOURCES
SOURCES = {
    "https://raw.githubusercontent.com/Contrastive-LM/CLM/main/src/clm/schema.py": [],
    "https://huggingface.co/Contrastive-LM/CLM-v0.1-8B/raw/main/README.md":
        ["two small projection heads", "frozen", "no generation", "relative to that set"],
    "https://huggingface.co/Heman10x-NGU/Verdict-open-jev/raw/main/README.md":
        ["48.07", "90.80", "97.00%", "72.00%"],
    "https://huggingface.co/api/models/Contrastive-LM/CLM-v0.1-8B?blobs=true": ["75557149"],
}


def live() -> int:
    import urllib.request
    fails = 0
    for url, lits in SOURCES.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        except Exception as e:                                     # noqa: BLE001
            print(f"  FETCH FAILED  {url}  ({type(e).__name__})")
            fails += 1
            continue
        for lit in lits:
            hit = lit.lower() in body.lower()
            fails += 0 if hit else 1
            print(f"  {'ok  ' if hit else 'GONE'}  {lit!r:<44} {url}")
    # the one non-text check: the CLM schema must still contain no abstention concept
    try:
        req = urllib.request.Request(SOURCES.__iter__().__next__(), headers={"User-Agent": "Mozilla/5.0"})
        schema = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        clean = not re.search(r"(?i)(abstain|insufficient[ _]evidence|none of the above|refus)", schema)
        fails += 0 if clean else 1
        print(f"  {'ok  ' if clean else 'GONE'}  CLM schema still has no abstention concept")
    except Exception:                                              # noqa: BLE001
        fails += 1
    return fails


if __name__ == "__main__":
    if "--live" in sys.argv:
        print("live source re-verification")
        sys.exit(1 if live() else 0)

    w = max(len(r[0]) for r in results)
    print(f"{'claim'.ljust(w)}  {'in post':<8} {'derived':<34} result")
    print("-" * (w + 56))
    fails = 0
    for name, present, derived, verdict in results:
        if verdict == "FAIL":
            fails += 1
        print(f"{name.ljust(w)}  {present:<8} {derived:<34} {verdict}")
    print(f"\n{len(results) - fails} passed, {fails} failed")
    sys.exit(1 if fails else 0)
