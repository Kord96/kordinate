#!/usr/bin/env bash
# eval-ast-rules.sh — Evaluate all ast-grep rules against test repos
# Outputs JSON report to eval-results.json
# Usage: bash eval-ast-rules.sh
set -euo pipefail

AST_GREP="${HOME}/.npm-global/bin/ast-grep"
CONCEPTS_DIR="/kord/kordinate/agents/designer/memory/concepts"
EVAL_REPOS_DIR="/tmp/eval-repos"
OUTPUT_FILE="${CONCEPTS_DIR}/eval-results.json"
SCAN_DATA=$(mktemp)
trap 'rm -f "$SCAN_DATA"' EXIT

# ── Test repos ──────────────────────────────────────────────────────
declare -A REPO_URLS=(
  [django]="https://github.com/django/django"
  [flask]="https://github.com/pallets/flask"
  [starlette]="https://github.com/encode/starlette"
  [fastapi-template]="https://github.com/tiangolo/full-stack-fastapi-template"
  [bulletproof-react]="https://github.com/alan2207/bulletproof-react"
  [tanstack-query]="https://github.com/TanStack/query"
  [nextjs]="https://github.com/vercel/next.js"
  [trpc]="https://github.com/trpc/trpc"
)

declare -A REPO_LANGUAGES=(
  [django]="python"
  [flask]="python"
  [starlette]="python"
  [fastapi-template]="python"
  [bulletproof-react]="typescript"
  [tanstack-query]="typescript"
  [nextjs]="typescript"
  [trpc]="typescript"
)

REPO_NAMES=(django flask starlette fastapi-template bulletproof-react tanstack-query nextjs trpc)

# ── Clone repos ─────────────────────────────────────────────────────
mkdir -p "$EVAL_REPOS_DIR"

for repo_name in "${REPO_NAMES[@]}"; do
  repo_dir="${EVAL_REPOS_DIR}/${repo_name}"
  if [ -d "$repo_dir" ]; then
    echo >&2 "[clone] ${repo_name}: already present, skipping"
  else
    url="${REPO_URLS[$repo_name]}"
    echo >&2 "[clone] ${repo_name}: cloning ${url} ..."
    git clone --depth 1 --quiet "$url" "$repo_dir" 2>&1 >&2
    echo >&2 "[clone] ${repo_name}: done"
  fi
done

# ── Collect valid rule files ────────────────────────────────────────
declare -a RULE_FILES=()
declare -a CONCEPTS=()

