#!/usr/bin/env python3
"""QA an audit PDF before it goes out.

Usage:
  python3 qa_pdf.py report.pdf [--scored scored.json] [--ban-dashes] [--png DIR] [--min-words 40]

Checks: em and en dash count (must be zero with --ban-dashes); blank or
near-empty pages (the final page may be short); every site total in
scored.json appears in the PDF text; per-page word counts. --png renders each
page with pdftoppm so you can look at them. Exit code 1 on any failure.
"""
import argparse
import json
import os
import subprocess
import sys

from pypdf import PdfReader


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--scored")
    ap.add_argument("--ban-dashes", action="store_true")
    ap.add_argument("--png")
    ap.add_argument("--min-words", type=int, default=40)
    a = ap.parse_args()

    reader = PdfReader(a.pdf)
    texts = [(p.extract_text() or "") for p in reader.pages]
    full = "\n".join(texts)
    fails = []
    n = len(texts)
    print(f"pages: {n}")
    for i, t in enumerate(texts, 1):
        wc = len(t.split())
        last = i == n
        cover = i == 1
        flag = ""
        if wc == 0:
            flag = "  BLANK"
            fails.append(f"page {i} is blank")
        elif wc < a.min_words and not last and not cover:
            flag = "  near-empty"
            fails.append(f"page {i} has only {wc} words (stacked page break or orphaned block?)")
        print(f"  page {i}: {wc} words{flag}")

    if a.ban_dashes:
        em, en = full.count("—"), full.count("–")
        print(f"em dashes: {em}  en dashes: {en}")
        if em or en:
            fails.append(f"dash ban broken: {em} em, {en} en")

    if a.scored:
        sc = json.load(open(a.scored, encoding="utf-8"))
        flat = full.replace("\n", " ")
        for s in sc["sites"]:
            if s["total"] is not None and f"{s['total']:.1f}" not in flat:
                fails.append(f"total {s['total']:.1f} for {s['site']} not found in PDF")
        print(f"checked {len(sc['sites'])} site totals against PDF text")

    if a.png:
        os.makedirs(a.png, exist_ok=True)
        r = subprocess.run(["pdftoppm", "-png", "-r", "60", a.pdf, os.path.join(a.png, "page")],
                           capture_output=True, text=True)
        if r.returncode:
            print("pdftoppm failed: " + r.stderr.strip())
        else:
            print(f"page images in {a.png}; view them before sending")

    if fails:
        print("\nFAIL")
        for f in fails:
            print("  - " + f)
        sys.exit(1)
    print("\nPASS")


if __name__ == "__main__":
    main()
