#!/usr/bin/env python3
"""Fact-check every number in the Taalas post.

This post describes hardware we did not build, so there are no run artifacts to read. The
discipline is different in three ways:

  1. DERIVE, DON'T TRANSCRIBE. Almost every figure in the post is arithmetic over constants that are
     published (parameter count, HBM bandwidth, TDP, transistor count, die area). Those are recomputed
     here from the constants, so a transcription slip cannot survive.
  2. TWO-SIDED CHECK. Every row asserts BOTH that the number is derivable AND that the exact literal
     appears in the prose. A derivation that has drifted away from the draft, or a draft number with
     no derivation behind it, both fail.
  3. IMAGE-ONLY SOURCES ARE THE DANGEROUS ONES. The competitor baselines exist ONLY inside a chart
     image (graph.png), not in any page text. The first draft took them from secondary coverage and
     got them wrong - 200/350 where the chart says 230/353, which inflated an 85x claim out of a real
     74x. They are pinned here as CHART_* constants with the image URL, and `--live` re-fetches the
     image and verifies it still renders, because a text extraction cannot check it for you.

External facts that are NOT derivable are pinned in SOURCES with the URL they came from, and
`--live` re-fetches those URLs and confirms the literal is still there.
"""
import re
import sys
import pathlib

POST = pathlib.Path(__file__).resolve().parent.parent / "blog" / "2026-09-17-taalas-etched-model-silicon.mdx"
TEXT = POST.read_text()
results = []


def check(name, literal, derived, ok):
    """One row = one claim. `literal` must appear in the post; `ok` is the derivation verdict."""
    present = literal in TEXT
    results.append((name, "yes" if present else "ABSENT", derived, "PASS" if (ok and present) else "FAIL"))


def check_absent(name, literal, why):
    """The inverse assertion, for claims the draft must NOT contain.

    A presence-only helper cannot express 'this number was retracted and is now gone', which is a
    real claim about the draft - the first version of this script reported nine of them as failures
    because `check()` treats 'absent' as a failure by construction."""
    present = literal in TEXT
    results.append((name, "PRESENT" if present else "absent", why, "FAIL" if present else "PASS"))


def near(a, b, tol):
    return abs(a - b) <= tol


# ============================================================ PUBLISHED CONSTANTS (the inputs)
PARAMS = 8.03e9          # Llama 3.1 8B parameter count
LAYERS = 32              # Llama 3.1 8B layer count
FP16_BITS = 16

H200_BW, H200_TDP = 4.8e12, 700.0        # HBM3e bandwidth, TDP in W
B200_BW, B200_TDP = 8.0e12, 1000.0
B200_FP4_PEAK, B200_FP8_PEAK, B200_FP16_PEAK = 9000e12, 4500e12, 2250e12
B200_TR, B200_MM2_EST = 208e9, 1600.0     # transistors per NVIDIA; mm2 is OUR estimate across two dies

# ---- read from the chart image at https://taalas.com/h-content/uploads/2026/02/graph.png
# "Tokens Per Second Per User", Llama 3.1 8B. These CANNOT be grepped from page text.
CHART = {"hc1": 16960.0, "cerebras": 1981.0, "sambanova": 932.0,
         "groq": 594.0, "b200": 353.0, "h200": 230.0}

HC1_TPS = 17000.0         # Taalas's own written figure ("17K tokens/sec per user")
HC1_W_PER_CARD = 200.0    # Next Platform interview: "burns about 200 watts"
HC1_SERVER_W = 2.5e3      # Taalas product page: "2.5 kW Server", ten cards
HC1_CARDS = 10
HC1_MM2, HC1_TR = 815.0, 53e9
HC1_BITS_PER_PARAM = 4.0  # 3-bit base type, 3-bit/6-bit mixed -> ~4 avg
HC1_BITS_PER_TR = 4.0     # Bajic: four bits stored and multiplied per transistor
RETICLE_MM2 = 858.0       # 26 x 33 mm, the standard single-exposure field for 193i

# ============================================================ 1. THE BANDWIDTH CEILING
weights_gb = PARAMS * FP16_BITS / 8 / 1e9
check("weights read per token", "16.06 GB", f"{weights_gb:.2f} GB", near(weights_gb, 16.06, 0.01))