for rule_file in "${CONCEPTS_DIR}"/*/ast-grep.yaml; do
  concept=$(basename "$(dirname "$rule_file")")
  # Skip comment-only / empty files: require at least one 'id:' line
  if ! grep -qE '^id:' "$rule_file" 2>/dev/null; then
    echo >&2 "[rules] ${concept}: no rules (comment-only), skipping"
    continue
  fi
  RULE_FILES+=("$rule_file")
  CONCEPTS+=("$concept")
done

echo >&2 "[rules] Found ${#RULE_FILES[@]} valid rule files"

# ── Write repo metadata to scan data file ──────────────────────────
for repo_name in "${REPO_NAMES[@]}"; do
  repo_dir="${EVAL_REPOS_DIR}/${repo_name}"
  file_count=$(find "$repo_dir" -type f | wc -l)
  echo "REPO|${repo_name}|${REPO_URLS[$repo_name]}|${REPO_LANGUAGES[$repo_name]}|${file_count}" >> "$SCAN_DATA"
  echo >&2 "[files] ${repo_name}: ${file_count} files"
done

# ── Run scans ───────────────────────────────────────────────────────
total_scans=$(( ${#RULE_FILES[@]} * ${#REPO_NAMES[@]} ))
scan_num=0

for i in "${!RULE_FILES[@]}"; do
  rule_file="${RULE_FILES[$i]}"
  concept="${CONCEPTS[$i]}"

  for repo_name in "${REPO_NAMES[@]}"; do
    scan_num=$((scan_num + 1))
    repo_dir="${EVAL_REPOS_DIR}/${repo_name}"

    printf >&2 "\r[scan %d/%d] %-30s x %-20s" "$scan_num" "$total_scans" "$concept" "$repo_name"

    # Run ast-grep and count JSON array length
    match_count=$("$AST_GREP" scan --rule "$rule_file" --json "$repo_dir" 2>/dev/null \
      | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null) || match_count=0

    echo "SCAN|${concept}|${repo_name}|${match_count}" >> "$SCAN_DATA"
  done
done

echo >&2 ""
echo >&2 "[scan] All scans complete. Generating report..."

# ── Generate JSON report via Python ─────────────────────────────────
python3 - "$SCAN_DATA" "$OUTPUT_FILE" "$CONCEPTS_DIR" << 'PYEOF'
import json, sys, os
from datetime import datetime, timezone

scan_data_file = sys.argv[1]
output_file = sys.argv[2]
concepts_dir = sys.argv[3]

# Parse scan data
repos = {}       # name -> {url, language, files}
results = {}     # concept -> {repo -> count}

with open(scan_data_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if parts[0] == "REPO":
            _, name, url, lang, files = parts
            repos[name] = {"url": url, "language": lang, "files": int(files)}
        elif parts[0] == "SCAN":
            _, concept, repo, count = parts
            results.setdefault(concept, {})[repo] = int(count)

# Determine which concepts are language-specific
ts_only_concepts = set()
py_only_concepts = set()
for concept in results:
    rule_file = os.path.join(concepts_dir, concept, "ast-grep.yaml")
    if not os.path.isfile(rule_file):
        continue
    with open(rule_file) as f:
        content = f.read()
    langs = set()
    for rl in content.split("\n"):
        if rl.startswith("language:"):
            langs.add(rl.split(":", 1)[1].strip())
    if langs <= {"TypeScript", "JavaScript"} and "TypeScript" in langs:
        ts_only_concepts.add(concept)
    elif langs == {"Python"}:
        py_only_concepts.add(concept)

# Build suspects
suspects = []
for concept, repo_counts in sorted(results.items()):
    nonzero = {r: c for r, c in repo_counts.items() if c > 0}
    if not nonzero:
        continue

    min_nonzero = min(nonzero.values())
    max_count = max(nonzero.values())

    for repo, count in repo_counts.items():
        if count == 0:
            continue
        repo_lang = repos.get(repo, {}).get("language", "unknown")
        reasons = []

        # Heuristic 1: language mismatch
        if concept in ts_only_concepts and repo_lang == "python":
            reasons.append("TypeScript-only concept matched in Python repo")
        if concept in py_only_concepts and repo_lang == "typescript":
            reasons.append("Python-only concept matched in TypeScript repo")

        # Heuristic 2: suspiciously high count
        if count > 500:
            reasons.append(f"very high count ({count})")
        elif count > 100:
            reasons.append(f"high count ({count})")

        # Heuristic 3: extreme ratio between repos (>10x)
        if min_nonzero > 0 and len(nonzero) > 1 and count >= 10:
            ratio = count / min_nonzero
            if ratio > 10:
                lowest_repo = min(nonzero, key=nonzero.get)
                reasons.append(f"{ratio:.0f}x vs {lowest_repo} ({min_nonzero})")

        if reasons:
            suspects.append({
                "concept": concept,
                "repo": repo,
                "count": count,
                "reason": "; ".join(reasons)
            })

suspects.sort(key=lambda s: s["count"], reverse=True)

# Build sorted output
report = {
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "repos": dict(sorted(repos.items())),
    "results": dict(sorted(
        ((c, dict(sorted(rc.items()))) for c, rc in results.items()),
        key=lambda x: x[0]
    )),
    "suspects": suspects
}

with open(output_file, "w") as f:
    json.dump(report, f, indent=2)
    f.write("\n")

print(f"Report written to {output_file}", file=sys.stderr)
print(f"  Concepts scanned: {len(results)}", file=sys.stderr)
nonzero_pairs = sum(1 for c in results.values() for v in c.values() if v > 0)
print(f"  Non-zero concept x repo pairs: {nonzero_pairs}", file=sys.stderr)
print(f"  Suspects flagged: {len(suspects)}", file=sys.stderr)
PYEOF
