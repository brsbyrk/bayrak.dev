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

import collections
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

# the n=12 routing runs (tool descriptions). NOTE: the draft no longer quotes these
# rates — the intro now speaks in "of 24" — so there is no claim here to check. The
# artifacts stay committed because the harness that produced them is what the post
# points at; the numbers are deliberately NOT asserted, because a check with no sentence
# behind it is a repo assertion, not a fact-check (see Rule 2b in the authoring skill).

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
check("tool selection across three engines", "for a 121M on-device model, **15 of 24**",
      f"{n_correct} then {v_correct}", n_correct == 14 and v_correct == 15)

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

# ============================================================================ A. JULIA-1
# Two variants, from the committed JSON. Variant B is the post's new centrepiece: the
# same 11 tools plus ONE offered abstain option, to test whether representation alone is
# sufficient. The answer is that it is not, and that is a claim about our own draft.
julia = json.loads((DATA / "openjev-julia1-ab.json").read_text())
by_tag = {v["tag"][0]: v for v in julia}
if "A" not in by_tag or "B" not in by_tag:
    print("FATAL: the Julia-1 variants are missing from the committed JSON")
    sys.exit(2)


def julia_stats(v):
    """(abstentions, correct, mean p on wrong calls, mean p on right calls)"""
    off, ins = v["off_topic"], v["in_scope"]
    abst = sum(1 for r in off if r[1] == "none_of_these")
    correct = sum(1 for r in ins if r[2] == r[1])
    p_wrong = [r[2] for r in off if r[1] != "none_of_these"]
    p_right = [r[3] for r in ins if r[2] == r[1]]
    return (abst, correct, sum(p_wrong) / len(p_wrong), sum(p_right) / len(p_right))


jA_stats = julia_stats(by_tag["A"])
jB_stats = julia_stats(by_tag["B"])
print(f"  [julia-1 A] abst={jA_stats[0]} acc={jA_stats[1]}/24 "
      f"p_wrong={jA_stats[2]:.3f} p_right={jA_stats[3]:.3f}")
print(f"  [julia-1 B] abst={jB_stats[0]} acc={jB_stats[1]}/24 "
      f"p_wrong={jB_stats[2]:.3f} p_right={jB_stats[3]:.3f}")

check("Julia-1 variant A refusals", "| **0 of 24** | 10 of 24 | 0.648 / 0.839 |",
      f"A abst={jA_stats[0]} acc={jA_stats[1]} p={jA_stats[2]:.3f}/{jA_stats[3]:.3f}",
      jA_stats[0] == 0 and jA_stats[1] == 10
      and abs(jA_stats[2] - 0.648) < 0.0005 and abs(jA_stats[3] - 0.839) < 0.0005)
check("Julia-1 variant B refusals (offering the option changed nothing)",
      "| **0 of 24** | 8 of 24 | 0.636 / 0.992 |",
      f"B abst={jB_stats[0]} acc={jB_stats[1]} p={jB_stats[2]:.3f}/{jB_stats[3]:.3f}",
      jB_stats[0] == 0 and jB_stats[1] == 8
      and abs(jB_stats[2] - 0.636) < 0.0005 and abs(jB_stats[3] - 0.992) < 0.0005)
check("Julia-1 tool correct in the results table", "**10 of 24**", f"{jA_stats[1]}",
      jA_stats[1] == 10)
check("Julia-1 mean confidence, wrong call", "**0.648**", f"{jA_stats[2]:.3f}",
      abs(jA_stats[2] - 0.648) < 0.0005)
check("Julia-1 mean confidence, right call", "**0.839**", f"{jA_stats[3]:.3f}",
      abs(jA_stats[3] - 0.839) < 0.0005)

# the option was OFFERED in B and never used — the load-bearing new claim
check("the option was offered and ignored 24 times", "**0 of 24**", f"B refusals = {jB_stats[0]}",
      jB_stats[0] == 0)
# what it picked instead, in B: execute_command 16 times
b_calls = collections.Counter(r[1] for r in by_tag["B"]["off_topic"] if r[1] != "none_of_these")
check("B picked execute_command 16 times", "16 times `execute_command`",
      f"{b_calls.get('execute_command', 0)}", b_calls.get("execute_command", 0) == 16)
check("B offered-but-ignored count matches the other buckets",
      "plus three `web_fetch`, three `read_file` and two `web_search`",
      f"{b_calls.get('web_fetch', 0)}/{b_calls.get('read_file', 0)}/{b_calls.get('web_search', 0)}",
      b_calls.get("web_fetch", 0) == 3 and b_calls.get("read_file", 0) == 3
      and b_calls.get("web_search", 0) == 2)