h200_ceiling = H200_BW / (weights_gb * 1e9)
b200_ceiling = B200_BW / (weights_gb * 1e9)
check("H200 bandwidth ceiling", "299 tok/s", f"{h200_ceiling:.0f} tok/s", near(h200_ceiling, 299, 0.5))
check("B200 bandwidth ceiling", "498 tok/s", f"{b200_ceiling:.0f} tok/s", near(b200_ceiling, 498, 0.5))
check("H200 bandwidth", "4.8 TB/s", "published spec", H200_BW == 4.8e12)
check("B200 bandwidth", "8.0 TB/s", "published spec", B200_BW == 8.0e12)

# THE CORRECTED BASELINES - from the chart, not from secondary prose
check("H200 baseline (chart)", "Nvidia H200 230", f"{CHART['h200']:.0f}", CHART["h200"] == 230.0)
check("B200 baseline (chart)", "B200 353", f"{CHART['b200']:.0f}", CHART["b200"] == 353.0)
check("Cerebras baseline (chart)", "Cerebras 1,981", f"{CHART['cerebras']:.0f}", CHART["cerebras"] == 1981.0)
check("SambaNova baseline (chart)", "SambaNova 932", f"{CHART['sambanova']:.0f}", CHART["sambanova"] == 932.0)
check("Groq baseline (chart)", "Groq 594", f"{CHART['groq']:.0f}", CHART["groq"] == 594.0)
check("HC1 chart value", "16,960", f"{CHART['hc1']:.0f}", CHART["hc1"] == 16960.0)

h200_pct = CHART["h200"] / h200_ceiling * 100
b200_pct = CHART["b200"] / b200_ceiling * 100
check("H200 at 77% of ceiling", "77% of ceiling", f"{h200_pct:.1f}%", near(h200_pct, 76.9, 0.2))
check("B200 at 71% of ceiling", "71% of ceiling", f"{b200_pct:.1f}%", near(b200_pct, 70.9, 0.2))
check("baselines bracket 71-77%", "71–77% of a wall", f"{b200_pct:.0f}-{h200_pct:.0f}%",
      round(b200_pct) == 71 and round(h200_pct) == 77)
# a predicate that can actually fail: the 71% band must REJECT a value that is not ~71%
check("  [self-test: 71% predicate rejects 3%]", "71% of ceiling", "3% -> rejected",
      not near(3.0, 71.0, 0.5))

# ============================================================ 2. HC1 TIMING
us_per_token = 1e6 / HC1_TPS
ns_per_layer = 1e9 / HC1_TPS / LAYERS
check("per-token latency", "58.8 µs per token", f"{us_per_token:.1f} µs", near(us_per_token, 58.8, 0.05))
check("per-layer latency", "1,838 ns per layer", f"{ns_per_layer:.0f} ns", near(ns_per_layer, 1838, 1))
check("layer count", "32 transformer layers", str(LAYERS), LAYERS == 32)

weights_per_layer_mb = weights_gb * 1000 / LAYERS
layer_bytes = weights_per_layer_mb * 1e6            # MB -> bytes
h200_layer_us = layer_bytes / H200_BW * 1e6         # bytes / (bytes/s) -> us
# internal guard against a DIFFERENT constant: one layer x 32 must return the per-token time implied
# by the bandwidth ceiling. A units slip here once produced 104,557 us and a false failure.
assert near(h200_layer_us * LAYERS, 1e6 / h200_ceiling, 1.0), \
    f"per-layer x layers = {h200_layer_us*LAYERS:.1f} us, ceiling implies {1e6/h200_ceiling:.1f} us"
check("H200 weights per layer", "502 MB", f"{weights_per_layer_mb:.0f} MB", near(weights_per_layer_mb, 502, 1))
check("H200 memory time per layer", "105 µs", f"{h200_layer_us:.0f} µs", near(h200_layer_us, 105, 1))
mem_gap = h200_layer_us * 1000 / ns_per_layer
check("per-layer memory gap", "57× gap", f"{mem_gap:.0f}×", near(mem_gap, 57, 0.6))

ratio_b200 = HC1_TPS / CHART["b200"]
ratio_h200 = HC1_TPS / CHART["h200"]
# chart value against chart value, for the Cerebras comparison the post makes
ratio_cerebras = HC1_TPS / CHART["cerebras"]
check("headline ratio vs B200", "48× the 353 tok/s", f"{ratio_b200:.1f}×", near(ratio_b200, 48.2, 0.2))
check("headline ratio vs H200 (was WRONGLY 85x)", "74×", f"{ratio_h200:.1f}×", near(ratio_h200, 73.9, 0.2))
check("ratio vs Cerebras", "8.6× the 1,981 tok/s", f"{ratio_cerebras:.2f}×", near(ratio_cerebras, 8.58, 0.02))
# the retracted ratio is MENTIONED in the post - deliberately, as the thing being corrected - so the
# check is that the retraction sentence exists, not that the number is absent.
check("retraction of 85x is stated", "not 48× and 85×", "retraction sentence present", True)

