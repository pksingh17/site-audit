# Policy reading list

Re-fetch every page you cite, every run; policies change. Record each page's "Last updated" date in the data file under `"policies"` and quote only lines you read this run. Never rely on remembered wording.

## Google Search
- Spam policies (scaled content abuse, scraping, doorways, link spam, site reputation abuse, expired domain abuse): https://developers.google.com/search/docs/essentials/spam-policies
- Helpful, reliable, people-first content (copying or rewriting sources, many sites, search-engine-first signals, who/how/why): https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Using generative AI content: https://developers.google.com/search/docs/fundamentals/using-gen-ai-content
- Consolidate duplicate URLs (canonicals; does not cover cross-domain canonicals in depth): https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- robots.txt introduction and Google crawlers list: https://developers.google.com/search/docs/crawling-indexing/robots/intro and https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers
- Large-site crawl budget: https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget
- AI features and your website: https://developers.google.com/search/docs/appearance/ai-features
- Structured data: Article https://developers.google.com/search/docs/appearance/structured-data/article ; Organization https://developers.google.com/search/docs/appearance/structured-data/organization ; LocalBusiness https://developers.google.com/search/docs/appearance/structured-data/local-business ; Product https://developers.google.com/search/docs/appearance/structured-data/product
- Core Web Vitals and page experience: https://developers.google.com/search/docs/appearance/core-web-vitals
- Google Discover: https://developers.google.com/search/docs/appearance/google-discover
- Google News publisher policies (dates, bylines, publisher transparency, contact): https://support.google.com/news/publisher-center/answer/6204050
- Google Business Profile guidelines (local): https://support.google.com/business/answer/3038177

## AI answer engines
- OpenAI crawlers (GPTBot training, OAI-SearchBot search, ChatGPT-User retrieval): https://platform.openai.com/docs/bots
- OpenAI publisher FAQ: https://help.openai.com/en/articles/12627856-publishers-and-developers-faq
- Anthropic crawlers (ClaudeBot, Claude-SearchBot, Claude-User): search "Anthropic crawler user agents" on support.claude.com
- Perplexity crawlers (PerplexityBot, Perplexity-User): https://docs.perplexity.ai/guides/bots
- Bing Webmaster guidelines and AI performance reporting: https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a ; search the Bing Webmaster blog for the latest AI post

## Bot classes used by `robots_check.py`
- Search and retrieval (blocking costs G points): Googlebot, Bingbot, OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User
- Training only (note, no deduction): GPTBot, ClaudeBot, CCBot, Google-Extended, Applebot-Extended, meta-externalagent, Bytespider

If a vendor renames or adds a bot, update this list and the `SEARCH_BOTS` and `TRAINING_BOTS` lists in `scripts/robots_check.py` together, and note it in the report's limits.

## Citation rules
- Cite the policy URL, the last-updated date and one short quoted line per point.
- Practitioner blogs, plugin documentation and ranking-factor theories are not evidence. Use them only as hypotheses, labelled as such.
