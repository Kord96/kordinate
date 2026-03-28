#!/usr/bin/env bash
# tune-ast-rules.sh — Summarize fixes needed from audit, re-run eval after manual fixes
# Usage: bash tune-ast-rules.sh [--rerun]
#   Without flags: prints summary of what needs fixing
#   With --rerun:  re-runs eval and diffs against previous results
set -euo pipefail

CONCEPTS_DIR="/kord/kordinate/agents/designer/memory/concepts"
AUDIT_FILE="${CONCEPTS_DIR}/eval-audit.md"
RESULTS_FILE="${CONCEPTS_DIR}/eval-results.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "${1:-}" = "--rerun" ]; then
  # ── Re-run mode: eval and diff ──────────────────────────────────
  if [ -f "$RESULTS_FILE" ]; then
    cp "$RESULTS_FILE" "${RESULTS_FILE}.prev"
    echo >&2 "[tune] Saved previous results to eval-results.json.prev"
  fi

  echo >&2 "[tune] Re-running eval..."
  bash "${SCRIPT_DIR}/eval-ast-rules.sh"

  if [ -f "${RESULTS_FILE}.prev" ]; then
    echo >&2 ""
    echo >&2 "[tune] Comparing results..."
    python3 - "$RESULTS_FILE" "${RESULTS_FILE}.prev" << 'PYEOF'
import json, sys

with open(sys.argv[1]) as f:
    current = json.load(f)
with open(sys.argv[2]) as f:
    previous = json.load(f)

cur_results = current.get("results", {})
prev_results = previous.get("results", {})
cur_suspects = current.get("suspects", [])
prev_suspects = previous.get("suspects", [])

print(f"\n{'='*60}", file=sys.stderr)
print(f"EVAL COMPARISON", file=sys.stderr)
print(f"{'='*60}", file=sys.stderr)
print(f"Previous suspects: {len(prev_suspects)}", file=sys.stderr)
print(f"Current suspects:  {len(cur_suspects)}", file=sys.stderr)

# Show changes per concept
all_concepts = sorted(set(list(cur_results.keys()) + list(prev_results.keys())))
changes = []
for concept in all_concepts:
    cur_repos = cur_results.get(concept, {})
    prev_repos = prev_results.get(concept, {})
    for repo in sorted(set(list(cur_repos.keys()) + list(prev_repos.keys()))):
        cur_count = cur_repos.get(repo, 0)
        prev_count = prev_repos.get(repo, 0)
        if cur_count != prev_count:
            delta = cur_count - prev_count
            changes.append((concept, repo, prev_count, cur_count, delta))

if changes:
    print(f"\nChanges ({len(changes)} concept x repo pairs):", file=sys.stderr)
    print(f"{'Concept':<35} {'Repo':<20} {'Before':>8} {'After':>8} {'Delta':>8}", file=sys.stderr)
    print(f"{'-'*35} {'-'*20} {'-'*8} {'-'*8} {'-'*8}", file=sys.stderr)
    for concept, repo, prev_c, cur_c, delta in sorted(changes, key=lambda x: abs(x[4]), reverse=True):
        sign = "+" if delta > 0 else ""
        print(f"{concept:<35} {repo:<20} {prev_c:>8} {cur_c:>8} {sign}{delta:>7}", file=sys.stderr)
else:
    print("\nNo changes detected.", file=sys.stderr)

print(f"{'='*60}\n", file=sys.stderr)
PYEOF
  fi
  exit 0
fi

# ── Summary mode: show what needs fixing ────────────────────────────
if [ ! -f "$AUDIT_FILE" ]; then
  echo >&2 "Error: ${AUDIT_FILE} not found. Run audit-ast-rules.sh first."
  exit 1
fi

if [ ! -f "$RESULTS_FILE" ]; then
  echo >&2 "Error: ${RESULTS_FILE} not found. Run eval-ast-rules.sh first."
  exit 1
fi

python3 - "$RESULTS_FILE" "$AUDIT_FILE" "$CONCEPTS_DIR" << 'PYEOF'
import json, sys, os

results_file = sys.argv[1]
audit_file = sys.argv[2]
concepts_dir = sys.argv[3]

with open(results_file) as f:
    report = json.load(f)

suspects = report.get("suspects", [])
if not suspects:
    print("No suspects found. Rules look clean!")
    sys.exit(0)

# Group by concept
by_concept = {}
for s in suspects:
    by_concept.setdefault(s["concept"], []).append(s)

print(f"{'='*60}")
print(f"TUNE SUMMARY — {len(suspects)} suspects across {len(by_concept)} concepts")
print(f"{'='*60}")
print()

for concept in sorted(by_concept, key=lambda c: max(s["count"] for s in by_concept[c]), reverse=True):
    entries = by_concept[concept]
    rule_file = os.path.join(concepts_dir, concept, "ast-grep.yaml")

    print(f"## {concept}")
    print(f"   Rule: {concept}/ast-grep.yaml")

    # Show current rules in the file
    if os.path.isfile(rule_file):
        with open(rule_file) as f:
            content = f.read()
        # Extract rule IDs
        rule_ids = [l.split(":", 1)[1].strip() for l in content.split("\n") if l.startswith("id:")]
        print(f"   Rules: {', '.join(rule_ids)}")

    for e in sorted(entries, key=lambda x: x["count"], reverse=True):
        print(f"   - {e['repo']}: {e['count']} matches — {e['reason']}")

    print()

print(f"{'='*60}")
print(f"Next steps:")
print(f"  1. Review samples in: {audit_file}")
print(f"  2. Edit rule files to reduce false positives")
print(f"  3. Re-run: bash tune-ast-rules.sh --rerun")
print(f"{'='*60}")
PYEOF
