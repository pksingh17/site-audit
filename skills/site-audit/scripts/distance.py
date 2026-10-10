#!/usr/bin/env python3
"""Rewrite distance between a source text and an article (Distance mode).

Usage:
  python3 distance.py source.txt article.txt [--n 5] [--json]

Use verbatim text only (pasted or extracted from page source), never a
summarising fetch tool's paraphrase. Reports:
  - shingle overlap: share of article n-word shingles found in the source
  - entity overlap: capitalised names in the article also in the source
  - figures not in source: numbers, percentages, money and years in the
    article that never appear in the source (each one needs another source,
    or it is unsupported)
  - suggested B anchor from the rubric
"""
import argparse
import json
import re

WORD = re.compile(r"[a-z0-9']+")
FIG = re.compile(r"(?:[$€£₹]\s?)?\d[\d,]*(?:\.\d+)?\s?(?:%|percent|million|billion|bn|mn|crore|lakh|mw|gw|kg|tonnes?)?", re.I)
ENT = re.compile(r"\b(?:[A-Z][a-zA-Z&]+(?:\s+(?:of|and|for|de|la)?\s*[A-Z][a-zA-Z&]+)*)\b")
STOP_ENT = {"The", "A", "An", "In", "On", "At", "It", "This", "That", "We", "He", "She", "They", "But", "And", "For", "As", "By", "With", "From", "Its"}


def shingles(text, n):
    w = WORD.findall(text.lower())
    return [" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))]


def norm_fig(s):
    return re.sub(r"[\s,]", "", s.lower()).replace("percent", "%")


def entities(text):
    out = set()
    for m in ENT.findall(text):
        m = m.strip()
        if m in STOP_ENT or len(m) < 3:
            continue
        out.add(m)
    return out


def anchor(overlap):
    if overlap > 0.50:
        return 0
    if overlap >= 0.25:
        return 4
    return 6  # 8 or 10 need an independent source or original input; judge from the article


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("article")
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    src = open(a.source, encoding="utf-8").read()
    art = open(a.article, encoding="utf-8").read()

    art_sh = shingles(art, a.n)
    src_sh = set(shingles(src, a.n))
    overlap = (sum(1 for s in art_sh if s in src_sh) / len(art_sh)) if art_sh else 0.0

    src_figs = {norm_fig(f) for f in FIG.findall(src) if f.strip()}
    art_figs = [f.strip() for f in FIG.findall(art) if f.strip()]
    missing_figs = sorted({f for f in art_figs if norm_fig(f) not in src_figs and len(norm_fig(f)) > 1})

    ae, se = entities(art), entities(src)
    shared = sorted(ae & se)
    new_ents = sorted(ae - se)

    res = {
        "article_words": len(WORD.findall(art)),
        "source_words": len(WORD.findall(src)),
        "shingle_n": a.n,
        "shingle_overlap": round(overlap, 3),
        "entities_shared": shared,
        "entities_not_in_source": new_ents,
        "figures_not_in_source": missing_figs,
        "suggested_B_anchor": anchor(overlap),
    }
    if a.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return
    print(f"{overlap*100:.0f}% of article phrasing ({a.n}-word shingles) traceable to source")
    print(f"article {res['article_words']} words, source {res['source_words']} words")
    print(f"figures not in source ({len(missing_figs)}): {', '.join(missing_figs) or 'none'}")
    print(f"entities not in source ({len(new_ents)}): {', '.join(new_ents[:25]) or 'none'}")
    print(f"suggested B anchor: {res['suggested_B_anchor']} (raise to 8 or 10 only if the new entities and figures come from a verified independent source or original input)")


if __name__ == "__main__":
    main()
