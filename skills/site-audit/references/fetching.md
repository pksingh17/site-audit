# Fetching: tools, traps and fallbacks

Tool names are generic, so the skill runs the same in Claude, ChatGPT and Codex: "the fetch tool" is whatever reads a web page in this session (WebFetch in Claude, web browsing in ChatGPT, a browser or fetch connector); "search" is the web search tool; "the shell" is a code sandbox (Claude code execution, ChatGPT's Python tool, a Codex or Claude Code terminal, a linked desktop).

## Order of preference
1. **Shell fetch** with `scripts/fetch_source.py URL` when the shell has open network. Real HTML: canonical, meta robots, H1s, hreflang, OG tags, JSON-LD, redirect chain, contact links. This is the only route that verifies structured data.
2. **The fetch tool** for reading content, dates and bylines.
3. **Search** for indexed titles (`site:` queries), brand collision, and copies on other domains.
4. **Pasted material** from the user (see the fallback ladder).

Many sandboxes route the shell through an allowlist. If a shell request is refused, do not retry with another command or a mirror. Note it once and use the next route.

## The summarising trap
The fetch tool passes pages through a small model. It has miscounted days, missed paragraphs and paraphrased quotes. So:
- Ask for verbatim quotes, first and last paragraphs, dates exactly as displayed, and explicit "none" answers ("byline: none", "outbound links in body: none").
- Before any finding enters a deliverable, confirm it with a **second, narrow fetch** asking only for the verbatim line.
- Never compute Distance on fetch-tool paraphrase.

## Reading traps
- Homepage news blocks lag. Use the listing page for recency and the article page for the date. Never call a site stale from its homepage.
- Listing pages pin old items. Read every date; do not trust order.
- Canonicals often appear in fetch metadata; record them when shown.
- A clean URL that returns 404 while a `-1` slug works means a publishing fault; record both URLs.

## robots.txt
Fetch it with the shell when possible and run `python3 scripts/robots_check.py robots.txt` (or `--url DOMAIN`). The script gives a verdict per bot, separates search and retrieval bots from training-only bots, and lists Sitemap lines.
If only the fetch tool works, verbatim reproduction may be refused. Ask instead: "For each of these user-agents, is it disallowed from the whole site: Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, GPTBot, Claude-SearchBot, Claude-User, ClaudeBot, PerplexityBot, Perplexity-User, Google-Extended, Applebot-Extended, CCBot? List every user-agent named. Sitemap lines?"

## When the fetch tool is refused
A refusal citing robots rules (or a 403 to the fetcher) is itself evidence: at least one AI retrieval agent is blocked. Record `"fetch_blocked": true` for the site and a finding with the error text. Then, in order:
1. **Search-index fallback.** Search the bare domain and "brand name + domain". Snippets often carry the indexed title, meta description and a slice of content. Use them, labelled "from search index, not live page".
2. **Robots text.** Ask the user to open `DOMAIN/robots.txt` in a browser and paste it. Save it and run `python3 scripts/robots_check.py robots.txt`. This shows whether the block is a named-bot rule or a blanket one.
3. **Page source.** Ask the user to open the homepage (and one content page), press Ctrl+U (Cmd+Option+U on Mac), copy all, and paste or attach it. Save as `home.html` and run `python3 scripts/fetch_source.py --file home.html --base https://DOMAIN/`. This verifies schema, canonical, H1s and contact links.
4. **PageSpeed.** Ask for the mobile performance number from pagespeed.web.dev if the shell cannot call the API.
5. **Shell fetch**, if network allows, as a last check.

Whatever stays unread stays unscored. Say which criteria are waiting on which paste, so the user can unblock them in one message.

## PageSpeed
`python3 scripts/fetch_source.py URL --psi` calls the free PageSpeed Insights API (no key needed at low volume; pass `--psi-key` if rate limited). It returns mobile performance, LCP, CLS, INP and whether field data exists.

## Free authoritative sources (prefer over paid estimates)
- Google Search Console and Bing Webmaster Tools exports from the owner: indexed vs submitted pages, Google-selected canonical, queries, AI-feature performance. Most authoritative source for the owner's own site.
- PageSpeed Insights API: Core Web Vitals.
- Wayback Machine (`web.archive.org/web/*/URL`): first-capture dates, which settle "who published first" in Dupes.
- Ahrefs free domain rating endpoint, where the connector offers it without a plan.

## Paid add-ons (optional)
Test access with one cheap call. On any plan, unit or subscription error, tell the user in one line and continue without it. Label third-party traffic and keyword numbers as estimates.
- Ahrefs: organic keywords, backlinks, site audit issues, Brand Radar for AI citations and share of voice.
- Semrush: domain overview, traffic, keyword gap, site audit.

## Cost
Quick: about 5 fetches. Audit: 3 to 5 per site, plus template checks once per network. Batch above 40 sites and tell the user.
