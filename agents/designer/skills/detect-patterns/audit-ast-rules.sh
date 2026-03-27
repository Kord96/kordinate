#!/usr/bin/env bash
# audit-ast-rules.sh — Audit suspect matches from eval-results.json
# For each suspect, captures sample matches and writes eval-audit.md
# Usage: bash audit-ast-rules.sh
set -euo pipefail

AST_GREP="${HOME}/.npm-global/bin/ast-grep"
CONCEPTS_DIR="/kord/kordinate/agents/designer/memory/concepts"
EVAL_REPOS_DIR="/tmp/eval-repos"
INPUT_FILE="${CONCEPTS_DIR}/eval-results.json"
OUTPUT_FILE="${CONCEPTS_DIR}/eval-audit.md"
MAX_SAMPLES=5

if [ ! -f "$INPUT_FILE" ]; then
  echo >&2 "Error: ${INPUT_FILE} not found. Run eval-ast-rules.sh first."
  exit 1
fi

# ── Extract suspects and collect samples ────────────────────────────
python3 - "$INPUT_FILE" "$CONCEPTS_DIR" "$EVAL_REPOS_DIR" "$AST_GREP" "$OUTPUT_FILE" "$MAX_SAMPLES" << 'PYEOF'
import json, sys, os, subprocess, textwrap
from pathlib import Path

input_file = sys.argv[1]
concepts_dir = sys.argv[2]
eval_repos_dir = sys.argv[3]
ast_grep = sys.argv[4]
output_file = sys.argv[5]
max_samples = int(sys.argv[6])

with open(input_file) as f:
    report = json.load(f)

suspects = report.get("suspects", [])
if not suspects:
    print("No suspects to audit.", file=sys.stderr)
    sys.exit(0)

print(f"Auditing {len(suspects)} suspects...", file=sys.stderr)

# Group suspects by concept to avoid redundant scans
by_concept_repo = {}
for s in suspects:
    key = (s["concept"], s["repo"])
    by_concept_repo[key] = s

lines = []
lines.append("# AST-Grep Rule Eval Audit")
lines.append("")
lines.append(f"Generated: {report['timestamp']}")
lines.append(f"Suspects: {len(suspects)}")
lines.append("")
lines.append("## Suspects")
lines.append("")

for idx, ((concept, repo), suspect) in enumerate(sorted(
    by_concept_repo.items(), key=lambda x: x[1]["count"], reverse=True
)):
    count = suspect["count"]
    reason = suspect["reason"]
    rule_file = os.path.join(concepts_dir, concept, "ast-grep.yaml")
    repo_dir = os.path.join(eval_repos_dir, repo)

    print(f"  [{idx+1}/{len(by_concept_repo)}] {concept} x {repo} ({count} matches)", file=sys.stderr)

    lines.append(f"### {concept} in {repo} ({count} matches)")
    lines.append(f"**Reason:** {reason}")
    lines.append(f"**Rule file:** `{concept}/ast-grep.yaml`")
    lines.append("")

    # Run ast-grep to get sample matches
    samples = []
    try:
        result = subprocess.run(
            [ast_grep, "scan", "--rule", rule_file, "--json", repo_dir],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0 and result.stdout.strip():
            matches = json.loads(result.stdout)
            # Deduplicate by file+line, take first N
            seen = set()
            for m in matches:
                fpath = m.get("file", "")
                start_line = m.get("range", {}).get("start", {}).get("line", 0)
                key = f"{fpath}:{start_line}"
                if key in seen:
                    continue
                seen.add(key)
                # Make path relative to repo dir
                rel_path = os.path.relpath(fpath, repo_dir)
                text = m.get("text", "").strip()
                rule_id = m.get("ruleId", "unknown")
                # Truncate long matches
                if len(text) > 200:
                    text = text[:200] + "..."
                # Escape backticks in text
                text = text.replace("`", "\\`")
                samples.append({
                    "location": f"{rel_path}:{start_line + 1}",
                    "text": text,
                    "rule_id": rule_id
                })
                if len(samples) >= max_samples:
                    break
    except (subprocess.TimeoutExpired, Exception) as e:
        samples = [{"location": "ERROR", "text": str(e), "rule_id": "N/A"}]

    if samples:
        lines.append("**Sample matches:**")
        for s in samples:
            lines.append(f"- `{s['location']}` (rule: {s['rule_id']})")
            # Show first line of match text
            first_line = s["text"].split("\n")[0]
            lines.append(f"  ```")
            lines.append(f"  {first_line}")
            lines.append(f"  ```")
    else:
        lines.append("**Sample matches:** (none captured)")

    lines.append("")
    lines.append("**Verdict:** NEEDS REVIEW")
    lines.append("**Fix:** (pending manual analysis)")
    lines.append("")
    lines.append("---")
    lines.append("")

with open(output_file, "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"Audit report written to {output_file}", file=sys.stderr)
PYEOF
