#!/usr/bin/env python3
"""Build the audit PDF from scored.json (numbers) and report.json (prose).

Usage:
  python3 build_report.py scored.json report.json [--out report.pdf]

Numbers come only from scored.json, so prose and tables cannot drift from the
scorer. With "ban_dashes": true in report.json, em and en dashes are replaced
everywhere before rendering. See references/report-spec.md for report.json.
Needs reportlab.
"""
import argparse
import json
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

INK = colors.HexColor("#1d2433")
MUTED = colors.HexColor("#5b6475")
ACCENT = colors.HexColor("#1f4e79")
RULE = colors.HexColor("#d5dae3")
BAND_COLOURS = {"benchmark met": "#2e7d4f", "adequate": "#4a7bb7", "at risk": "#c98a12",
                "high risk": "#b23b3b", "unscored": "#8a8f99"}


def clean(s, ban):
    s = "" if s is None else str(s)
    if ban:
        s = re.sub(r"\s*—\s*", ", ", s)
        s = re.sub(r"(\d)\s*–\s*(\d)", r"\1 to \2", s)
        s = re.sub(r"\s*–\s*", ", ", s)
    return s


def styles():
    ss = getSampleStyleSheet()
    base = dict(fontName="Helvetica", textColor=INK, alignment=TA_LEFT)
    return {
        "title": ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=26, leading=31, textColor=INK, spaceAfter=8),
        "subtitle": ParagraphStyle("st", fontName="Helvetica", fontSize=13, leading=17, textColor=MUTED, spaceAfter=24),
        "meta": ParagraphStyle("m", fontSize=10, leading=15, textColor=MUTED, **{k: v for k, v in base.items() if k != "textColor"}),
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=ACCENT, spaceBefore=14, spaceAfter=6),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=INK, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("b", fontSize=10, leading=14.5, spaceAfter=6, **base),
        "cell": ParagraphStyle("c", fontSize=8.5, leading=11, **base),
        "cellb": ParagraphStyle("cb", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white),
        "big": ParagraphStyle("big", fontName="Helvetica-Bold", fontSize=30, leading=34, textColor=ACCENT),
        "_": ss,
    }


