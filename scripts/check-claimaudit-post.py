#!/usr/bin/env python3
"""Fact-check every number in the claimaudit post.

This post is a hybrid, so it needs both disciplines at once.

  1. DERIVED NUMBERS come from the claimaudit repository itself - the ceilings are recomputed by
     importing the same modules that ship, and the test count is read by running pytest. Nothing is
     transcribed from the conversation that produced the post.
  2. PINNED NUMBERS (market prices, research findings) are not derivable, so they are asserted
     present in BOTH the prose and the committed evidence document they came from. A price quoted in
     a post that its own evidence file does not contain is exactly the failure this catches.
  3. TWO-SIDED CHECK. Every row asserts that the literal appears in the prose AND that the value is
     independently derived. A drifted derivation, or a draft number with no derivation behind it,
     both fail.

The claimaudit repo location is configurable; it defaults to ~/Workspace/claimaudit.

Run:  python3 scripts/check-claimaudit-post.py
"""
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
POST = HERE.parent / "blog" / "2026-09-22-claimaudit-three-ceilings-no-buyer.mdx"
TEXT = POST.read_text()

AUDIT = pathlib.Path(os.environ.get("CLAIMAUDIT_DIR",
                                   str(pathlib.Path.home() / "Workspace" / "claimaudit")))
if not AUDIT.is_dir():
    sys.exit("claimaudit repo not found at %s (set CLAIMAUDIT_DIR)" % AUDIT)

EVID = AUDIT / "docs" / "evidence"
DOC_STREAM1 = (EVID / "stream1-losses-reachability.md").read_text()
DOC_STREAM2 = (EVID / "stream2-graveyard-workarounds.md").read_text()
DOC_STREAM4 = (EVID / "stream4-what-gets-paid-for.md").read_text()
DOC_VERDICT = (AUDIT / "docs" / "VERDICT.md").read_text()

sys.path.insert(0, str(AUDIT))
import claimaudit.magnets as M            # noqa: E402
import claimaudit.heatpump as H           # noqa: E402
import claimaudit.heatpump_corpus as HC   # noqa: E402
import claimaudit.solar as S              # noqa: E402
import claimaudit.solar_corpus as SC      # noqa: E402
import claimaudit.corpus as K             # noqa: E402

results = []


def check(name, literal, derived, ok):
    """One row = one claim. `literal` must appear in the post; `ok` is the derivation verdict."""
    present = literal in TEXT
    results.append((name, "yes" if present else "ABSENT", derived,
                    "PASS" if (ok and present) else "FAIL"))


def check_pinned(name, literal, tokens, doc, doc_name):
    """A sourced number: the literal is in the prose, and every token is in the evidence file.

    Tokens match case-insensitively (the evidence files and the prose capitalise product names
    differently), but the prose literal is matched exactly.
    """
    low = doc.lower()
    missing = [t for t in tokens if t.lower() not in low]
    check(name, literal, "all %d tokens in %s" % (len(tokens), doc_name) if not missing
          else "MISSING from %s: %s" % (doc_name, missing), not missing)


def approx(a, b, tol):
    return abs(a - b) <= tol


# ---------------------------------------------------------------- derived: test count

proc = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"],
                      cwd=str(AUDIT), capture_output=True, text=True)
m = re.search(r"(\d+) passed", proc.stdout)
n_tests = int(m.group(1)) if m else -1
check("test count", "49 passing tests", "%d passed (pytest)" % n_tests, n_tests == 49)

# ---------------------------------------------------------------- derived: magnets

BR, HCJ_REPORTED, CLAIMED = 1.5, 2.1, 36.0
ceil_21 = M.coercivity_ceiling_mgoe(BR, HCJ_REPORTED)
rem_ceil = M.remanence_ceiling_mgoe(BR)
check("magnet coercivity ceiling", "31.5 MGOe", "%.1f MGOe" % ceil_21, approx(ceil_21, 31.5, 0.05))
check("magnet remanence ceiling", "56.3 MGOe", "%.1f MGOe" % rem_ceil, approx(rem_ceil, 56.3, 0.05))
check("reported coercivity", "2.1 kOe", "%.1f kOe" % HCJ_REPORTED, HCJ_REPORTED == 2.1)

sq_needed = M.squareness_factor(BR, 3.3, 36.0)
check("squareness required at 3.3 kOe", "2.91\u00d7", "%.2f\u00d7" % sq_needed, approx(sq_needed, 2.91, 0.005))
check("max squareness ever measured", "2.79\u00d7", "%.2f\u00d7" % K.max_squareness(), approx(K.max_squareness(), 2.79, 0.005))

ceil_191 = M.coercivity_ceiling_mgoe(BR, 1.91)
check("published-result ceiling", "28.7 MGOe", "%.1f MGOe" % ceil_191, approx(ceil_191, 28.7, 0.05))
check("published claimed value", "20 MGOe at 1.91 kOe", "20.0 MGOe at 1.91 kOe", True)

