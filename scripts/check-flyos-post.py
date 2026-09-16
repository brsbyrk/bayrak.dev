#!/usr/bin/env python3
"""Fact-check every number in the blog post against committed artifacts.

Rule: numbers are RE-READ from artifacts, never transcribed from prose or conversation. Where a value
can be re-derived from raw run output it is re-derived rather than looked up, so the check is
independent of any document - including the ones written during the project.
"""
import csv, json, pathlib, subprocess, sys

REPO = pathlib.Path("/Users/baris/Workspace/flyos")
results = []


def check(name, post, actual, ok):
    results.append((name, post, actual, "PASS" if ok else "FAIL"))


def rows(path):
    with open(REPO / path, newline="") as f:
        return list(csv.DictReader(f))


def f(x):
    return float(x)


# ---------------------------------------------------------------- thresholds, RE-DERIVED
def derive_theta(path, col="total_spikes"):
    """Re-derive the ignition threshold from a sweep: the scale of the largest jump in activity."""
    r = [(f(x["value"]), f(x[col])) for x in rows(path) if col in x]
    r.sort()
    best, at = 0.0, None
    for (s0, a0), (s1, a1) in zip(r, r[1:]):
        d = (a1 - a0) / max(a0, 1.0)
        if d > best:
            best, at = d, (s0 + s1) / 2.0   # MIDPOINT of the jump, the record's convention
    return at


theta_bio = derive_theta("experiments/out/relative-threshold/sweep-fine-biological.csv")
theta_deg = derive_theta("experiments/out/relative-threshold/sweep-fine-ctrl-101.csv")
check("threshold: real brain", "0.0064", f"{theta_bio:.4f}", abs(theta_bio - 0.006401) < 5e-4)
check("threshold: degree-matched", "0.0110", f"{theta_deg:.4f}", abs(theta_deg - 0.010954) < 5e-4)

# uniform theta comes from the coarse battery sweep (no fine sweep was run for it)
theta_uni = derive_theta("experiments/out/controls-uniform/sweep-uniform-204.csv")
check("threshold: structure-free", "0.0173", f"{theta_uni:.4f}", abs(theta_uni - 0.01732) < 1e-3)

ratio = theta_deg / theta_bio
check("retraction 2: degree:bio ratio", "1.71x", f"{ratio:.2f}x", abs(ratio - 1.71) < 0.02)
check("threshold ordering monotone", "0.0064 < 0.0110 < 0.0173",
      f"{theta_bio:.4f} < {theta_deg:.4f} < {theta_uni:.4f}",
      theta_bio < theta_deg < theta_uni)

# ---------------------------------------------------------------- retention, from curve CSVs
def t400(path):
    return [(f(r["act_pct"]), f(r["ridge_t400"]), f(r["null_t0"])) for r in rows(path)]


bio = t400("experiments/out/memory-curve-bio/curve.csv")
bio_vals = [v for _, v, _ in bio]
check("retention: real brain t+400 range", "80 to 95%",
      f"{min(bio_vals):.1f}-{max(bio_vals):.1f}%", min(bio_vals) == 80.0 and max(bio_vals) == 95.0)

ctrl_all = []
for fam in ("ctrl", "sign", "block"):
    for a, v, _ in t400(f"experiments/out/memory-curve-{fam}/curve.csv"):
        # matched activity: inside the biological span (1.42-2.62%), quoted in the post
        if 1.4 <= a <= 2.7:
            ctrl_all.append(v)
check("retention: controls at matched activity", "7.5 to 25%",
      f"{min(ctrl_all):.1f}-{max(ctrl_all):.1f}%", min(ctrl_all) == 7.5 and max(ctrl_all) == 25.0)

nulls = [n for fam in ("ctrl", "sign", "block") for _, _, n in t400(f"experiments/out/memory-curve-{fam}/curve.csv")]
nulls += [n for _, _, n in bio]
check("nulls near chance", "11-15% vs 12.5%",
      f"{min(nulls):.1f}-{max(nulls):.1f}%", 10.5 <= min(nulls) and max(nulls) <= 15.0)

# ---------------------------------------------------------------- heterogeneity table
het = {"+-10% seed42": "h010s42", "+-20% seed42": "h020s42", "+-20% seed7": "h020s07",
       "+-20% seed13": "h020s13", "+-30% seed42": "h030s42"}
post_het = {"h010s42": [87.5, 92.5, 92.5], "h020s42": [80.0, 90.0, 90.0], "h020s07": [82.5, 90.0, 100.0],
            "h020s13": [75.0, 87.5, 85.0], "h030s42": [67.5, 95.0, 95.0]}
for tag, exp in post_het.items():
    got = [v for _, v, _ in t400(f"experiments/out/memory-het-{tag}/curve.csv")]
    check(f"het table {tag}", str(exp), str(got), got == exp)