def table(rows, st, widths=None, ban=False):
    data = [[Paragraph(escape(clean(c, ban)), st["cellb"] if i == 0 else st["cell"]) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def para(text, st, ban, style="body"):
    return Paragraph(escape(clean(text, ban)), st[style])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, doc._audit_title)
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scored")
    ap.add_argument("report")
    ap.add_argument("--out", default="report.pdf")
    a = ap.parse_args()
    sc = json.load(open(a.scored, encoding="utf-8"))
    rp = json.load(open(a.report, encoding="utf-8"))
    ban = bool(rp.get("ban_dashes"))
    st = styles()
    W = A4[0] - 36 * mm
    story = []
    net = sc["network"]
    sites = sc["sites"]

    # cover
    story += [Spacer(1, 50 * mm), para(rp.get("title", "Website audit"), st, ban, "title"),
              para(rp.get("subtitle", ""), st, ban, "subtitle")]
    for label, key in (("Prepared by", "prepared_by"), ("Prepared for", "prepared_for"),
                       ("Report date", "date"), ("Evidence gathered", "evidence_date")):
        if rp.get(key):
            story.append(para(f"{label}: {rp[key]}", st, ban, "meta"))
    story.append(para(f"Rubric version {sc.get('rubric_version')}. Sites scored: {net['count']}.", st, ban, "meta"))
    story.append(PageBreak())

    # summary
    story.append(para("Executive summary", st, ban, "h1"))
    if net["count"] == 1:
        s0 = sites[0]
        head = f"{s0['total']}" if s0["total"] is not None else "unscored"
        story.append(Paragraph(escape(head) + "<font size=12 color='#5b6475'> / 100, "
                               + escape(s0["band"]) + (", provisional" if s0["provisional"] else "") + "</font>", st["big"]))
        if s0["projected"] is not None and s0["total"] is not None and s0["projected"] > s0["total"]:
            story.append(para(f"Projected after listed fixes: {s0['projected']} ({s0['projected_band']}).", st, ban))
    else:
        story.append(Paragraph(escape(str(net["median_total"])) + "<font size=12 color='#5b6475'> network median / 100</font>", st["big"]))
        bands = ", ".join(f"{v} {k}" for k, v in net["bands"].items() if v)
        story.append(para(f"Bands: {bands}. Projected median after listed fixes: {net['median_projected']}.", st, ban))
    story.append(Spacer(1, 4))
    for p in rp.get("summary", []):
        story.append(para(p, st, ban))

    # method
    story.append(para("Method and rubric", st, ban, "h1"))
    if rp.get("method"):
        story.append(para(rp["method"], st, ban))
    story.append(para("Each criterion is scored 0 to 10 against fixed anchors and weighted by site type. "
                      "Criteria that do not apply are marked N/A and their weight is redistributed. Criteria without proof "
                      "stay unscored and lower coverage; coverage below 80 percent marks a total provisional. Bands: 80 and above "
                      "benchmark met; 65 to 79 adequate; 55 to 64 at risk; below 55 high risk. The rubric is this audit's own, "
                      "derived from published search and publisher policy. Scores measure exposure under those policies, "
                      "not traffic, rankings or penalties.", st, ban))

    # scorecard
    story.append(para("Scorecard", st, ban, "h1"))
    rows = [["Site", "Type", "Total", "Band", "Coverage", "Projected"]]
    for s in sites:
        rows.append([s["site"] + (" (fetch blocked)" if s.get("fetch_blocked") else ""), s["type"],
                     "unscored" if s["total"] is None else f"{s['total']:.1f}" + (" *" if s["provisional"] else ""),
                     s["band"], f"{s['coverage']*100:.0f}%",
                     "" if s["projected"] is None else f"{s['projected']:.1f}"])
    story.append(table(rows, st, [W * .32, W * .12, W * .13, W * .17, W * .12, W * .14], ban))
    if any(s["provisional"] for s in sites):
        story.append(para("* provisional: less than 80 percent of applicable weight scored.", st, ban, "meta"))

    # per-site criteria
    for s in sites:
        crow = [["Criterion", "Weight", "Raw", "Proof"]]
        for code, c in s["criteria"].items():
            raw = "N/A" if c["state"] == "na" else ("unscored" if c["raw"] is None else f"{c['raw']}/10")
            proof = c["na"] if c["state"] == "na" else (c["proof"] or "awaiting evidence")
            crow.append([f"{code}. {c['name']}", str(c["weight"]), raw, proof])
        block = [para(f"{s['site']}: criterion detail", st, ban, "h2"),
                 table(crow, st, [W * .30, W * .09, W * .11, W * .50], ban)]
        story.append(KeepTogether(block[:1] + [block[1]]))

    # custom sections
    for sec in rp.get("sections", []):
        items = [para(sec.get("heading", ""), st, ban, "h1")]
        for p in sec.get("paragraphs", []):
            items.append(para(p, st, ban))
        story.append(KeepTogether(items[:2]))
        story += items[2:]
        if sec.get("table"):
            tb = sec["table"]
            n = len(tb[0])
            story.append(table(tb, st, [W / n] * n, ban))

    # fixes
    if rp.get("fix_list"):
        story.append(para("Fix list", st, ban, "h1"))
        rows = [["Fix", "Owner", "Criterion"]] + [[f.get("item", ""), f.get("owner", ""), f.get("criterion", "")]
                                                    for f in rp["fix_list"]]
        story.append(table(rows, st, [W * .62, W * .23, W * .15], ban))

    # limits and references
    if rp.get("limits"):
        story.append(para("Limits and what still needs access", st, ban, "h1"))
        for l in rp["limits"]:
            story.append(para("• " + clean(l, ban), st, ban))
    if rp.get("references"):
        story.append(para("References", st, ban, "h1"))
        for r in rp["references"]:
            story.append(para(f"{r.get('title','')}. {r.get('url','')} (last updated {r.get('updated') or 'not shown'})", st, ban))

    doc = SimpleDocTemplate(a.out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm, title=clean(rp.get("title", "Website audit"), ban),
                            author=clean(rp.get("prepared_by", ""), ban))
    doc._audit_title = clean(rp.get("title", "Website audit"), ban)
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=footer)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
