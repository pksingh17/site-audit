#!/usr/bin/env python3
"""Bot-by-bot robots.txt verdicts for the site-audit rubric (criterion G).

Usage:
  python3 robots_check.py robots.txt            # pasted or saved text
  python3 robots_check.py --url example.com     # fetch, if the shell has network
  add --json for machine output

For each search/retrieval bot and each training-only bot, finds the group that
applies (most specific user-agent match, else '*') and reports: allowed,
partial (some paths disallowed) or blocked (whole site). Computes the G bot
points: 3 minus 1 per blocked search/retrieval bot, floor 0. Training-only
blocks are noted, never deducted. Lists Sitemap lines.
"""
import argparse
import json
import sys
import urllib.request

SEARCH_BOTS = ["Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot",
               "Claude-User", "PerplexityBot", "Perplexity-User"]
TRAINING_BOTS = ["GPTBot", "ClaudeBot", "CCBot", "Google-Extended", "Applebot-Extended",
                 "meta-externalagent", "Bytespider"]


def parse(text):
    groups, sitemaps = [], []
    cur, last_was_ua = None, False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip().lower(), val.strip()
        if key == "user-agent":
            if cur is None or not last_was_ua:
                cur = {"agents": [], "rules": []}
                groups.append(cur)
            cur["agents"].append(val.lower())
            last_was_ua = True
        elif key in ("allow", "disallow"):
            if cur is None:
                cur = {"agents": ["*"], "rules": []}
                groups.append(cur)
            cur["rules"].append((key, val))
            last_was_ua = False
        elif key == "sitemap":
            sitemaps.append(val)
            last_was_ua = False
        else:
            last_was_ua = False
    return groups, sitemaps


def group_for(bot, groups):
    b = bot.lower()
    exact = [g for g in groups if b in g["agents"]]
    if exact:
        rules = [r for g in exact for r in g["rules"]]
        return rules, bot
    star = [g for g in groups if "*" in g["agents"]]
    if star:
        return [r for g in star for r in g["rules"]], "*"
    return [], None


def verdict(rules):
    dis = [v for k, v in rules if k == "disallow" and v]
    allow = [v for k, v in rules if k == "allow" and v]
    if "/" in dis or "/*" in dis:
        if any(a in ("/", "/*") for a in allow):
            return "allowed", dis
        return "blocked", dis
    if dis:
        return "partial", dis
    return "allowed", []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--url")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.url:
        u = a.url if a.url.startswith("http") else "https://" + a.url
        u = u.rstrip("/") + "/robots.txt" if not u.endswith("robots.txt") else u
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 site-audit robots check"})
            text = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
        except Exception as e:
            print(f"Could not fetch {u}: {e}. Ask the user to paste robots.txt and run with a file.")
            sys.exit(2)
    elif a.file:
        text = open(a.file, encoding="utf-8", errors="replace").read()
    else:
        ap.error("give a robots.txt file or --url")

    groups, sitemaps = parse(text)
    res = {"search": [], "training": [], "sitemaps": sitemaps, "named_agents": sorted({ag for g in groups for ag in g["agents"]})}
    for cls, bots in (("search", SEARCH_BOTS), ("training", TRAINING_BOTS)):
        for bot in bots:
            rules, via = group_for(bot, groups)
            v, paths = verdict(rules)
            res[cls].append({"bot": bot, "verdict": v, "via": via or "(no rules)", "disallowed": paths[:10]})
    blocked_search = [r["bot"] for r in res["search"] if r["verdict"] == "blocked"]
    res["blocked_search"] = blocked_search
    res["blocked_training"] = [r["bot"] for r in res["training"] if r["verdict"] == "blocked"]
    res["g_bot_points"] = max(0, 3 - len(blocked_search))

    if a.json:
        print(json.dumps(res, indent=2))
        return
    print("SEARCH AND RETRIEVAL BOTS (only 'blocked' costs G points; 'partial' is path-level, usually admin areas, and costs nothing)")
    for r in res["search"]:
        extra = f"  [{', '.join(r['disallowed'])}]" if r["verdict"] == "partial" else ""
        print(f"  {r['bot']:18} {r['verdict']:8} via {r['via']}{extra}")
    print("TRAINING-ONLY BOTS (note only, no deduction)")
    for r in res["training"]:
        print(f"  {r['bot']:18} {r['verdict']:8} via {r['via']}")
    print(f"\nG bot points: {res['g_bot_points']} / 3" + (f"  (blocked: {', '.join(blocked_search)})" if blocked_search else ""))
    if res["blocked_training"]:
        print("training blocks noted (legitimate business choice): " + ", ".join(res["blocked_training"]))
    print("user-agents named: " + ", ".join(res["named_agents"]))
    print("sitemaps: " + (", ".join(sitemaps) if sitemaps else "none declared"))


if __name__ == "__main__":
    main()
