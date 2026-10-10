#!/usr/bin/env python3
"""Score sites against the site-audit rubric v2.1.

Usage:
  python3 score.py data.json [--out scored.json] [--group owner]

Reads the run data file, validates every raw score (ladder anchors, additive
range, proof present, N/A allowed), computes weighted totals with N/A and
unscored weight redistributed, coverage, bands, projection from fixes,
network and per-criterion medians. Invalid scores are dropped to unscored and
reported. Exit code 1 when any validation problem was found, so it cannot be
missed.
"""
import argparse
import json
import statistics
import sys

RUBRIC_VERSION = "2.1"
CRITERIA = "ABCDEFGHI"
NAMES = {
    "A": "Duplication and story governance",
    "B": "Added value beyond the source",
    "C": "Source transparency",
    "D": "Ownership and trust signals",
    "E": "Topic and audience fit",
    "F": "Technical hygiene",
    "G": "AI answer (AEO) readiness",
    "H": "Publishing consistency",
    "I": "Performance and mobile UX",
}
WEIGHTS = {
    "event":     {"A": 15, "B": 12, "C": 12, "D": 13, "E": 10, "F": 10, "G": 10, "H": 10, "I": 8},
    "publisher": {"A": 18, "B": 15, "C": 15, "D": 14, "E": 8,  "F": 8,  "G": 10, "H": 7,  "I": 5},
    "local":     {"A": 5,  "B": 5,  "C": 5,  "D": 20, "E": 10, "F": 15, "G": 15, "H": 5,  "I": 20},
    "ecommerce": {"A": 10, "B": 10, "C": 5,  "D": 15, "E": 10, "F": 20, "G": 10, "H": 5,  "I": 15},
    "b2b":       {"A": 10, "B": 12, "C": 10, "D": 15, "E": 12, "F": 12, "G": 12, "H": 7,  "I": 10},
}
LADDER = {"A", "B", "C", "E", "H", "I"}
ADDITIVE = {"D", "F", "G"}
ANCHORS = {0, 2, 4, 6, 8, 10}
NA_ALLOWED = {"A", "B", "C", "H"}
PROVISIONAL_BELOW = 0.80

for t, w in WEIGHTS.items():
    assert sum(w.values()) == 100, t


def band(total):
    if total >= 80:
        return "benchmark met"
    if total >= 65:
        return "adequate"
    if total >= 55:
        return "at risk"
    return "high risk"


def validate(site_name, code, entry, problems):
    """Return ('na'|'scored'|'unscored', raw)."""
    if entry is None:
        return "unscored", None
    raw, proof, na = entry.get("raw"), (entry.get("proof") or "").strip(), entry.get("na")
    if raw is None:
        if na:
            if code not in NA_ALLOWED:
                problems.append(f"{site_name} {code}: N/A not allowed for this criterion; treated as unscored")
                return "unscored", None
            return "na", None
        return "unscored", None
    if na:
        problems.append(f"{site_name} {code}: has both a raw score and N/A; using the score")
    if not isinstance(raw, (int, float)) or raw != int(raw):
        problems.append(f"{site_name} {code}: raw {raw!r} is not a whole number; dropped")
        return "unscored", None
    raw = int(raw)
    if code in LADDER and raw not in ANCHORS:
        problems.append(f"{site_name} {code}: {raw} is off-ladder (use 0,2,4,6,8,10, lower anchor when between); dropped")
        return "unscored", None
    if code in ADDITIVE and not 0 <= raw <= 10:
        problems.append(f"{site_name} {code}: {raw} outside 0..10; dropped")
        return "unscored", None
    if not proof:
        problems.append(f"{site_name} {code}: no proof note; no proof, no score; dropped")
        return "unscored", None
    return "scored", raw


def total_for(raws, weights, states):
    scored_w = sum(weights[c] for c in CRITERIA if states[c] == "scored")
    applicable_w = sum(weights[c] for c in CRITERIA if states[c] != "na")
    if scored_w == 0:
        return None, 0.0
    pts = sum(raws[c] / 10 * weights[c] for c in CRITERIA if states[c] == "scored")
    return round(pts / scored_w * 100, 1), (scored_w / applicable_w if applicable_w else 0.0)


