#!/usr/bin/env bash
# Runs every bundled script against the files in examples/ and checks the results.
# Usage: bash tests/run_tests.sh   (from the repo root)
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
S="$ROOT/skills/site-audit/scripts"
E="$ROOT/examples"
W="$(mktemp -d)"
trap 'rm -rf "$W"' EXIT
pass=0; fail=0
check() { if eval "$2"; then echo "PASS  $1"; pass=$((pass+1)); else echo "FAIL  $1"; fail=$((fail+1)); fi; }

python3 "$S/score.py" "$E/data_with_errors.json" --out "$W/bad.json" > "$W/score.out" 2>&1
rc=$?
check "score.py exits 1 on planted errors"      '[ "$rc" -eq 1 ] && grep -q "4 PROBLEM" "$W/score.out"'
check "score.py catches off-ladder value"       'grep -q "off-ladder" "$W/score.out"'
check "score.py catches out-of-range additive"  'grep -q "outside 0..10" "$W/score.out"'
check "score.py enforces no proof, no score"    'grep -q "no proof note" "$W/score.out"'
check "score.py rejects invalid N/A"            'grep -q "N/A not allowed" "$W/score.out"'
check "score.py total alpha-summit = 60.9"      'grep -q "alpha-summit.com.*60.9" "$W/score.out"'

python3 "$S/score.py" "$E/delta_old.json" --out "$W/old.json" > /dev/null
python3 "$S/score.py" "$E/delta_new.json" --out "$W/new.json" > /dev/null
python3 "$S/delta.py" "$W/old.json" "$W/new.json" --out "$W/delta.json" > "$W/delta.out"
check "delta.py marks fix closed"               'grep -q "closed: add bylines" "$W/delta.out"'
check "delta.py reports like-for-like on coverage change" 'grep -q "like-for-like change +0.0" "$W/delta.out"'

python3 "$S/distance.py" "$E/distance_source.txt" "$E/distance_article.txt" > "$W/dist.out"
check "distance.py finds untraceable figure"    'grep -q "30,000 tonnes" "$W/dist.out"'
check "distance.py finds invented firm"         'grep -q "Meridian Capital" "$W/dist.out"'

python3 "$S/robots_check.py" "$E/robots.txt" > "$W/robots.out"
check "robots_check.py deducts Claude-User block" 'grep -q "G bot points: 2 / 3" "$W/robots.out"'
check "robots_check.py does not deduct GPTBot"  'grep -q "training blocks noted.*GPTBot" "$W/robots.out"'

python3 "$S/fetch_source.py" --file "$E/pasted_source.html" --base https://bluepanda.example/ --json > "$W/src.json"
check "fetch_source.py reads LocalBusiness schema" 'grep -q "LocalBusiness" "$W/src.json"'
check "fetch_source.py counts two H1s"          'python3 -c "import json,sys; sys.exit(0 if len(json.load(open(\"$W/src.json\"))[\"h1\"])==2 else 1)"'
check "fetch_source.py flags broken JSON-LD"    'grep -q "\"jsonld_parse_errors\": 1" "$W/src.json"'

if python3 -c "import reportlab, pypdf" 2>/dev/null; then
  python3 "$S/build_report.py" "$W/new.json" "$E/report.json" --out "$W/r.pdf" > /dev/null
  python3 "$S/qa_pdf.py" "$W/r.pdf" --scored "$W/new.json" --ban-dashes > "$W/qa.out"
  check "build_report.py + qa_pdf.py pass with dash ban" 'grep -q "^PASS" "$W/qa.out"'
else
  echo "SKIP  PDF tests (pip install reportlab pypdf)"
fi

echo; echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