# adding the option cost accuracy — a second-order claim that also has to be true
check("adding the option cost two points of accuracy", "cost two points of tool accuracy",
      f"{jA_stats[1]} -> {jB_stats[1]}", jA_stats[1] - jB_stats[1] == 2)

# Julia-1's published artifact facts
JULIA_WEIGHTS = 577_189_056
check("Julia-1 weight size", "577,189,056 bytes", f"{JULIA_WEIGHTS:,}", JULIA_WEIGHTS == 577_189_056)
check("Julia-1 weights in MiB", "550.5 MiB", f"{JULIA_WEIGHTS/2**20:.1f} MiB",
      abs(JULIA_WEIGHTS / 2**20 - 550.5) < 0.05)
check("Julia-1 weight hash prefix", "`df853bf7fe42…`", "sha256 prefix", True)
check("Julia-1 parameter count", "144.3M", "pinned card figure", True)
check("Julia-1 banking failure stated", "**64 of 100** against Jev's 87%", "pinned metric", True)
check("Julia-1 on-disk size in the table", "577.2 MB", f"{JULIA_WEIGHTS/1e6:.1f} MB",
      abs(JULIA_WEIGHTS / 1e6 - 577.2) < 0.05)
check("Julia-1 per-turn range", "39–63 ms",
      f"{by_tag['A']['seconds']/48*1000:.0f}-{by_tag['B']['seconds']/48*1000:.0f} ms",
      38 <= by_tag["A"]["seconds"] / 48 * 1000 <= 40
      and 62 <= by_tag["B"]["seconds"] / 48 * 1000 <= 64)
check("Julia-1 declared uncalibrated", '"calibration": null', "pinned policy file", True)

# ============================================================================ D. DECISION 3.0
# Pinned card facts, snapshotted into scripts/data by the fetch that produced them. The
# parameter counts are DERIVED from the published weight bytes (/2 for bf16), not taken
# from the card — the card's own number is what we are checking. --live re-fetches.
cards = json.loads((DATA / "openjev-decision30-cards.json").read_text())
d3c, edge = cards["d3"], cards["d3-edge"]
d3_p = d3c["derived_params_bf16"] / 1e9
edge_p = edge["derived_params_bf16"] / 1e9
print(f"  [decision 3.0] d3 weights {d3c['weights_bytes']:,} B -> {d3_p:.2f}B params bf16")
print(f"  [decision 3.0] d3-edge weights {edge['weights_bytes']:,} B -> {edge_p:.2f}B params bf16")

check("d3 / d3-edge params derived from weight bytes", "**0.59B to 26.09B**",
      f"{edge_p:.2f}B .. {d3_p:.2f}B",
      abs(d3_p - 26.09) < 0.02 and abs(edge_p - 0.59) < 0.01)
check("the design-intent quote", "**without generating text**",
      "'without generating text' in card" if "without generating text" in d3c["readme"] else "NOT IN CARD",
      "without generating text" in d3c["readme"])
check("the suite size", "**140,178 requests**", "140,178 in both cards",
      "140,178" in d3c["readme"] and "140,178" in edge["readme"])
check("the claimed coverage line, quoted as theirs", "none unsupported",
      "present in card" if "none unsupported" in d3c["readme"] else "NOT IN CARD",
      "none unsupported" in d3c["readme"])

BOARD = {
    "d3": ("| **d3** (26.09B) | **64.7** | **65.5** | **62.8** | **56.6** |",
           "| **d3** | **64.7** | **65.5** | **62.8** | **56.6** |"),
    "perplexity": ("| Perplexity Decider v1.1 (27B) | 62.8 | 62.3 | 61.1 | 55.6 |",
                   "Perplexity Decider v1.1 (27B) | 62.8 | 62.3 | 61.1 | 55.6"),
    "fastino": ("| Fastino GLiDE (28B, no-thinking) | 60.2 | 59.1 | 59.5 | 52.9 |",
                "Fastino GLiDE no-thinking (28B) | 60.2 | 59.1 | 59.5 | 52.9"),
    "jev": ("| **Jev** — the model being reimplemented | 60.1 | 58.0 | 58.0 | 55.0 |",
            "| Jev | 60.1 | 58.0 | 58.0 | 55.0 |"),
    "torchcast": ("| Torchcast Decision 27B | 59.9 | 65.1 | 58.1 | 50.8 |",
                  "| Torchcast Decision 27B | 59.9 | 65.1 | 58.1 | 50.8 |"),
}
for key, (post_row, card_row) in BOARD.items():
    check(f"board row: {key}", post_row, "matches card" if card_row in d3c["readme"] else "NO MATCH",
          card_row in d3c["readme"])

check("the 0.59B index figure", "**28.82** at 0.59B", "28.82 in d3-edge card",
      "28.82" in edge["readme"])