def score_site(site, problems):
    name = site.get("site", "?")
    stype = site.get("type", "").lower()
    if stype not in WEIGHTS:
        problems.append(f"{name}: unknown type {stype!r}; using 'b2b'. Valid: {', '.join(WEIGHTS)}")
        stype = "b2b"
    weights = WEIGHTS[stype]
    scores = site.get("scores", {})
    states, raws, rows = {}, {}, {}
    for c in CRITERIA:
        st, raw = validate(name, c, scores.get(c), problems)
        states[c], raws[c] = st, raw
    total, coverage = total_for(raws, weights, states)
    eff_w = sum(weights[c] for c in CRITERIA if states[c] == "scored")
    for c in CRITERIA:
        rows[c] = {
            "name": NAMES[c],
            "weight": weights[c],
            "state": states[c],
            "raw": raws[c],
            "weighted": round(raws[c] / 10 * weights[c] / eff_w * 100, 2) if states[c] == "scored" and eff_w else None,
            "proof": (scores.get(c) or {}).get("proof", ""),
            "na": (scores.get(c) or {}).get("na"),
        }
    # projection
    proj_raws, proj_states = dict(raws), dict(states)
    applied = []
    for fx in site.get("fixes", []) or []:
        c, to = fx.get("criterion"), fx.get("to")
        if c not in CRITERIA or states[c] != "scored" or not isinstance(to, int):
            problems.append(f"{name}: fix {fx!r} skipped (criterion must be scored and 'to' a whole number)")
            continue
        if c in LADDER and to not in ANCHORS:
            problems.append(f"{name}: fix target {c}={to} off-ladder; skipped")
            continue
        if to > proj_raws[c]:
            proj_raws[c] = min(to, 10)
            applied.append(fx)
    projected, _ = total_for(proj_raws, weights, proj_states)
    provisional = coverage < PROVISIONAL_BELOW
    return {
        "site": name,
        "type": stype,
        "owner": site.get("owner", ""),
        "total": total,
        "band": band(total) if total is not None else "unscored",
        "coverage": round(coverage, 3),
        "provisional": provisional,
        "projected": projected,
        "projected_band": band(projected) if projected is not None else "unscored",
        "fixes_applied": applied,
        "fetch_blocked": bool(site.get("fetch_blocked")),
        "criteria": rows,
    }


def median_or_none(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.median(vals), 1) if vals else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data")
    ap.add_argument("--out", default="scored.json")
    ap.add_argument("--group", help="field to group totals by, e.g. owner")
    a = ap.parse_args()

    with open(a.data, encoding="utf-8") as f:
        data = json.load(f)
    if str(data.get("rubric_version", RUBRIC_VERSION)) != RUBRIC_VERSION:
        print(f"WARNING: data says rubric {data.get('rubric_version')}, scorer is {RUBRIC_VERSION}")

    problems = []
    results = [score_site(s, problems) for s in data.get("sites", [])]
    results.sort(key=lambda r: (r["total"] is None, r["total"] if r["total"] is not None else 0))

    medians = {c: median_or_none([r["criteria"][c]["raw"] for r in results]) for c in CRITERIA}
    out = {
        "rubric_version": RUBRIC_VERSION,
        "run_date": data.get("run_date"),
        "sites": results,
        "network": {
            "count": len(results),
            "median_total": median_or_none([r["total"] for r in results]),
            "median_projected": median_or_none([r["projected"] for r in results]),
            "criterion_medians": medians,
            "bands": {b: sum(1 for r in results if r["band"] == b) for b in
                      ["benchmark met", "adequate", "at risk", "high risk", "unscored"]},
        },
        "problems": problems,
    }
    if a.group:
        groups = {}
        src = {s.get("site"): s for s in data.get("sites", [])}
        for r in results:
            key = src.get(r["site"], {}).get(a.group) or "(none)"
            groups.setdefault(key, []).append(r["total"])
        out["groups"] = {k: {"sites": len(v), "median": median_or_none(v)} for k, v in groups.items()}

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"{'site':32} {'type':10} {'total':>6} {'band':14} {'cov':>5} {'proj':>6}")
    for r in results:
        t = "-" if r["total"] is None else f"{r['total']:.1f}"
        p = "-" if r["projected"] is None else f"{r['projected']:.1f}"
        flag = " provisional" if r["provisional"] else ""
        print(f"{r['site'][:32]:32} {r['type']:10} {t:>6} {r['band']:14} {r['coverage']*100:4.0f}% {p:>6}{flag}")
    n = out["network"]
    print(f"\nnetwork median {n['median_total']}  projected {n['median_projected']}  bands {n['bands']}")
    print("criterion medians: " + "  ".join(f"{c}={medians[c]}" for c in CRITERIA))
    if a.group:
        print("groups: " + json.dumps(out["groups"]))
    if problems:
        print(f"\n{len(problems)} PROBLEM(S): fix these before reporting")
        for p in problems:
            print("  - " + p)
        sys.exit(1)


if __name__ == "__main__":
    main()
