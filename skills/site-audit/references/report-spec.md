# PDF report spec

Build with `scripts/build_report.py` from `scored.json` plus `report.json` (prose sections). Never hand-type a number that `score.py` computed; the builder pulls them.

## report.json
```json
{
  "title": "Website audit",
  "subtitle": "SEO, AI-answer readiness and content risk",
  "prepared_by": "byline the user gave",
  "prepared_for": "client or team",
  "date": "2026-10-09",
  "evidence_date": "2026-10-08",
  "ban_dashes": true,
  "summary": ["paragraph", "paragraph"],
  "method": "paragraph",
  "sections": [{"heading": "Duplication register", "paragraphs": ["..."], "table": [["Cluster","Sites","Proof"],["..."]]}],
  "fix_list": [{"item": "Add bylines", "owner": "Editorial", "criterion": "D"}],
  "limits": ["..."],
  "references": [{"title": "Spam policies", "url": "https://...", "updated": "2026-..."}]
}
```

## Section order
1. Cover: title, subtitle, prepared-by line, prepared-for, date, evidence access date
2. Executive summary: headline number, what works, fastest lift (from the projection)
3. Method and rubric: site types and weights used, bands, coverage rule, the exposure-not-penalty statement
4. Scorecard: sorted low to high, band, coverage, provisional marker, owner column when grouped
5. Custom sections from `report.json` in order (duplication register, brand collision, roster cross-check, network evidence, site-by-site proof, correction note)
6. Fix list: network items first, then per site or owner
7. Limits and what still needs access
8. References with last-updated dates

## QA (run `scripts/qa_pdf.py report.pdf --scored scored.json [--ban-dashes]`)
- Zero em-dashes and en-dashes in extracted text when the style rule bans them.
- No blank pages; no near-empty page except the last.
- Every total in the scored data appears in the PDF text.
- Render pages to PNG (`--png DIR`) and look at them: no orphaned headings, no wrapped table headers, no overflow.
- When scope changes (sites added or dropped), rebuild from data; never patch numbers in prose.