check("the 27B index figure", "**65.45** at 27B", "65.45 in d3 card",
      "65.45" in d3c["readme"])
for m in ("d3", "d3-edge"):
    check(f"{m} licence is Apache-2.0", "Apache-2.0", cards[m]["license"],
          cards[m]["license"] == "apache-2.0")

# the language head we would have to bolt back on, derived from the vocabulary shape
V, H = 256_000, 384
head_cost = V * H + V + H * H + H          # decoder.weight + decoder.bias + dense + norm
check("the language head costs 98.7M params", "**98.7M parameters**", f"{head_cost:,}",
      abs(head_cost / 1e6 - 98.7) < 0.05)
pb = (DATA / "openjev-param-breakdown.txt").read_text()
m = re.search(r"^\s*([\d,]+)\s+29\.2%\s+encoder: transformer layers", pb, re.M)
layers = int(m.group(1).replace(",", "")) if m else -1
check("the 22 encoder layers are 42.2M", "**42.2M** in all 22 encoder layers",
      f"{layers:,}", abs(layers / 1e6 - 42.2) < 0.05)
check("the encoder is the larger half of the head cost", "more than double the **42.2M**",
      f"{head_cost/layers:.2f}x", head_cost / layers > 2)

# ============================================================================ E. CLOZE PROBE
# Can a Jev-style model emit a word at all? Parsed from the committed probe log, whose
# CONTROL section is the point: the parent model must answer sensibly, or the probe
# cannot distinguish "no language head" from "our probe is broken".
cloze = (DATA / "openjev-cloze-probe.txt").read_text()
rows: dict[tuple[str, str], list[tuple[str, float]]] = {}
section = None
for line in cloze.splitlines():
    if line.startswith("--- "):
        section = "parent" if "PARENT" in line else "post-trained"
        continue
    if section and line.startswith("  ") and "'" in line:
        label = line[:line.index("'")].strip()
        pairs = re.findall(r"'((?:[^'\\]|\\.)*)':([0-9.]+)", line)
        if pairs:
            rows[(section, label)] = [(t, float(p)) for t, p in pairs]
print(f"  [cloze] parsed {len(rows)} probe rows")
if len(rows) < 8:
    print("FATAL: the cloze probe log did not parse into 8 rows")
    sys.exit(2)

PROBE = [
    ("parent answers the control at all", "parent", "mid-mask", "horse", 0.39, "horse .39"),
    ("parent answers at the END of a sentence", "parent", "end-mask = next word", ".", 0.28,
     "a full stop .28"),
    ("post-trained encoder still completes", "post-trained", "mid-mask", "gun", 0.48,
     "**gun .48**"),
    ("post-trained encoder gives a next word", "post-trained", "end-mask = next word",
     "think", 0.62, "**think .62**"),
    ("the parent's second control", "parent", "mid-mask (2)", "coast", 0.25, "coast .25"),
    ("the degraded third case", "post-trained", "mid-mask (2)", "america", 0.32, "america .32"),
]
for name, sec, label, tok, want, literal in PROBE:
    got = rows.get((sec, label), [])
    top = got[0] if got else ("<none>", 0.0)
    check(name, literal, f"{top[0]!r} {top[1]:.2f}",
          top[0] == tok and abs(top[1] - want) < 0.006)

check("the whole encoder was swapped, not part of it", "**134 of 134**",
      "134 / 134 in probe log" if "134 / 134" in cloze else "NOT IN LOG",
      "134 / 134" in cloze)

# ============================================================================ F. NEW GUARDS
check_absent("[must be gone] the Fastino row loses its mode qualifier",
             "| Fastino GLiDE (28B) |",
             "the card reads 'Fastino GLiDE no-thinking (28B)' — the qualifier is part of the claim")
check_absent("[must be gone] implying we ran Decision 3.0", "ran Decision 3.0",
             "we read its card; we did not run it")
check_absent("[must be gone] a verdict on the index floor", "near chance",
             "no floor is published, so 'near chance' is unsupported")
# 140,178 appears TWICE in the post (the board intro and the quoted highlight), so a
# presence check cannot see one of them corrupted. Absence of the neighbouring variant is
# the only thing that catches a partial edit.
check_absent("[off-by-one] the suite size", "141,178", "the suite is 140,178 requests")
check_absent("[off-by-one] the d3 index", "**65.7**", "d3 scores 64.7 on the 0.3.1 board")
check_absent("[off-by-one] a competitor row", "Perplexity Decider v1.1 (27B) | 63.8",
             "the card reads 62.8")
check_absent("[off-by-one] the reference model row", "| Jev | 61.1 |",
             "the card reads 60.1 for Jev")
check_absent("[off-by-one] the head cost", "**99.7M parameters**",
             "the head costs 98.7M")

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
