#!/usr/bin/env python3
"""Read real page source for the site-audit skill.

Usage:
  python3 fetch_source.py URL [URL ...] [--psi] [--psi-key KEY] [--json]
  python3 fetch_source.py --file home.html --base https://example.com/ [--json]

Extracts what a summarising fetch tool cannot verify: title, meta description,
meta robots, canonical (and whether it is self-referencing), H1s, hreflang,
Open Graph, JSON-LD (types, name, address, telephone, areaServed, sameAs,
author, dates), tel and mailto links, word count, internal and external link
counts, images missing alt, and the redirect chain (URL mode only).
--psi adds PageSpeed Insights mobile performance and Core Web Vitals.
--file parses pasted source (Ctrl+U, copy all) when direct fetching fails.
Needs beautifulsoup4; requests for URL mode.
"""
import argparse
import json
import sys
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("pip install beautifulsoup4 (add --break-system-packages if needed)")

UA = "Mozilla/5.0 (compatible; site-audit/2.1; +evidence-first audit)"


def walk_ld(node, out):
    if isinstance(node, list):
        for n in node:
            walk_ld(n, out)
    elif isinstance(node, dict):
        if "@graph" in node:
            walk_ld(node["@graph"], out)
        if "@type" in node:
            out.append(node)  # nested objects (author, address) stay inside their parent


def summarise_ld(items):
    keep = ("name", "url", "telephone", "email", "address", "areaServed", "sameAs", "author",
            "publisher", "datePublished", "dateModified", "headline", "logo", "priceRange", "geo")
    res = []
    for it in items:
        t = it.get("@type")
        row = {"@type": t}
        for k in keep:
            if k in it:
                v = it[k]
                if isinstance(v, dict):
                    v = {kk: vv for kk, vv in v.items() if kk in ("@type", "name", "streetAddress", "addressLocality",
                                                                  "addressRegion", "postalCode", "addressCountry", "url")}
                row[k] = v
        res.append(row)
    return res


def parse_html(html, base):
    soup = BeautifulSoup(html, "html.parser")
    host = urlparse(base).netloc.lower().removeprefix("www.")

    def meta(name=None, prop=None):
        tag = soup.find("meta", attrs={"name": name}) if name else soup.find("meta", attrs={"property": prop})
        return tag.get("content", "").strip() if tag else None

    canon_tag = soup.find("link", rel=lambda v: v and "canonical" in (v if isinstance(v, list) else [v]))
    canonical = urljoin(base, canon_tag["href"]) if canon_tag and canon_tag.get("href") else None
    ld_raw, ld_errors = [], 0
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            walk_ld(json.loads(s.string or s.get_text() or ""), ld_raw)
        except Exception:
            ld_errors += 1
    links = [urljoin(base, a.get("href", "")) for a in soup.find_all("a", href=True)]
    tel = sorted({l for l in links if l.startswith("tel:")})
    mail = sorted({l for l in links if l.startswith("mailto:")})
    web = [l for l in links if l.startswith("http")]
    internal = [l for l in web if urlparse(l).netloc.lower().removeprefix("www.") == host]
    external = [l for l in web if l not in internal]
    imgs = soup.find_all("img")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    text = " ".join(soup.get_text(" ").split())
    title = soup.title.get_text(strip=True) if soup.title else None
    norm = lambda u: (u or "").rstrip("/").replace("://www.", "://").split("#")[0]
    return {
        "title": title,
        "title_length": len(title) if title else 0,
        "meta_description": meta(name="description"),
        "meta_robots": meta(name="robots"),
        "canonical": canonical,
        "canonical_self": bool(canonical) and norm(canonical) == norm(base),
        "h1": [h.get_text(" ", strip=True) for h in BeautifulSoup(html, "html.parser").find_all("h1")],
        "hreflang": [{"lang": l.get("hreflang"), "href": l.get("href")} for l in
                     BeautifulSoup(html, "html.parser").find_all("link", hreflang=True)],
        "og": {p: meta(prop=p) for p in ("og:title", "og:type", "og:url", "og:site_name") if meta(prop=p)},
        "jsonld": summarise_ld(ld_raw),
        "jsonld_types": sorted({str(x.get("@type")) for x in ld_raw}),
        "jsonld_parse_errors": ld_errors,
        "tel_links": tel,
        "mailto_links": mail,
        "word_count": len(text.split()),
        "links_internal": len(internal),
        "links_external": len(external),
        "external_sample": sorted(set(external))[:15],
        "images": len(imgs),
        "images_missing_alt": sum(1 for i in imgs if not (i.get("alt") or "").strip()),
    }