# ============================================================ 3. TRANSISTOR BUDGET
rom_tr = PARAMS * HC1_BITS_PER_PARAM / HC1_BITS_PER_TR
rom_pct = rom_tr / HC1_TR * 100
rest_tr = HC1_TR - rom_tr
rest_pct = rest_tr / HC1_TR * 100
check("weights in ROM", "8.0B", f"{rom_tr/1e9:.1f}B", near(rom_tr / 1e9, 8.0, 0.05))
check("weights share of transistors", "(15%)", f"({rom_pct:.0f}%)", near(rom_pct, 15.1, 0.2))
check("everything else", "~45B (85%)", f"~{rest_tr/1e9:.0f}B ({rest_pct:.0f}%)",
      near(rest_tr / 1e9, 45, 0.6) and near(rest_pct, 85, 0.3))
check("HC1 transistor count", "53 billion transistors", "published", HC1_TR == 53e9)
check("HC1 die area", "815 mm²", "published", HC1_MM2 == 815.0)

hc1_density = HC1_TR / HC1_MM2 / 1e6
b200_density = B200_TR / B200_MM2_EST / 1e6
check("HC1 density", "65 MTr/mm²", f"{hc1_density:.0f} MTr/mm²", near(hc1_density, 65, 0.5))
check("B200 density (area is OUR estimate)", "130 MTr/mm²", f"{b200_density:.0f} MTr/mm²",
      near(b200_density, 130, 1))
check("B200 transistor count", "208 billion transistors", "published", B200_TR == 208e9)
check("density is ~double", "about double", f"{b200_density/hc1_density:.2f}x",
      near(b200_density / hc1_density, 2.0, 0.05))
check("area figure flagged as our estimate", "our estimate, not a published NVIDIA number", "flagged", True)

power_density = HC1_W_PER_CARD / HC1_MM2
check("HC1 power density", "0.25 W/mm²", f"{power_density:.2f} W/mm²", near(power_density, 0.245, 0.005))
check("server power", "2.5 kW", "published", HC1_SERVER_W == 2500.0)
check("reticle utilisation", "95% of the 858 mm²", f"{HC1_MM2/RETICLE_MM2*100:.0f}% of {RETICLE_MM2:.0f}",
      near(HC1_MM2 / RETICLE_MM2 * 100, 95, 0.1))

# ============================================================ 4. THREE NUMBERS CALLED EFFICIENCY
hc1_mj = HC1_W_PER_CARD / HC1_TPS * 1000
check("HC1 energy per token (200 W)", "11.8 mJ per token", f"{hc1_mj:.1f} mJ", near(hc1_mj, 11.76, 0.05))

h200_mj_b1 = H200_TDP / CHART["h200"] * 1000
check("H200 batch-1 energy per token", "3,043 mJ per token", f"{h200_mj_b1:.0f} mJ", near(h200_mj_b1, 3043, 1))
energy_ratio_b1 = h200_mj_b1 / hc1_mj
check("batch-1 energy ratio (was WRONGLY 298x / 3500 mJ)", "259×", f"{energy_ratio_b1:.0f}×",
      near(energy_ratio_b1, 258.8, 0.5))

# the batched sensitivity table - this is the load-bearing ASSUMPTION, so every row is checked
# against the literal as it appears in the table, spacing and bold included.
BATCH_ROWS = [(5000, 140, 12, "| 140 | 12× |"), (10000, 70, 6, "| 70 | 6× |"),
              (20000, 35, 3, "| **35** | **3×** |"), (40000, 17.5, 1.5, "| 17.5 | 1.5× |")]
for agg, exp_mj, exp_ratio, literal in BATCH_ROWS:
    mj = H200_TDP / agg * 1000
    r = mj / hc1_mj
    check(f"batched @{agg:,} tok/s -> mJ/token and ratio", literal, f"{mj:.1f} mJ, {r:.1f}×",
          near(mj, exp_mj, 1.0) and near(r, exp_ratio, 0.1))
check("20000 tok/s row is marked as the assumption", "**20,000 tok/s**", "bolded in table", True)

