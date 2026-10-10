#!/usr/bin/env python3
"""Compare two scored.json files from score.py (Delta mode).

Usage:
  python3 delta.py old_scored.json new_scored.json [--out delta.json]

Prints per-site total and band movement, criterion changes, fixes closed
(projected fixes from the old run whose target the new run reached), and
sites added or dropped. Flags rubric version changes (v2 to v2.1 moved G).
"""
import argparse
import json

CRITERIA = "ABCDEFGHI"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--out", default="delta.json")
    a = ap.parse_args()
    old, new = load(a.old), load(a.new)
    notes = []
    if old.get("rubric_version") != new.get("rubric_version"):
        notes.append(f"Rubric changed {old.get('rubric_version')} -> {new.get('rubric_version')}. "
                     "v2 to v2.1 changed only G; compare G separately.")
    o = {s["site"]: s for s in old["sites"]}
    n = {s["site"]: s for s in new["sites"]}
    rows = []
    for site in sorted(set(o) & set(n)):
        so, sn = o[site], n[site]
        crit = []
        for c in CRITERIA:
            ro, rn = so["criteria"][c]["raw"], sn["criteria"][c]["raw"]
            if ro != rn:
                crit.append({"criterion": c, "old": ro, "new": rn,
                             "change": (rn - ro) if ro is not None and rn is not None else None,
                             "proof": sn["criteria"][c].get("proof", "")})
        closed, still_open = [], []
        for fx in so.get("fixes_applied", []):
            c = fx["criterion"]
            rn = sn["criteria"][c]["raw"]
            (closed if rn is not None and rn >= fx["to"] else still_open).append(fx)
        change = None if so["total"] is None or sn["total"] is None else round(sn["total"] - so["total"], 1)
        # like-for-like: only criteria scored in both runs, so newly scored or dropped criteria
        # (a coverage change) are not mistaken for improvement or decline
        both = [c for c in CRITERIA if so["criteria"][c]["raw"] is not None and sn["criteria"][c]["raw"] is not None]
        coverage_changed = len(both) != sum(1 for c in CRITERIA if sn["criteria"][c]["raw"] is not None) or \
            len(both) != sum(1 for c in CRITERIA if so["criteria"][c]["raw"] is not None)
        lfl = None
        if both:
            w = {c: sn["criteria"][c]["weight"] for c in both}
            tw = sum(w.values())
            lo = sum(so["criteria"][c]["raw"] / 10 * w[c] for c in both) / tw * 100
            ln = sum(sn["criteria"][c]["raw"] / 10 * w[c] for c in both) / tw * 100
            lfl = round(ln - lo, 1)
        rows.append({"site": site, "old_total": so["total"], "new_total": sn["total"], "change": change,
                     "like_for_like_change": lfl, "coverage_changed": coverage_changed,
                     "old_band": so["band"], "new_band": sn["band"], "criteria": crit,
                     "fixes_closed": closed, "fixes_open": still_open,
                     "coverage_old": so["coverage"], "coverage_new": sn["coverage"]})
    rows.sort(key=lambda r: -(r["change"] or 0))
    out = {"notes": notes, "sites": rows,
           "added": sorted(set(n) - set(o)), "dropped": sorted(set(o) - set(n)),
           "median_old": old["network"]["median_total"], "median_new": new["network"]["median_total"]}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    for note in notes:
        print("NOTE: " + note)
    print(f"network median {out['median_old']} -> {out['median_new']}")
    for r in rows:
        ch = "n/a" if r["change"] is None else f"{r['change']:+.1f}"
        bm = "" if r["old_band"] == r["new_band"] else f"  band {r['old_band']} -> {r['new_band']}"
        print(f"\n{r['site']}: {r['old_total']} -> {r['new_total']} ({ch}){bm}")
        if r["coverage_changed"]:
            lfl = "n/a" if r["like_for_like_change"] is None else f"{r['like_for_like_change']:+.1f}"
            print(f"   coverage changed ({r['coverage_old']*100:.0f}% -> {r['coverage_new']*100:.0f}%): "
                  f"like-for-like change {lfl}. Report this figure as the real movement; the headline "
                  f"change includes newly scored or dropped criteria")
        for c in r["criteria"]:
            print(f"   {c['criterion']}: {c['old']} -> {c['new']}")
        for fx in r["fixes_closed"]:
            print(f"   closed: {fx['fix']}")
        for fx in r["fixes_open"]:
            print(f"   open:   {fx['fix']}")
    if out["added"]:
        print("\nadded: " + ", ".join(out["added"]))
    if out["dropped"]:
        print("dropped: " + ", ".join(out["dropped"]))


if __name__ == "__main__":
    main()