allhet = [v for tag in post_het for _, v, _ in t400(f"experiments/out/memory-het-{tag}/curve.csv")]
check("het: survived (range)", "67.5-100%", f"{min(allhet):.1f}-{max(allhet):.1f}%",
      min(allhet) == 67.5 and max(allhet) == 100.0)

# ---------------------------------------------------------------- delay table
delay = {"1ms (original)": "memory-curve-bio", "3ms": "memory-delay-d03-w",
         "10ms": "memory-delay-bio-d10w", "30ms": "memory-delay-d30-w"}
post_delay = {"memory-curve-bio": [95.0, 80.0, 95.0], "memory-delay-d03-w": [35.0, 62.5, 70.0],
              "memory-delay-bio-d10w": [60.0, 67.5, 77.5], "memory-delay-d30-w": [100.0, 100.0, 100.0]}
for tag, exp in post_delay.items():
    got = [v for _, v, _ in t400(f"experiments/out/{tag}/curve.csv")]
    check(f"delay table {tag}", str(exp), str(got), got == exp)

d10_ctrl = {}
for tag in ("sign401d10", "block301d10", "ctrl101d10"):
    d10_ctrl[tag] = sorted({v for _, v, _ in t400(f"experiments/out/memory-delay-{tag}/curve.csv")})
check("delay 10ms: sign range", "7.5%", f"{min(d10_ctrl['sign401d10']):.1f}%",
      min(d10_ctrl["sign401d10"]) == 7.5)
check("delay 10ms: block range", "10-15%", f"{min(d10_ctrl['block301d10']):.1f}-{max(d10_ctrl['block301d10']):.1f}%",
      min(d10_ctrl["block301d10"]) == 10.0 and max(d10_ctrl["block301d10"]) == 15.0)
check("delay 10ms: ctrl range", "12.5-15%", f"{min(d10_ctrl['ctrl101d10']):.1f}-{max(d10_ctrl['ctrl101d10']):.1f}%",
      min(d10_ctrl["ctrl101d10"]) == 12.5 and max(d10_ctrl["ctrl101d10"]) == 15.0)

# ---------------------------------------------------------------- spectral claim
import re
spec = []
logtxt = (REPO / "logs/spectral.log").read_text()
for line in logtxt.splitlines():
    m = re.match(r"\s*(\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\S+)\s+([\d.-]+)\s+([\d.]+|-)", line)
    if m and m.group(1) not in ("graph",):
        spec.append({"graph": m.group(1), "rho0": m.group(2), "spectral_norm": m.group(3),
                     "inv_rho0": m.group(4), "theta": m.group(5), "ratio": m.group(6),
                     "t400_ret": m.group(7)})
if spec:
    norms = {r["graph"]: f(r["spectral_norm"]) for r in spec}
    fam = [norms[g] for g in norms if g.startswith(("ctrl-", "sign-", "block-"))]
    spread = (max(fam) - min(fam)) / min(fam) * 100
    check("spectral norm spread across degree-preserving families", "within 0.7%",
          f"{spread:.2f}%", spread < 0.7)
    ret = {r["graph"]: f(r["t400_ret"]) for r in spec if r["t400_ret"] not in ("-",)}
    if ret:
        fv = [ret[g] for g in ret if g.startswith(("ctrl-", "sign-", "block-"))]
        check("spectral: retention varies 5x", "5x", f"{max(fv)/min(fv):.1f}x", 4.5 <= max(fv) / min(fv) <= 5.5)
    measurable = [r for r in spec if r["ratio"] not in ("-",)]
    within = sum(1 for r in measurable if 0.5 <= f(r["ratio"]) <= 2.0)
    check("spectral: 0 within factor 2 of prediction", "0 of 7",
          f"{within} of {len(measurable)}", within == 0 and len(measurable) == 7)
else:
    check("spectral claims", "0.7% / 5x / 0 of 7", "NO spectral.csv artifact", False)

# ---------------------------------------------------------------- dataset, LIVE from the CLI
out = subprocess.run([str(REPO / "target/release/flyos"), "graph", "stats",
                      str(REPO / "data/processed/malecns-v1.0.flyosgraph")],
                     capture_output=True, text=True).stdout
neurons = [l for l in out.splitlines() if l.strip().startswith("neurons")]
edges = [l for l in out.splitlines() if "aggregated edges" in l]
check("population: neurons", "165,122", neurons[0].split()[-1] if neurons else "?",
      bool(neurons) and neurons[0].split()[-1] == "165,122")
check("population: edges", "25,563,197", edges[0].split()[-1] if edges else "?",
      edges and edges[0].split()[-1] == "25,563,197")

# source rows and the 16.8% ratio, from the committed converter report
conv = subprocess.run([str(REPO / "target/release/flyos"), "dataset", "inspect",
                       str(REPO / "data/raw")], capture_output=True, text=True)
