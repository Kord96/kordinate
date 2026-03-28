---
name: train-detection
description: >
  Continuously improve concept detection by cloning diverse repos, running detect-patterns,
  evaluating results against question-based ground truth, and refining signatures, AST rules,
  and diagnostic questions. Use when improving detection quality or expanding concept coverage.
argument-hint: "[--rounds N] [--language LANG] [--topic TOPIC]"
curated: true
---

# train-detection

Automated training loop for improving concept detection quality across the full catalog.

## Arguments

`$ARGUMENTS` -- Optional flags:
- `--rounds N` -- number of repos to process (default: 5)
- `--language LANG` -- filter repos by language (e.g., `python`, `java`, `typescript`, `go`)
- `--topic TOPIC` -- filter repos by GitHub topic (e.g., `microservices`, `api`, `cli`)
- `--concept NAME` -- focus on a single concept (run repos likely to contain it)
- `--skip-clone` -- reuse repos already in `/tmp/train-repos/` from a prior run

## Overview

The training loop has four phases:

1. **Sample** -- clone diverse repos from GitHub
2. **Detect** -- run detect-patterns on each
3. **Evaluate** -- compare detection results against question-based ground truth
4. **Improve** -- update signatures, questions, and AST rules based on findings

Each round produces a scorecard. Over multiple runs, detection precision and recall improve.

## Steps

### Phase 1: Sample Repos

1. **Select repos.** Use the GitHub CLI to discover repos matching the criteria:
   ```bash
   gh search repos --language=$LANG --topic=$TOPIC --stars=50..5000 --sort=updated --limit=20 --json nameWithOwner,description,primaryLanguage,stargazerCount
   ```
   If no language/topic specified, rotate through: `python`, `typescript`, `java`, `go` (one per round).
   Filter out: forks, archived repos, repos < 5 files, repos > 10000 files.
   Select `--rounds` repos randomly from the results.

2. **Clone.** Shallow-clone each repo to `/tmp/train-repos/<owner>--<name>/`:
   ```bash
   git clone --depth 1 https://github.com/<nameWithOwner>.git /tmp/train-repos/<owner>--<name>
   ```
   Skip if already cloned and `--skip-clone` is set.

### Phase 2: Detect

3. **Run detect-patterns** on each cloned repo. Use an Agent subagent with `subagent_type=designer`:
   ```
   Agent(subagent_type="designer", prompt="Run /detect-patterns on /tmp/train-repos/<repo>")
   ```
   Collect the output `patterns.md` from each repo's `.kord/agents/designer/memory/patterns.md`.
   Run repos in parallel where possible (up to 3 concurrent).

### Phase 3: Evaluate (Multi-Oracle Ground Truth)

Ground truth uses three independent oracles to avoid circularity (Claude both detecting and verifying would be circular).

4. **Build ground truth.** For each repo, establish what concepts ACTUALLY exist using three oracles:

   **Oracle 1: Gemini (primary).** Send the repo tree + key source files to Gemini. The prompt provides the full concept list with one-line descriptions and instructs: "Look for the BEHAVIOR, not the NAME. A strategy pattern might be called 'processor' or 'handler'."
   ```bash
   gemini -m gemini-2.5-pro -o json -p "Analyze this codebase. For each concept in this list, answer present/absent with file-level evidence. Look for BEHAVIOR, not naming. $(cat concept-list.txt)" @/tmp/train-repos/<repo>/src/ > /tmp/train-results/<repo>/oracle-gemini.json
   ```

   **Oracle 2: Question-based analysis.** For each concept that passes a quick grep pre-filter (same as detect-patterns Pass 1), load `questions.yaml` and evaluate:
   - For questions with `signals` hints, grep first; skip questions with zero evidence
   - Answer remaining questions yes/no by reading relevant code
   - Score: if weight sum >= threshold, mark present

   **Oracle 3: Mechanical verification.** For concepts with clear markers (specific imports, config files, directory names), verify purely with grep/glob. Unambiguous evidence regardless of LLM opinion.

   **Reconciliation:**
   - Gemini + mechanical agree → **high confidence** ground truth
   - Gemini + questions agree → **medium confidence** ground truth
   - Only one oracle says yes → **low confidence** (flagged, excluded from training metrics)
   - Active disagreement → **excluded** (ambiguous, logged for manual review)

   Write ground truth to `/tmp/train-results/<repo>/ground-truth.json`. Cache persistently in the skill's `data/ground_truth/` directory — re-deriving is expensive.