def fetch(url):
    import requests
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30, allow_redirects=True)
    chain = [{"url": h.url, "status": h.status_code} for h in r.history] + [{"url": r.url, "status": r.status_code}]
    return r, chain


def psi(url, key=None):
    import requests
    params = {"url": url, "strategy": "mobile", "category": "performance"}
    if key:
        params["key"] = key
    r = requests.get("https://www.googleapis.com/pagespeedonline/v5/runPagespeed", params=params, timeout=120)
    if r.status_code != 200:
        return {"error": f"HTTP {r.status_code}: {r.text[:200]}"}
    d = r.json()
    lh = d.get("lighthouseResult", {})
    perf = lh.get("categories", {}).get("performance", {}).get("score")
    fld = d.get("loadingExperience", {})
    m = fld.get("metrics", {})
    return {
        "performance": round(perf * 100) if perf is not None else None,
        "field_data": bool(m),
        "field_overall": fld.get("overall_category"),
        "lcp_ms": m.get("LARGEST_CONTENTFUL_PAINT_MS", {}).get("percentile"),
        "cls_x100": m.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {}).get("percentile"),
        "inp_ms": m.get("INTERACTION_TO_NEXT_PAINT", {}).get("percentile"),
        "lab_lcp": lh.get("audits", {}).get("largest-contentful-paint", {}).get("displayValue"),
    }


def show(res):
    for k, v in res.items():
        if v in (None, [], {}, ""):
            v = "none"
        print(f"{k:20} {json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file", help="saved or pasted page source")
    ap.add_argument("--base", help="page URL for --file (resolves links and canonical)")
    ap.add_argument("--psi", action="store_true")
    ap.add_argument("--psi-key")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    results = []
    if a.file:
        if not a.base:
            ap.error("--file needs --base https://domain/page")
        html = open(a.file, encoding="utf-8", errors="replace").read()
        res = {"source": "pasted", "url": a.base, **parse_html(html, a.base)}
        if a.psi:
            try:
                res["pagespeed"] = psi(a.base, a.psi_key)
            except Exception as e:
                res["pagespeed"] = {"error": str(e)}
        results.append(res)
    for url in a.urls:
        url = url if url.startswith("http") else "https://" + url
        try:
            r, chain = fetch(url)
        except Exception as e:
            results.append({"url": url, "error": f"{type(e).__name__}: {e}",
                            "next": "network refused: use the fallback ladder in references/fetching.md"})
            continue
        res = {"source": "live", "url": url, "final_url": r.url, "status": r.status_code,
               "redirect_hops": len(chain) - 1, "redirect_chain": chain,
               "x_robots_tag": r.headers.get("X-Robots-Tag")}
        if r.status_code in (401, 403, 429, 503):
            res["note"] = "blocked or challenged; record as a finding and use the fallback ladder"
        if "html" in r.headers.get("Content-Type", "html"):
            res.update(parse_html(r.text, r.url))
        if a.psi:
            try:
                res["pagespeed"] = psi(url, a.psi_key)
            except Exception as e:
                res["pagespeed"] = {"error": str(e)}
        results.append(res)
    if not results:
        ap.error("give a URL or --file")
    if a.json:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2, ensure_ascii=False))
    else:
        for res in results:
            print("=" * 70)
            show(res)


if __name__ == "__main__":
    main()
