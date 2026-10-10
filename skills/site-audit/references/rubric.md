# Benchmark rubric v2.1

Read this before scoring anything. Totals are computed by `scripts/score.py`; never total by hand.

## How scoring works

1. Every criterion gets a **raw score from 0 to 10**.
   - **Ladder criteria** (A, B, C, E, H, I) take only the anchor values 0, 2, 4, 6, 8, 10. When a site sits between two anchors, take the lower one and say why in the proof note.
   - **Additive criteria** (D, F, G) sum the listed points, any whole number 0 to 10.
2. Each site type assigns **weights** that sum to 100. Weighted score = raw / 10 x weight.
3. **N/A** applies only for the reasons listed under a criterion. Record it as `"raw": null, "na": "reason"`. Its weight is redistributed proportionally across the scored criteria and it does not hurt coverage.
4. **Unscored** means the criterion applies but you lack proof. Record `"raw": null` with no `na`. Its weight is also redistributed, but it lowers **coverage** (share of applicable weight actually scored). Coverage below 80% marks the total *provisional*.
5. Every raw score needs a proof note in `"proof"`: a quoted line, a URL, or a date. No proof, no score. `score.py` rejects scores without proof.

Bands: **80+** benchmark met; **65 to 79** adequate; **55 to 64** at risk; **below 55** high risk.

State in every report: the rubric is this skill's own, derived from published search and publisher policy; scores measure exposure under those policies, not traffic, rankings or penalties.

## Site-type weights

Pick one type per site at intake. Mixed sites (a SaaS with a news blog) take the type of the pages being audited.

| Code | Criterion | event | publisher | local | ecommerce | b2b |
|---|---|---|---|---|---|---|
| A | Duplication and story governance | 15 | 18 | 5 | 10 | 10 |
| B | Added value beyond the source | 12 | 15 | 5 | 10 | 12 |
| C | Source transparency | 12 | 15 | 5 | 5 | 10 |
| D | Ownership and trust signals | 13 | 14 | 20 | 15 | 15 |
| E | Topic and audience fit | 10 | 8 | 10 | 10 | 12 |
| F | Technical hygiene | 10 | 8 | 15 | 20 | 12 |
| G | AI answer (AEO) readiness | 10 | 10 | 15 | 10 | 12 |
| H | Publishing consistency | 10 | 7 | 5 | 5 | 7 |
| I | Performance and mobile UX | 8 | 5 | 20 | 15 | 10 |

The same table lives in `scripts/score.py`. Change both together.

## Ladders

### A. Duplication and story governance (ladder)
- 10: no confirmed duplicate across the audited sites or against external copies
- 8: one confirmed cluster, already canonicalised, removed, or older than 90 days
- 6: one live confirmed cluster
- 4: two live confirmed clusters
- 2: three or four live clusters
- 0: five or more, or a systematic pattern (same piece reposted across domains as routine)

Confirmed means facts match on reading both pieces (`modes.md`, Dupes). Legitimate follow-ups are cleared, not counted.
N/A: fewer than five content pages on the site and no sibling sites.

### B. Added value beyond the source (ladder)
- 10: original reporting, data, testing, or named expert input in most sampled pieces
- 8: adds an independent source or dataset beyond the originating announcement
- 6: single-source rewrite with real framing or context of its own; Distance overlap under 25%
- 4: single-source rewrite in close phrasing; Distance overlap 25% to 50%
- 2: late or unsupported copy, or claims not traceable to any source
- 0: near-verbatim reproduction; Distance overlap above 50%

Use `scripts/distance.py` whenever source and article text are available verbatim. Without it, cap B at 6 and say so.
N/A: the site publishes no editorial or informational content (pure product catalogue, brochure site).

### C. Source transparency (ladder)
- 10: primary source linked and an independent source linked
- 8: primary source linked
- 6: primary source named without a link, plus an independent source named
- 4: primary source named without a link
- 2: quotes or figures used, no source named
- 0: claims with nothing attributed

N/A: same as B.