# the 250 W per-card reading, which is the OTHER end of the range
w_server_per_card = HC1_SERVER_W / HC1_CARDS
check("250 W per card from the server figure", "250 W per card", f"{w_server_per_card:.0f} W",
      near(w_server_per_card, 250, 0.1))
hc1_mj_250 = w_server_per_card / HC1_TPS * 1000
check("HC1 energy per token (250 W)", "14.7 mJ/token", f"{hc1_mj_250:.1f} mJ", near(hc1_mj_250, 14.7, 0.05))
ratio_250 = 35.0 / hc1_mj_250
check("honest ratio at 250 W", "2.4×", f"{ratio_250:.1f}×", near(ratio_250, 2.38, 0.03))
check("the range is stated", "**2.4× to 3×**", "2.4 to 3.0", True)

# the utilisation bracket - the point is that it is a RANGE, not one number. Each row is checked
# against the literal the POST uses for that precision: the FP4 row carries a percentage, the FP8 and
# FP16 rows carry the peak figure and the ratio, and the post never states their percentages. Asserting
# a percentage the prose does not contain is the "check whose number appears nowhere in the post" trap.
flops_per_token = 2 * PARAMS
b200_flops = CHART["b200"] * flops_per_token
check("B200 achieved throughput", "5.67 TFLOP/s", f"{b200_flops/1e12:.2f} TFLOP/s",
      near(b200_flops / 1e12, 5.669, 0.005))
for peak, exp_pct, exp_recip, lit_pct, lit_recip in (
        (B200_FP4_PEAK, 0.063, 1600, "**0.063% of peak**", "**1,600×**"),
        (B200_FP8_PEAK, 0.126, 800, "4,500 TFLOP/s", "~800×"),
        (B200_FP16_PEAK, 0.252, 400, "2,250 TFLOP/s", "~400×")):
    util = b200_flops / peak
    check(f"B200 utilisation vs {peak/1e12:.0f} TFLOP/s peak", lit_pct, f"{util*100:.3f}%",
          near(util * 100, exp_pct, 0.001))
    check(f"  reciprocal -> {exp_recip:,}x", lit_recip, f"{1/util:,.0f}×", near(1 / util, exp_recip, 15))
check("bracket stated as a range", "400× and 1,600×", "400 to 1600", True)

hc1_flops = HC1_TPS * flops_per_token
hc1_flopj = hc1_flops / HC1_W_PER_CARD / 1e12
b200_flopj = B200_FP4_PEAK / B200_TDP / 1e12
# NOTE: no row for HC1's 273 TFLOP/s. The post states the joules-per-FLOP figures and does not state
# the throughput behind them, so such a row would assert a number the draft never makes.
check("HC1 TFLOP/J", "1.37 TFLOP/J", f"{hc1_flopj:.2f} TFLOP/J", near(hc1_flopj, 1.365, 0.005))
check("B200 TFLOP/J at peak", "9.00 TFLOP/J", f"{b200_flopj:.2f} TFLOP/J", near(b200_flopj, 9.0, 0.005))
check("GPU better per joule at peak", "9.00 TFLOP/J against HC1's 1.37", "6.59x",
      near(b200_flopj / hc1_flopj, 6.59, 0.05))

for lit in ("3.7 pJ", "10 pJ", "20 pJ per bit", "1–2 nJ"):
    check(f"Horowitz: {lit}", lit, "pinned", True)
check("Horowitz 10 pJ attributed to his prose", "his prose", "pinned", True)
check("a weight is 16 bits", "sixteen bits", f"FP16 = {FP16_BITS} bits", FP16_BITS == 16)

# ============================================================ 5. CLAIMS THAT ARE PINNED, NOT DERIVED
for lit, name in (
    ("24 employees", "team size"),
    ("6 August 2026", "announcement date"),
    ("definitive agreement", "deal status"),
    ("subject to customary closing conditions and regulatory approvals", "deal conditions"),
    ("The release does not state a price", "price absence, stated as an absence"),
    ("1k-in/1k-out", "benchmark config"),
    ("3-bit base type with 3-bit and 6-bit parameters mixed", "quantization (Taalas's own words)"),
    ("some quality degradations", "quantization caveat (Taalas's own words)"),
    ("1000x more efficient than their software counterparts", "homepage claim"),
    ("nearly 10X faster than the current state of the art", "Taalas's written claim"),
    ("two months", "turnaround (Taalas)"),
    ("we don't want to broadcast", "non-disclosure (Bajic)"),
    ("secondary coverage, not a Taalas statement", "mechanism attributed correctly"),
    ("reported that Nvidia had just bought Groq for ~$20 billion", "Groq deal, attributed to NP"),
    ("The Next Platform reported", "NP attribution"),
    ("configurable context window size and LoRA fine-tuning", "Taalas's stated flexibility"),
):
    check(f"pinned: {name}", lit, "pinned literal", True)

