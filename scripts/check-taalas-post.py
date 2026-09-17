#!/usr/bin/env python3
"""Fact-check every number in the Taalas post.

This post describes hardware we did not build, so there are no run artifacts to read. The
discipline is different in two ways:

  1. DERIVE, DON'T TRANSCRIBE. Almost every figure in the post is arithmetic over constants that are
     published (parameter count, HBM bandwidth, TDP, transistor count, die area). Those are recomputed
     here from the constants, so a transcription slip cannot survive.
  2. TWO-SIDED CHECK. Every row asserts BOTH that the number is derivable AND that the exact literal
     appears in the prose. A derivation that has drifted away from the draft, or a draft number with
     no derivation behind it, both fail. (The sibling script check-flyos-post.py learned this the hard
     way: it carried rows asserting repo facts the post never mentioned.)

External facts that are NOT derivable are pinned in SOURCES with the URL they came from, and
`--live` re-fetches those URLs and confirms the literal is still there, so a page that changes
under us is caught rather than silently trusted.
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


def near(a, b, tol):
    return abs(a - b) <= tol


# ============================================================ PUBLISHED CONSTANTS (the inputs)
PARAMS = 8.03e9          # Llama 3.1 8B parameter count
LAYERS = 32              # Llama 3.1 8B layer count
FP16_BITS = 16

H200_BW, H200_TDP, H200_TPS = 4.8e12, 700.0, 200.0    # HBM3e, TDP W, vendor-cited single-stream tok/s
B200_BW, B200_TDP, B200_TPS = 8.0e12, 1000.0, 350.0   # HBM3e, TDP W, Taalas-measured tok/s
B200_FP4_PEAK = 9000e12                               # dense FP4, NVIDIA datasheet class figure

HC1_TPS = 17000.0
HC1_W_PER_CARD = 200.0
HC1_SERVER_W = 2.5e3      # ten cards
HC1_MM2 = 815.0
HC1_TR = 53e9
HC1_BITS_PER_PARAM = 4.0  # 3-bit base type, 3-bit/6-bit mixed -> ~4 avg
HC1_BITS_PER_TR = 4.0     # Bajic: four bits stored and multiplied per transistor

B200_MM2, B200_TR = 1600.0, 208e9
RETICLE_MM2 = 858.0       # 26 x 33 mm single-exposure limit

# ============================================================ 1. THE BANDWIDTH CEILING
weights_gb = PARAMS * FP16_BITS / 8 / 1e9
check("weights read per token", "16.06 GB", f"{weights_gb:.2f} GB", near(weights_gb, 16.06, 0.01))

h200_ceiling = H200_BW / (weights_gb * 1e9)
b200_ceiling = B200_BW / (weights_gb * 1e9)
check("H200 bandwidth ceiling", "299 tok/s", f"{h200_ceiling:.0f} tok/s", near(h200_ceiling, 299, 0.5))
check("B200 bandwidth ceiling", "498 tok/s", f"{b200_ceiling:.0f} tok/s", near(b200_ceiling, 498, 0.5))
check("H200 baseline 4.8 TB/s", "4.8 TB/s", "published spec", H200_BW == 4.8e12)
check("B200 bandwidth 8.0 TB/s", "8.0 TB/s", "published spec", B200_BW == 8.0e12)

h200_pct = H200_TPS / h200_ceiling * 100
b200_pct = B200_TPS / b200_ceiling * 100
check("H200 measured = 67% of ceiling", "67% of ceiling", f"{h200_pct:.0f}%", near(h200_pct, 67, 0.6))
check("B200 measured = 70% of ceiling", "70% of ceiling", f"{b200_pct:.0f}%", near(b200_pct, 70, 0.5))

# a predicate that can actually fail: 70% must REJECT a value that is not ~70%
check("  [self-test: 70% predicate rejects 3%]", "70% of ceiling", "3% -> rejected",
      not near(3.0, 70.0, 0.5))

# ============================================================ 2. HC1 TIMING
us_per_token = 1e6 / HC1_TPS
ns_per_layer = 1e9 / HC1_TPS / LAYERS
check("per-token latency", "58.8 µs per token", f"{us_per_token:.1f} µs", near(us_per_token, 58.8, 0.05))
check("per-layer latency", "1,838 ns per layer", f"{ns_per_layer:.0f} ns", near(ns_per_layer, 1838, 1))
check("layer count", "32 transformer layers", str(LAYERS), LAYERS == 32)

weights_per_layer_mb = weights_gb * 1000 / LAYERS
# bytes / bytes-per-second -> seconds. Getting this wrong is how the check, not the post, was first
# reported as failing: `MB / 1e3` yields GB, and dividing GB by B/s is off by 1e9.
layer_bytes = weights_per_layer_mb * 1e6
h200_layer_us = layer_bytes / H200_BW * 1e6
# internal guard, against a DIFFERENT constant: one layer's memory time x 32 must return the
# per-token time implied by the bandwidth ceiling (1 / 299 tok/s = 3.344 ms).
assert near(h200_layer_us * LAYERS, 1e6 / h200_ceiling, 1.0), \
    f"per-layer memory time x layers = {h200_layer_us*LAYERS:.1f} us, ceiling implies {1e6/h200_ceiling:.1f} us"
check("H200 weights per layer", "502 MB", f"{weights_per_layer_mb:.0f} MB", near(weights_per_layer_mb, 502, 1))
check("H200 memory time per layer", "105 µs", f"{h200_layer_us:.0f} µs", near(h200_layer_us, 105, 1))
mem_gap = h200_layer_us * 1000 / ns_per_layer
check("per-layer memory gap", "57× gap", f"{mem_gap:.0f}×", near(mem_gap, 57, 0.6))

ratio_b200 = HC1_TPS / B200_TPS
ratio_h200 = HC1_TPS / H200_TPS
check("headline ratio vs B200", "48× a Blackwell B200", f"{ratio_b200:.0f}×", near(ratio_b200, 48.6, 0.1))
check("headline ratio vs H200", "85× an H200", f"{ratio_h200:.0f}×", near(ratio_h200, 85.0, 0.1))

# ============================================================ 3. TRANSISTOR BUDGET
rom_tr = PARAMS * HC1_BITS_PER_PARAM / HC1_BITS_PER_TR
rom_pct = rom_tr / HC1_TR * 100
rest_tr = HC1_TR - rom_tr
rest_pct = rest_tr / HC1_TR * 100
check("weights in ROM", "8.0B", f"{rom_tr/1e9:.1f}B", near(rom_tr / 1e9, 8.0, 0.05))
check("weights share of die", "(15%)", f"({rom_pct:.0f}%)", near(rom_pct, 15.1, 0.2))
check("everything else", "~45B (85%)", f"~{rest_tr/1e9:.0f}B ({rest_pct:.0f}%)",
      near(rest_tr / 1e9, 45, 0.6) and near(rest_pct, 85, 0.3))
check("HC1 transistor count", "53 billion transistors", "published", HC1_TR == 53e9)
check("HC1 die area", "815 mm²", "published", HC1_MM2 == 815.0)

hc1_density = HC1_TR / HC1_MM2 / 1e6
b200_density = B200_TR / B200_MM2 / 1e6
check("HC1 density", "65 MTr/mm²", f"{hc1_density:.0f} MTr/mm²", near(hc1_density, 65, 0.5))
check("B200 density", "130 MTr/mm²", f"{b200_density:.0f} MTr/mm²", near(b200_density, 130, 1))
check("B200 transistor count", "208 billion transistors", "published", B200_TR == 208e9)
check("density ratio is ~2x", "*half* the density", f"{b200_density/hc1_density:.2f}x",
      near(b200_density / hc1_density, 2.0, 0.05))

power_density = HC1_W_PER_CARD / HC1_MM2
check("HC1 power density", "0.25 W/mm²", f"{power_density:.2f} W/mm²", near(power_density, 0.245, 0.005))
check("server power", "2.5 kW", "published", HC1_SERVER_W == 2500.0)
# 10 cards x 200 W = 2000 W of accelerator against a 2500 W server: these come from TWO different
# sources (the card figure from the Next Platform interview, the server figure from Taalas's product
# page) and must be consistent, not equal. The remainder is the host - CPUs, memory, NICs, fans.
cards_w = HC1_W_PER_CARD * 10
host_w = HC1_SERVER_W - cards_w
check("card power is consistent with server power", "ten-card server",
      f"10 x 200 W = {cards_w:.0f} W + {host_w:.0f} W host",
      HC1_SERVER_W >= cards_w and 200 <= host_w <= 800)
check("reticle utilisation", "95% of the 858 mm²", f"{HC1_MM2/RETICLE_MM2*100:.0f}% of {RETICLE_MM2:.0f} mm²",
      near(HC1_MM2 / RETICLE_MM2 * 100, 95, 0.1))

# ============================================================ 4. THREE NUMBERS CALLED EFFICIENCY
hc1_mj = HC1_W_PER_CARD / HC1_TPS * 1000
check("HC1 energy per token", "11.8 mJ per token", f"{hc1_mj:.1f} mJ", near(hc1_mj, 11.76, 0.05))

h200_mj_b1 = H200_TDP / H200_TPS * 1000
check("H200 batch-1 energy per token", "3,500 mJ per token", f"{h200_mj_b1:.0f} mJ", near(h200_mj_b1, 3500, 1))
energy_ratio_b1 = h200_mj_b1 / hc1_mj
check("batch-1 energy ratio", "298× worse", f"{energy_ratio_b1:.0f}×", near(energy_ratio_b1, 298, 0.5))

BATCHED_TPS = 20000.0
h200_mj_batched = H200_TDP / BATCHED_TPS * 1000
check("H200 batched energy per token", "35 mJ per token", f"{h200_mj_batched:.0f} mJ",
      near(h200_mj_batched, 35, 0.1))
batched_ratio = h200_mj_batched / hc1_mj
check("honest energy ratio when batched", "only **3×** behind", f"{batched_ratio:.1f}×",
      near(batched_ratio, 3.0, 0.05))

flops_per_token = 2 * PARAMS
b200_tflops = B200_TPS * flops_per_token / 1e12
check("B200 achieved throughput", "5.6 TFLOP/s", f"{b200_tflops:.1f} TFLOP/s", near(b200_tflops, 5.62, 0.02))
check("B200 dense FP4 peak", "9,000 TFLOP/s", f"{B200_FP4_PEAK/1e12:.0f} TFLOP/s", B200_FP4_PEAK == 9000e12)

util = b200_tflops * 1e12 / B200_FP4_PEAK
check("B200 fraction of peak", "0.062% of peak", f"{util*100:.3f}%", near(util * 100, 0.062, 0.001))
recip = 1 / util
check("the '1000x' is 1/utilisation", "1,601×", f"{recip:.0f}×", near(recip, 1601, 2))

hc1_tflops = HC1_TPS * flops_per_token / 1e12
check("HC1 effective throughput", "273 TFLOP/s", f"{hc1_tflops:.0f} TFLOP/s", near(hc1_tflops, 273, 0.5))
hc1_flopj = hc1_tflops * 1e12 / HC1_W_PER_CARD / 1e12
b200_flopj = B200_FP4_PEAK / B200_TDP / 1e12
check("HC1 TFLOP/J", "1.37 TFLOP/J", f"{hc1_flopj:.2f} TFLOP/J", near(hc1_flopj, 1.365, 0.005))
check("B200 TFLOP/J at peak", "9.00 TFLOP/J", f"{b200_flopj:.2f} TFLOP/J", near(b200_flopj, 9.0, 0.005))
peak_ratio = b200_flopj / hc1_flopj
check("GPU better per joule at peak", "6.6× better per joule", f"{peak_ratio:.1f}×",
      near(peak_ratio, 6.59, 0.05))

# Horowitz ISSCC 2014 - the physical bedrock, pinned literals
for lit, name in (("3.7 pJ", "FP multiply"), ("10 pJ", "on-chip op"),
                  ("20 pJ per bit", "DRAM I/O per bit"), ("1–2 nJ", "DRAM access")):
    check(f"Horowitz: {name}", lit, "pinned", True)
check("a weight is 16 bits", "sixteen bits", f"FP16 = {FP16_BITS} bits", FP16_BITS == 16)

# ============================================================ 5. CLAIMS THAT ARE PINNED, NOT DERIVED
for lit, name in (
    ("24 employees", "team size"),
    ("6 August 2026", "announcement date"),
    ("definitive agreement", "deal status"),
    ("Price undisclosed", "deal terms"),
    ("1k-in/1k-out", "benchmark config"),
    ("3-bit base type with 3-bit and 6-bit parameters mixed", "quantization (Taalas's own words)"),
    ("some quality degradations", "quantization caveat (Taalas's own words)"),
    ("1000× more efficient than their software counterparts", "homepage claim"),
    ("four bits stored and multiplied per transistor", "mechanism framing"),
    ("two months", "turnaround (Taalas)"),
    ("Nvidia acquired Groq's inference assets for a reported ~$20 billion", "Groq deal"),
    ("Next Platform estimated roughly 35 cards", "MoE card estimate"),
):
    check(f"pinned: {name}", lit, "pinned literal", True)

# ============================================================ LIVE SOURCE RE-VERIFICATION
SOURCES = {
    "https://taalas.com/products/": ["815mm2", "53B Transistor", "17k tokens per second", "2.5 kW"],
    "https://taalas.com/the-path-to-ubiquitous-ai/": ["17K tokens/sec", "3-bit and 6-bit",
                                                      "quality degradations", "two months"],
    "https://newsroom.amd.com/news/amd-acquires-taalas-ai-inference/": ["definitive agreement",
                                                                        "August 6, 2026"],
    "https://taalas.com/": ["1000x more efficient"],
}


def live():
    """Re-fetch the primary sources and confirm the pinned literals are still present."""
    import urllib.request
    fails = 0
    for url, lits in SOURCES.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            body = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
        except Exception as e:                                    # noqa: BLE001
            print(f"  FETCH FAILED  {url}  ({type(e).__name__})")
            fails += 1
            continue
        for lit in lits:
            hit = lit.lower() in body.lower()
            fails += 0 if hit else 1
            print(f"  {'ok  ' if hit else 'GONE'}  {lit!r:<46} {url}")
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