### D. Ownership and trust signals (additive, max 10)
- date visible on content pages, or an updated date on service pages: 1
- byline with a real name on content (or a named owner or practitioner on a local or service site): 2
- author page or bio, or team page: 1
- About page naming the owning organisation: 2
- full contact: physical address or phone, plus email or form: 2
- editorial policy, or for commerce a returns, shipping and privacy set: 1
- owner, organiser or registered business name stated on the page itself: 1

Never N/A.

### E. Topic and audience fit (ladder)
- 10: every sampled page on topic, in region, for the stated audience
- 8: one sampled page drifts in angle or region
- 6: noticeable drift across samples
- 4: mostly off topic, or no local angle where the site promises one
- 2: promotes competitors or unrelated offers
- 0: content contradicts the site's stated purpose

Never N/A.

### F. Technical hygiene (additive, max 10)
- self-referencing canonical on sampled pages: 2
- XML sitemap reachable and referenced from robots.txt or the root: 2
- `lastmod` present and plausible in the sitemap: 1
- HTTPS everywhere with at most one redirect hop from the bare domain: 1
- one H1 per page and clean titles (no stale years, no duplicates across samples): 2
- meta descriptions present on sampled pages: 1
- no 404 on clean URLs, no future-dated posts, no malformed slugs (trailing hyphen, `-1` copies): 1

Never N/A.

### G. AI answer (AEO) readiness (additive, max 10)
- search and retrieval bots allowed (Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User): 3, minus 1 per blocked bot, floor 0. Use `scripts/robots_check.py`. If the fetch tool was refused by robots rules and robots.txt text is unavailable, score 2 provisionally and say why. Blocking training-only bots (GPTBot, ClaudeBot, CCBot, Google-Extended, Applebot-Extended, meta-externalagent) is a legitimate business choice: note it, never deduct
- **entity clarity** (from the brand collision check in `modes.md`): 2 when the brand query returns the site first and no namesake competes; 1 when namesakes exist but the site carries separating signals (city or category in the title, schema address, sameAs to its own profiles); 0 when a namesake dominates the brand query and the site carries no separating signals
- structured data present **and verified** against visible text from page source (Article, Organization, LocalBusiness, Product as fits the type): 2. Organization schema carrying only a name: 1. Present but unverified: 0, marked "Not verified"
- key pages indexable and dated: 1
- entity-first titles and an answer-first opening paragraph: 1
- material claims linked or carrying citable figures: 1

Never N/A.

### H. Publishing consistency (ladder)
Use the cadence the site states or the user gives (daily means working days). Interval = one cadence period.
- 10: latest post within 1 interval
- 8: within 2 intervals
- 6: within 4 intervals
- 4: within 8 intervals
- 2: within 16 intervals
- 0: older, or the latest item is future-dated

Read dates on the listing and the article, never the homepage block alone.
N/A: no publishing section and no stated cadence (most local and catalogue sites).

### I. Performance and mobile UX (ladder)
Use PageSpeed Insights mobile, homepage plus one content page; take the lower.
- 10: performance 90+ and field Core Web Vitals pass
- 8: performance 90+ or field CWV pass
- 6: performance 70 to 89
- 4: performance 50 to 69
- 2: performance 30 to 49
- 0: below 30, or the page is not usable on mobile

When no field data exists, score on lab data and say "lab only". When PageSpeed cannot be reached, ask the user to paste the number; until then I is unscored.

## Projection

List template fixes in the data file under `"fixes"` with the expected raw change per criterion (`{"criterion": "D", "to": 8, "fix": "add bylines and author pages"}`). `score.py` prints current and projected totals. Project only fixes the site owner controls.

## Changes in v2.1
G now scores entity clarity (2 points) from the brand collision check, after a live run showed a namesake agency in another country owning the brand query. Indexable pages and entity-first titles dropped from 2 to 1 each to make room. Name-only Organization schema earns 1. v2 and v2.1 totals differ only through G.

## Changes from v1
Fixed 0 to 10 ladders replace improvised scales; site-type weights replace the event-network default; criterion I added; D generalised from news transparency to ownership and trust; N/A and coverage handling added; training-only bot blocks no longer cost points.