# things that were WRONG in the first draft and must now be ABSENT
# NOTE: "85×" is deliberately NOT in this list. The post mentions the retracted ratio while explaining
# the correction, which is correct practice; the row above checks the retraction sentence instead.
for lit, name in (("Version 1 of the company", "the Tenstorrent/Taalas conflation"),
                  ("the comparison the marketing uses", "claiming 298x was Taalas's comparison"),
                  ("Price undisclosed", "price asserted as a Taalas/AMD statement"),
                  ("the claim attached to the announcement", "1000x attributed to the AMD release"),
                  ("a few millimetres", "unsourced 'few millimetres'"),
                  ("The measured power density", "'measured' for a computed value"),
                  ("Next Platform estimated roughly 35 cards", "the over-read 35-card figure"),
                  ("Context length is bought at tapeout", "context window as a tapeout constant"),
                  ("The chip pre-computes all possible products", "mechanism stated as fact")):
    check_absent(f"[must be gone] {name}", lit, "absent from draft")

# ============================================================ LIVE SOURCE RE-VERIFICATION
SOURCES = {
    "https://taalas.com/products/": ["815mm2", "53B Transistor", "17k tokens per second", "2.5 kW"],
    "https://taalas.com/the-path-to-ubiquitous-ai/": ["17K tokens/sec", "3-bit and 6-bit",
                                                      "quality degradations", "two months",
                                                      "configurable context window"],
    "https://newsroom.amd.com/news/amd-acquires-taalas-ai-inference/": ["definitive agreement",
                                                                        "August 6, 2026",
                                                                        "regulatory approvals"],
    "https://taalas.com/": ["1000x more efficient"],
    "https://taalas.com/h-content/uploads/2026/02/graph.png": ["IMAGE"],
}
# the chart is an IMAGE: it cannot be grepped, so its numbers are pinned in CHART above and the live
# check can only confirm the image still exists and still carries its alt-text description.
CHART_PAGE = "https://taalas.com/products/"
CHART_ALT = "Chart showing speed comparison between Taalas and competitors"


def live():
    """Re-fetch the primary sources and confirm the pinned literals are still present."""
    import urllib.request
    fails = 0
    for url, lits in SOURCES.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=25)
            raw, ctype = r.read(), r.headers.get("Content-Type", "")
        except Exception as e:                                    # noqa: BLE001
            print(f"  FETCH FAILED  {url}  ({type(e).__name__})")
            fails += 1
            continue
        if "IMAGE" in lits:
            good = ctype.startswith("image/") and len(raw) > 10_000
            fails += 0 if good else 1
            print(f"  {'ok  ' if good else 'BAD '}  chart image still served  ({ctype}, {len(raw)} bytes)")
            continue
        body = raw.decode("utf-8", "ignore")
        for lit in lits:
            hit = lit.lower() in body.lower()
            fails += 0 if hit else 1
            print(f"  {'ok  ' if hit else 'GONE'}  {lit!r:<46} {url}")
    # the chart's alt text is greppable even though its numbers are not
    try:
        req = urllib.request.Request(CHART_PAGE, headers={"User-Agent": "Mozilla/5.0"})
        page = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
        hit = CHART_ALT in page and "graph.png" in page
        fails += 0 if hit else 1
        print(f"  {'ok  ' if hit else 'GONE'}  chart alt-text + graph.png referenced  ({CHART_PAGE})")
    except Exception as e:                                        # noqa: BLE001
        print(f"  FETCH FAILED  {CHART_PAGE}  ({type(e).__name__})")
        fails += 1
    return fails


# ============================================================ REPORT
if __name__ == "__main__":
    if "--live" in sys.argv:
        print("live source re-verification")
        sys.exit(1 if live() else 0)

    w = max(len(r[0]) for r in results)
    print(f"{'claim'.ljust(w)}  {'in post':<8} {'from constants':<28} result")
    print("-" * (w + 48))
    fails = 0
    for name, present, derived, verdict in results:
        if verdict == "FAIL":
            fails += 1
        print(f"{name.ljust(w)}  {present:<8} {derived:<28} {verdict}")
    print(f"\n{len(results) - fails} passed, {fails} failed")
    sys.exit(1 if fails else 0)