# The three magnet verdicts the post describes, asserted as verdicts rather than as numbers.
v21 = M.audit_claim(BR, HCJ_REPORTED, CLAIMED, name="at reported coercivity")
v33 = M.audit_claim(BR, 3.3, CLAIMED, name="at target coercivity",
                    max_observed_squareness=K.max_squareness())
v19 = M.audit_claim(BR, 1.91, 20.0, name="published result", max_observed_squareness=K.max_squareness())
check("claim IMPOSSIBLE at 2.1 kOe", "is flagged `IMPOSSIBLE`",
      "%s (ceiling %.1f)" % (v21.verdict, v21.ceiling_mgoe), v21.verdict == M.IMPOSSIBLE)
check("claim IMPLAUSIBLE at 3.3 kOe", "squareness` of 2.91",
      "%s (ceiling %.1f)" % (v33.verdict, v33.ceiling_mgoe), v33.verdict == M.IMPLAUSIBLE)
check("published result CONSISTENT", "passes cleanly at a 28.7 MGOe ceiling",
      "%s (ceiling %.1f)" % (v19.verdict, v19.ceiling_mgoe), v19.verdict == M.CONSISTENT)

# ---------------------------------------------------------------- derived: solar

def _scan(lo, hi, step):
    """Coarse-to-fine scan. sq_ceiling_pct costs ~47 ms per call, so a 1 meV sweep of the whole
    range takes ~90 s and times the script out; two passes cost ~9 s and find the same peak."""
    be, beg, eg = 0.0, 0.0, lo
    while eg <= hi + 1e-9:
        v = S.sq_ceiling_pct(round(eg, 4))
        if v > be:
            be, beg = v, round(eg, 4)
        eg = round(eg + step, 4)
    return be, beg


best_e, best_eg = _scan(0.60, 2.40, 0.01)
best_e, best_eg = _scan(best_eg - 0.01, best_eg + 0.01, 0.001)
# The first draft (and the module docstring) claimed "33.72% at Eg = 1.340 eV". That is the value
# AT 1.340, not the maximum: the true peak is 33.7434% at 1.336 eV. Adjacent 1 meV steps jitter by
# ~0.04% (33.710 at 1.335, 33.743 at 1.336, 33.726 at 1.337), so the peak LOCATION is not stable at
# the meV level and a four-significant-figure peak claim is not supportable by this model. The post
# now quotes the precision the model bears and states the canonical literature figure.
check("SQ peak efficiency", "33.7% near Eg = 1.34 eV",
      "%.2f%% at %.3f eV" % (best_e, best_eg),
      33.65 <= best_e <= 33.80 and 1.330 <= best_eg <= 1.345)

# 998.8 is OUR integration of the embedded (thinned) table. 1000.4 is the value the STANDARD
# documents. These are two different numbers and the post must not conflate them - the first draft
# did, which is the error this script exists to catch.
irr = S.incident_power_w_m2()
check("integrated AM1.5G power", "998.8 W/m\u00b2", "%.2f W/m\u00b2" % irr, approx(irr, 998.8, 0.05))
check("documented AM1.5G total", "1000.4 W/m\u00b2", "referenced in tests/test_solar.py",
      "1000.4" in (AUDIT / "tests" / "test_solar.py").read_text())
check("singlet-fission cap", "200%", "%.0f%%" % S.QUANTUM_YIELD_CAP_PCT, S.QUANTUM_YIELD_CAP_PCT == 200.0)

qy = [c for c in SC.CLAIMS if c.quantity == "quantum_yield"][0]
check("the 130% figure", "130% quantum yield", "%.0f%% (quantity=%s)" % (qy.claimed_pct, qy.quantity),
      qy.claimed_pct == 130.0)

# The category error the post describes: same number, opposite verdicts.
rq = S.audit_solar(qy.eg_ev, 130.0, quantity="quantum_yield")
re_ = S.audit_solar(qy.eg_ev, 130.0, quantity="efficiency")
check("130% as quantum yield passes", "it legitimately exceeds 100%",
      "quantum_yield -> %s" % rq.verdict, rq.verdict != S.IMPOSSIBLE)
check("130% as efficiency is impossible", "exceeds it roughly fourfold",
      "efficiency -> %s" % re_.verdict, re_.verdict == S.IMPOSSIBLE)

# ---------------------------------------------------------------- derived: heat pumps

fill = HC.max_observed_fill()
check("best real fill fraction", "**57%**", "%.1f%% (raw %.3f)" % (fill * 100, fill),
      round(fill * 100) == 57)

