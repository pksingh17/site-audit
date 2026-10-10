# Mode procedures

Read only the section for the mode you are running, plus the brand collision check for Quick, Audit and Peer.

## Brand collision check (step zero: Quick, Audit, Peer)
Run three searches per site: the brand name alone; brand plus city or region; brand plus category ("Blue Panda digital marketing"). For each result page:
1. List every business sharing or closely resembling the name, with its domain, location and what it does.
2. Rate each namesake: **dominant** (owns page one, or most of it, possibly with a syndication or directory network), **present** (one or two page-one results), **minor** (page two or beyond).
3. Check whether the audited site carries separating signals: city or category in the homepage title, a schema address or areaServed, sameAs links to its own Google Business Profile and social profiles, a distinct About page.
4. Record in the data file under `"brand_collision"`: queries, namesakes with ratings, separating signals present. This feeds G's entity-clarity points.

When a namesake is dominant, the top fixes are: add city and category to the title and H1; publish LocalBusiness or Organization schema with address, areaServed and sameAs; claim and complete the Google Business Profile; build a few citations that pair the brand with the city. Say plainly that ranking for the bare brand name may not be realistic and that brand-plus-city is the target.

## Quick
A free-sample health check for one site, about five fetches, answered in chat.
1. Brand collision check (three searches).
2. Homepage: title, H1, contact, About link, owner named, date signals.
3. One content or service page: byline or owner, date, sources, opening paragraph.
4. robots.txt and sitemap (`robots_check.py`), PageSpeed if the shell allows.
5. Score every criterion you have proof for with `score.py`. Most Quick runs are provisional; say so.

Reply format: one-line verdict with provisional score and band; coverage; **top 3 risks**, each with its proof line; **top 3 fixes**, each with the criterion it moves; what a full audit adds. Keep it under 300 words. Offer the full audit in one line.

## Audit
Copy `assets/data_template.json` to the working folder as `data.json`. Per site:
1. **Homepage:** name and key facts exactly as shown in the hero (dates and city for events; services and area for local; categories for ecommerce); contact; About page; owner or organiser named; footer links to sibling sites.
2. **Listing page** (news, blog, products): every item as `date | title | slug`; meta description; pagination.
3. **One content page** (two for large sites): byline, date, outbound links in body, sources named without links, word count, canonical, primary call to action, first and last paragraph verbatim, which original announcement it rests on, topic and region fit.
4. **Template checks**, once per network (sample three sites): robots.txt, sitemap (URL set or index, lastmod, news sitemap), indexed titles via `site:` searches, page source via `fetch_source.py` or paste.

Watch for: future-dated posts, slugs ending in `-1` or a hyphen, clean URL returning 404, duplicate listing entries, stale years in titles, competitor promotion, closing paragraphs templated across sites.

Write every observation into `data.json` with its proof. Then confirm each finding with a second narrow fetch (`fetching.md`).

## Dupes
1. Put every headline from every listing page in one list.
2. Cluster by named entity (company, project, place), figure and a 30-day window.
3. For each candidate cluster, read every article and match companies, figures and dates. Confirmed only when facts match. A different development on the same topic is a legitimate follow-up: mark it cleared.
4. For who published first, use on-page dates, then Wayback first-capture dates.
5. Register per cluster: title, sites, owner or team, dates, headline and URL, proof quoting opening lines and shared figures, any unsupported claim copied between versions.
6. Search the story name plus the network's domains to catch copies on sites outside the list.

## Benchmark
1. Read `rubric.md`. Set each site's type.
2. Fill `raw`, `proof` and `na` per criterion in `data.json`.
3. Run `python3 scripts/score.py data.json --out scored.json`. Fix every warning it prints (off-ladder value, missing proof, invalid N/A) before using the numbers.
4. Report totals, bands, coverage, network median, and projection from `fixes`.
5. Group by site by default; by owner or team only if the user asked. Frame as process load.
6. Fix list: network-level items first (for web and editorial leads), then per site or owner.

## Delta
Needs an earlier `scored.json` (the user attaches it, or it is in their files).
1. Re-run Audit on the same sites and pages where possible; note pages that changed or vanished.
2. Score with the same rubric version. If the earlier run used v2, note that G moved in v2.1 and compare G separately.
3. Run `python3 scripts/delta.py old_scored.json new_scored.json`.
4. Report: band moves, criterion changes with proof, fixes closed, fixes still open, new issues. Lead with what improved; this is the retainer view.
5. When `delta.py` says coverage changed, report the like-for-like change as the real movement. A criterion scored for the first time can drag a headline total down without anything on the site getting worse; never present that as a decline.

## Verify
For each cited source, in the user's priority order: open it, record Exists, Date match (page date vs report date), Claim accurate (Yes, Partly, No), and quote the relevant line. Flag sources cited in an appendix but never in the body, mislabelled sources, and claims resting on the wrong source. If the report is a file, render its pages to images and check for orphaned citations, orphaned headings and blank pages. End with the list of claims no source supports.
If a report cites a Google blog post whose body will not extract, confirm it through two independent trade outlets quoting it, and say so.

## Roster
Load the sheet with openpyxl or pandas. Ask what codes and status labels mean before interpreting them. Parse dates, split codes, sort rows into live, concluded and cancelled using the user's vocabulary. Compare each live row with the site hero. Flag: date or city conflicts, sites showing TBC or a later year, codes listed twice, live rows missing from the audit list, concluded or cancelled entries still publishing. Report workload per owner and how it lines up with findings, framed as process load.

## Peer
Ask for 5 to 10 competitors, or the outlets the client sources from. Run the brand collision check, Audit (one listing page, two content pages each) and the rubric with the client's site type. Present the client against peer medians per criterion (`score.py` prints medians). Peers are scored on the same evidence standard; unscored peer criteria stay unscored.

## Panel
Build 15 to 20 real questions per vertical, phrased the way a buyer or reader asks. Give the user a log template: date, engine (ChatGPT, Perplexity, Gemini, Claude, Google AI Overview), prompt, cited domains, whether an audited site was cited, position. Repeat monthly. Answers vary by user and day; report trends only. Web search in this session is not Google and does not prove indexing.

## Distance
With source text and article text pasted or extracted verbatim (never fetch-tool paraphrase), run `python3 scripts/distance.py source.txt article.txt`. It reports 5-word shingle overlap (share of article 5-grams found in the source), entity and figure overlap, and figures in the article absent from the source. Report: "x% of article phrasing traceable to source; y figures not traceable." Use it to anchor B.

## Drive
If drafts live in a connected Drive, list today's folders, read drafts, run Dupes against the last 30 days of published headlines, and flag drafts with no source link. Read only; never edit their files unless asked.

## Handoff
Turn audit findings into a content-gap brief for the client-blog-generator skill. Per gap: target query or question (from Panel, Peer gaps, or search suggestions), page type (service page or blog), the evidence that the gap exists (competitor URL covering it, a question the site cannot answer), entities to cover, and internal pages to link. Save as `handoff.md`. Do not draft the content here.
