#!/usr/bin/env bash
# eval-ast-rules.sh — Deterministic evaluation of ast-grep rules against test codebases.
# Runs every rule against every repo and collects match counts into eval-results.json.
# The AUDIT step is done by the designer agent (see eval-audit.md), not this script.

set -euo pipefail

CONCEPTS_DIR="${CONCEPTS_DIR:-$(dirname "$0")/../../memory/concepts}"
RESULTS_FILE="${RESULTS_FILE:-$(dirname "$0")/eval-results.json}"

# Resolve to absolute paths
CONCEPTS_DIR="$(cd "$CONCEPTS_DIR" && pwd)"
RESULTS_FILE="$(cd "$(dirname "$RESULTS_FILE")" && pwd)/$(basename "$RESULTS_FILE")"

# Test codebases — add paths as they become available
REPOS=()
for candidate in \
    "$HOME/stoik" "$HOME/repos/stoik" "$HOME/test-repos/stoik" \
    "$HOME/sous-storefront" "$HOME/repos/sous-storefront" "$HOME/test-repos/sous-storefront" \
    "$HOME/kordinate" "$HOME/repos/kordinate" "$HOME/test-repos/kordinate" \
    "$HOME/logbd" "$HOME/repos/logbd" "$HOME/test-repos/logbd"; do
    if [[ -d "$candidate" ]]; then
        REPOS+=("$candidate")
    fi
done

if [[ ${#REPOS[@]} -eq 0 ]]; then
    echo "ERROR: No test codebases found. Expected at least one of: stoik, sous-storefront, kordinate, logbd"
    echo "Searched: ~/<name>, ~/repos/<name>, ~/test-repos/<name>"
    exit 1
fi

echo "=== ast-grep Rule Evaluation ==="
echo "Concepts dir: $CONCEPTS_DIR"
echo "Repos: ${REPOS[*]}"
echo "Output: $RESULTS_FILE"
echo ""

# Check for ast-grep
if ! command -v ast-grep &>/dev/null; then
    echo "ERROR: ast-grep not found. Install with: npm install -g @ast-grep/cli"
    exit 1
fi

# Collect all ast-grep rule files
RULE_FILES=()
while IFS= read -r -d '' f; do
    RULE_FILES+=("$f")
done < <(find "$CONCEPTS_DIR" -name 'ast-grep.yaml' -print0 | sort -z)

echo "Found ${#RULE_FILES[@]} ast-grep rule files"
echo "Found ${#REPOS[@]} test codebases"
echo ""

# Build JSON results
tmp_results=$(mktemp)
echo '{"meta":{},"results":[]}' > "$tmp_results"

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
repo_names=()
for repo in "${REPOS[@]}"; do
    repo_names+=("\"$(basename "$repo")\"")
done
repo_list=$(IFS=,; echo "${repo_names[*]}")

# Update meta
python3 -c "
import json, sys
d = json.load(open('$tmp_results'))
d['meta'] = {
    'timestamp': '$timestamp',
    'repos': [$(echo "$repo_list")],
    'rule_count': ${#RULE_FILES[@]},
    'repo_count': ${#REPOS[@]}
}
json.dump(d, open('$tmp_results', 'w'), indent=2)
"

total_rules=${#RULE_FILES[@]}
current=0

for rule_file in "${RULE_FILES[@]}"; do
    current=$((current + 1))
    concept=$(basename "$(dirname "$rule_file")")

    printf "[%d/%d] %-40s" "$current" "$total_rules" "$concept"

    repo_counts="{"
    total_matches=0
    first=true

    for repo in "${REPOS[@]}"; do
        repo_name=$(basename "$repo")

        # Run ast-grep and count matches (each match prints one line in JSON output)
        count=$(ast-grep scan --rule "$rule_file" "$repo" --json 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(len(data) if isinstance(data, list) else 0)
except:
    print(0)
" 2>/dev/null || echo "0")

        if [[ "$first" == "true" ]]; then
            first=false
        else
            repo_counts+=","
        fi
        repo_counts+="\"$repo_name\":$count"
        total_matches=$((total_matches + count))

        printf " %s=%d" "$repo_name" "$count"
    done

    repo_counts+="}"
    echo ""

    # Append result
    python3 -c "
import json
d = json.load(open('$tmp_results'))
d['results'].append({
    'concept': '$concept',
    'rule_file': '$rule_file',
    'total_matches': $total_matches,
    'by_repo': $repo_counts
})
json.dump(d, open('$tmp_results', 'w'), indent=2)
"
done

# Sort results by total_matches descending for easy review
python3 -c "
import json
d = json.load(open('$tmp_results'))
d['results'].sort(key=lambda r: r['total_matches'], reverse=True)
json.dump(d, open('$tmp_results', 'w'), indent=2)
"

mv "$tmp_results" "$RESULTS_FILE"

echo ""
echo "=== Summary ==="
python3 -c "
import json
d = json.load(open('$RESULTS_FILE'))
results = d['results']
with_matches = [r for r in results if r['total_matches'] > 0]
high_count = [r for r in results if r['total_matches'] > 100]
zero = [r for r in results if r['total_matches'] == 0]

print(f'Total rules evaluated: {len(results)}')
print(f'Rules with matches:    {len(with_matches)}')
print(f'Rules with 0 matches:  {len(zero)}')
print(f'High-count (>100):     {len(high_count)}')
print()

if high_count:
    print('Top 10 by match count (audit candidates):')
    for r in high_count[:10]:
        repos = ', '.join(f\"{k}={v}\" for k, v in r['by_repo'].items() if v > 0)
        print(f'  {r[\"concept\"]:40s} total={r[\"total_matches\"]:6d}  ({repos})')
print()
print(f'Results written to: $RESULTS_FILE')
print('Next step: designer agent runs eval-audit procedure to check for false positives.')
"