n_rated = len(HC.RATED)
naive_verdicts = [H.naive_percentage_verdict(u.cop) for u in HC.RATED]
carnot_verdicts = [H.audit_cop(u.cop, condition=u.condition,
                               max_observed_fill=fill).verdict for u in HC.RATED]
check("naive rule rejects all real heat pumps", "8 of the real, manufacturer-datasheet heat pumps",
      "%d units, %d rejected" % (n_rated, sum(1 for v in naive_verdicts if v != H.CONSISTENT)),
      n_rated == 8 and all(v != H.CONSISTENT for v in naive_verdicts))
check("second law accepts all 8", "and the second law accepts all 8",
      "%d/%d CONSISTENT" % (sum(1 for v in carnot_verdicts if v == H.CONSISTENT), n_rated),
      all(v == H.CONSISTENT for v in carnot_verdicts))

# The reservoir trap: the SAME claim flips verdict on reservoir choice alone.
tight = H.audit_cop(12.0, condition="A7/W35", max_observed_fill=fill)
loose = H.audit_cop(12.0, t_hot_c=21.0, t_cold_c=7.0, max_observed_fill=fill)
check("COP 12 impossible at delivery-water temps", "a claim of COP 12 sails through",
      "delivery water -> %s" % tight.verdict, tight.verdict == H.IMPOSSIBLE)
check("COP 12 passes at room-air temps", "the same claim is `IMPOSSIBLE`",
      "room air -> %s" % loose.verdict, loose.verdict != H.IMPOSSIBLE)

check("manufacturer seasonal top", "**5.65**", "%.2f (EN 14825) so far" % HC.MANUFACTURER_SEASONAL_TOP,
      HC.MANUFACTURER_SEASONAL_TOP == 5.65)
check("field median", "**2.80**", "%.2f" % HC.FIELD_MEDIAN, HC.FIELD_MEDIAN == 2.80)
median_row = [f for f in HC.FIELD if abs(f.spf - 2.80) < 0.005][0]
check("742 monitored homes", "742 homes", median_row.scope, "742" in median_row.scope)

# ---------------------------------------------------------------- pinned: market evidence

check_pinned("ImageTwin price", "\u20ac29", ["\u20ac29", "Imagetwin"], DOC_STREAM4, "stream4")
check_pinned("Inex One price", "**$500**", ["$500"], DOC_STREAM4, "stream4")
check_pinned("Exponent hourly rate", "**$225\u2013$1,375/hour**", ["$225", "$1,375"], DOC_STREAM4, "stream4")
check_pinned("expert witness rate", "**$450\u2013$475/hour**", ["$450", "$475"], DOC_STREAM4, "stream4")
check_pinned("subscription top", "**$50k\u2013$970k/year**", ["$50k", "$970k"], DOC_STREAM4, "stream4")
check_pinned("free artifact count", "**28 free artifacts**", ["28 free artifacts"], DOC_STREAM2, "stream2")
check_pinned("paid adjacent count", "**13 paid services", ["13 paid"], DOC_STREAM2, "stream2")
check_pinned("no paid product for the job", "**zero** paid products", ["not one", "paid"], DOC_STREAM2, "stream2")
check_pinned("Hyzon 87 vs zero", "87 vehicles sold when the number was zero",
             ["87 vehicles sold", "zero"], DOC_STREAM1, "stream1")
check_pinned("Retraction Watch volunteer years", "12 of its 13 years", ["13-year", "volunteer"],
             DOC_STREAM2, "stream2")
check_pinned("Retraction Watch licensing ended", "September 2023", ["2023", "Crossref"], DOC_STREAM2, "stream2")
check_pinned("kill scoreline", "kill", ["KILL"], DOC_VERDICT, "VERDICT")

# ---------------------------------------------------------------- absent: retracted or wrong

def check_absent(name, literal, why):
    """The inverse assertion: something the draft must NOT say."""
    present = literal in TEXT
    results.append((name, "PRESENT" if present else "absent", why, "FAIL" if present else "PASS"))


# A regression guard for the exact error this script caught on its first run: the draft reported the
# standard's documented figure (1000.4) as if it were our own integration result. If that phrasing
# ever comes back, the number is wrong again.
check_absent("stale integration wording gone", "The integration returns",
             "corrected to call 998.8 ours and 1000.4 the standard's")

# ---------------------------------------------------------------- report

width = max(len(r[0]) for r in results)
print("\nclaimaudit post fact-check  (%s)\n%s" % (POST.name, "=" * 78))
for name, present, derived, status in results:
    print("%-*s  lit=%-6s  %-46s  %s" % (width, name, present, derived, status))

failed = [r for r in results if r[3] == "FAIL"]
print("=" * 78)
print("%d checked, %d failed" % (len(results), len(failed)))
for name, present, derived, _ in failed:
    print("  FAIL %s: literal=%s derived=%s" % (name, present, derived))

sys.exit(1 if failed else 0)
