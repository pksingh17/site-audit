# site-audit

Evidence-first website audits for Claude: SEO, AI-answer (AEO) readiness and content risk, for one site or a whole network of sites.

Every score, finding and claim carries proof: a quoted line, a URL, a date. If there's no proof, there's no score. Free sources come first. Paid SEO tools (Ahrefs, Semrush) are optional add-ons, never a requirement.

## What it does

| Mode | Use it for | Output |
|---|---|---|
| Quick | A fast health check of one site, or a free sample for a prospective client | Chat reply: provisional score, top 3 risks, top 3 fixes |
| Audit | Gathering evidence across a list of sites | Per-site evidence file |
| Dupes | Duplicate stories across domains | Duplication register with proof |
| Benchmark | Scoring sites against the rubric | Totals, bands, coverage, projection, fix list |
| Delta | Progress since a previous audit | Band moves, fixes closed, like-for-like change |
| Verify | Checking the sources in someone else's SEO report | Source table and unsupported-claims list |
| Roster | Reconciling a sheet of sites and owners with the live sites | Conflicts and workload |
| Peer | Benchmarking against competitors | Client vs peer medians |
| Panel | Tracking AI-answer citations over time | Prompt panel and results log |
| Distance | Measuring how closely an article rewrites its source | Shingle overlap, untraceable figures |
| Drive | Pre-publication checks on drafts in Google Drive | Duplicate and source-link flags |
| Handoff | Turning gaps into briefs for a blog-writing skill | Content-gap brief |

A plain request like "audit this site" runs Quick and offers the full audit.

## The rubric (v2.1)

There are nine criteria, each scored 0 to 10 against fixed anchors and weighted by site type (event, publisher, local, ecommerce, b2b):

A. Duplication and story governance, B. Added value beyond the source, C. Source transparency, D. Ownership and trust signals, E. Topic and audience fit, F. Technical hygiene, G. AI answer (AEO) readiness, H. Publishing consistency, I. Performance and mobile UX.

- **N/A is allowed only where the rubric says so.** Its weight is redistributed.
- **Unscored criteria lower coverage.** Below 80% coverage, a total is marked provisional.
- **Blocking training-only bots** (GPTBot, CCBot, Google-Extended and similar) is noted but costs nothing. Blocking search and retrieval bots does cost points.
- **The brand collision check** runs first. It detects a namesake business that owns your brand query and scores entity clarity under G.

Scores measure exposure under published search and publisher policy. They don't measure traffic, rankings or penalties. The full ladders are in [`skills/site-audit/references/rubric.md`](skills/site-audit/references/rubric.md).

## Bundled scripts

All scripts sit in `skills/site-audit/scripts/` and each takes `--help`.

| Script | Job |
|---|---|
| `score.py` | Validates every score (ladder anchors, proof, N/A rules) and computes totals, coverage, bands, medians and projection. Exits 1 on any problem |
| `delta.py` | Compares two scored runs. Reports a like-for-like change when coverage shifts |
| `distance.py` | Rewrite distance between a source and an article, plus figures and names the source never mentions |
| `robots_check.py` | Bot-by-bot robots.txt verdicts and G bot points, from a file or a URL |
| `fetch_source.py` | Reads real page source (canonical, H1s, JSON-LD, contact links, redirects) and PageSpeed. Use `--file` for pasted source when fetching is blocked |
| `build_report.py` | Builds the client PDF from scored data. Has an optional dash ban |
| `qa_pdf.py` | Checks the PDF: blank pages, dash count, every total present, page images |

Requirements: Python 3.9+. `fetch_source.py` needs `beautifulsoup4` and `requests`. The PDF scripts need `reportlab` and `pypdf`.

## Install

**Claude Code**
```
/plugin marketplace add pksingh17/site-audit
/plugin install site-audit@site-audit
```

**Claude apps (web, desktop)**

Download the `.skill` file from the latest release, or zip `skills/site-audit/`, then upload it in your skills settings.

## Test

```
bash tests/run_tests.sh
```

The tests run every script against the files in `examples/`, including deliberately broken scores the scorer must catch.

## Changelog

- **2.1.0**: Added the fetch fallback ladder (search index, pasted robots.txt, pasted page source), `robots_check.py`, the brand collision check and the entity-clarity points under G. Delta now reports a like-for-like change when coverage shifts.
- **2.0.0**: Split the skill into a router plus references. Added fixed 0 to 10 ladders, site-type weights, criterion I, N/A and coverage handling, and the Quick, Delta and Handoff modes. Bundled scripts.
- **1.0.0**: First release, built around an event-network audit.

## License

MIT, © 2026 Prabhakar Singh