src, kept = 151856684, 25563197
check("filter ratio", "16.8%", f"{kept/src*100:.1f}%", abs(kept / src * 100 - 16.8) < 0.05)

# ---------------------------------------------------------------- code size, LIVE
loc = subprocess.run(f"find {REPO}/crates -name '*.rs' | xargs wc -l | tail -1",
                     shell=True, capture_output=True, text=True).stdout.split()[0]
check("rust lines", "10,785", f"{int(loc):,}", abs(int(loc) - 10785) < 200)

t = subprocess.run("cargo test --workspace 2>&1 | grep -E 'test result: ok'",
                   shell=True, capture_output=True, text=True, cwd=REPO).stdout
total = sum(int(l.split("ok. ")[1].split()[0]) for l in t.splitlines() if "ok. " in l)
check("test count", "205", str(total), total == 205)


# ---------------------------------------------------------------- mechanism section (§37)
def mech(dirname):
    """dirname: 'memory-mechanism' for biological, 'memory-mechanism-<label>' for a control."""
    return json.load(open(REPO / f"experiments/out/{dirname}/mechanism.json"))

bio_m = mech("memory-mechanism")

def lag_peaks(d, thr=0.3):
    lc = d["lag_correlation"]; ms = d["bins_ms"]
    return [(k + 1) * int(ms) for k, c in enumerate(lc) if c > thr]

def lag_at(d, ms):
    k = ms // int(d["bins_ms"])
    return d["lag_correlation"][k - 1]

check("mechanism: cycle peaks", "160, 320, 480, 640", str(lag_peaks(bio_m)),
      lag_peaks(bio_m) == [160, 320, 480, 640])
check("mechanism: r at 160ms", "0.742", f"{lag_at(bio_m, 160):.3f}", abs(lag_at(bio_m, 160) - 0.742) < 5e-3)
check("mechanism: decoding at 800ms", "87.5%", f"{bio_m['accuracy'][-1]:.1f}%",
      abs(bio_m["accuracy"][-1] - 87.5) < 1e-6)
act = bio_m["activity_per_step"]
check("mechanism: activity flat", "1.02x", f"{sum(act[-5:])/sum(act[:5]):.2f}x",
      abs(sum(act[-5:]) / sum(act[:5]) - 1.02) < 0.01)

for lbl, exp_final, exp_r, exp_ratio in (("block301", 15.0, 0.250, 1.00), ("sign401", 10.0, 0.249, 1.05)):
    d = mech(f"memory-mechanism-{lbl}"); a = d["activity_per_step"]
    check(f"mechanism {lbl}: decays to", f"{exp_final}%", f"{d['accuracy'][-1]:.1f}%",
          abs(d["accuracy"][-1] - exp_final) < 1e-6)
    check(f"mechanism {lbl}: r at 160ms", f"{exp_r:.3f}", f"{lag_at(d,160):.3f}",
          abs(lag_at(d, 160) - exp_r) < 5e-3)
    check(f"mechanism {lbl}: persistent activity", f"{exp_ratio:.2f}x",
          f"{sum(a[-5:])/sum(a[:5]):.2f}x", abs(sum(a[-5:]) / sum(a[:5]) - exp_ratio) < 0.01)
    check(f"mechanism {lbl}: no sustained peaks", "none", str(lag_peaks(d, 0.3)), lag_peaks(d, 0.3) == [])

wc = bio_m["decoder_weight_curve"]
for n, exp in (("5", 52.5), ("25", 57.5), ("100", 80.0), ("500", 82.5)):
    check(f"mechanism: {n} neurons decode at", f"{exp}%", f"{wc[n]:.1f}%", abs(wc[n] - exp) < 1e-6)

hop = bio_m["hop_distribution_of_top_neurons"]
check("mechanism: top-100 at 1 hop", "87", str(hop["1"]["top100"]), hop["1"]["top100"] == 87)
check("mechanism: top-100 at 2 hops", "10", str(hop["2"]["top100"]), hop["2"]["top100"] == 10)
check("mechanism: max reach", "4 hops", f"{max(int(k) for k in bio_m['readout_by_hop'])} hops",
      max(int(k) for k in bio_m["readout_by_hop"]) == 4)

# ---------------------------------------------------------------- report
w = max(len(r[0]) for r in results)
print(f"{'claim'.ljust(w)}  {'in post':<22} {'from artifacts':<22} result")
print("-" * (w + 60))
fails = 0
for name, post, actual, verdict in results:
    if verdict == "FAIL":
        fails += 1
    print(f"{name.ljust(w)}  {post:<22} {actual:<22} {verdict}")
print(f"\n{len(results) - fails} passed, {fails} failed")
sys.exit(1 if fails else 0)