5. **Check anchor repos.** On every run, also evaluate against the anchor repos in [anchor-repos.json](anchor-repos.json). These are well-known projects with documented patterns (e.g., decorator in Flask, visitor in TypeScript compiler). If detection regresses on anchors, something broke — flag it before proceeding with improvements.

6. **Compare.** For each repo, diff the detect-patterns output against ground truth:
   - **True Positive** -- detected AND in ground truth
   - **False Positive** -- detected but NOT in ground truth
   - **False Negative** -- NOT detected but IS in ground truth
   - **True Negative** -- neither detected nor in ground truth

   Compute per-concept precision and recall across all repos in the round.

7. **Write scorecard** to `/tmp/train-results/scorecard-<timestamp>.json`:
   ```json
   {
     "timestamp": "2026-03-28T07:30:00Z",
     "repos": ["owner--name", ...],
     "per_concept": {
       "circuit-breaker": {"tp": 2, "fp": 0, "fn": 1, "tn": 2, "precision": 1.0, "recall": 0.67},
       "hexagonal": {"tp": 1, "fp": 1, "fn": 0, "tn": 3, "precision": 0.5, "recall": 1.0}
     },
     "aggregate": {"precision": 0.85, "recall": 0.78, "f1": 0.81},
     "worst_precision": ["concept-a", "concept-b"],
     "worst_recall": ["concept-c", "concept-d"]
   }
   ```

### Phase 4: Improve

8. **Analyze failures.** For each false negative (missed detection):
   - Read the repo code where the concept exists (from ground truth evidence)
   - Identify WHY detect-patterns missed it:
     - Missing grep keyword? → add to Recognition signatures
     - AST rule too narrow? → broaden the rule
     - No AST rule exists? → consider writing one
     - Question caught it but grep didn't? → add grep keywords from question signals

9. **Analyze false positives.** For each false positive:
   - Read the detection evidence
   - Identify WHY it was wrongly detected:
     - Grep keyword too broad? → narrow or add exclusion
     - AST rule matches unrelated code? → add constraints
     - Question threshold too low? → raise it

10. **Apply improvements.** For each concept with poor precision or recall:
   - Update `concept.md` Recognition signatures (add/remove keywords)
   - Update `questions.yaml` (refine questions, adjust weights/threshold)
   - Update `ast-grep.yaml` if the rule needs tightening/broadening
   - Keep a changelog in the scorecard

11. **Accumulate results.** Append the scorecard to a persistent log at:
    `~/.kord/agents/designer/memory/training-log.json`
    This allows tracking improvement over time across multiple runs.

12. **Report** -- summarize: repos analyzed, aggregate precision/recall/F1, worst-performing concepts, improvements applied, and where the scorecard was written.

## Scorecard Schema

See [scorecard-schema.md](scorecard-schema.md) for the full JSON schema.

## Error Handling

- **GitHub API rate limit:** Back off and retry, or use `--skip-clone` with existing repos.
- **Repo too large:** Skip repos over 10000 files with a warning.
- **detect-patterns fails:** Record the failure in the scorecard, continue with next repo.
- **Gemini unavailable:** Fall back to running questions through the designer agent (Claude) instead. Slower but functional.
- **No questions.yaml:** Skip question-based evaluation for that concept. Flag it for question generation.
