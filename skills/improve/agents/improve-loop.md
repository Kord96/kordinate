# Improve Loop — Per-Agent Prompt

Prompt for each team agent launched by `/improve all` or `/improve agent`.
Each agent is spawned as its own `subagent_type` so it brings domain expertise and memories.

## Setup

Run `/boot` first to load your memories and context.

## Input

- `$SKILL_PATHS` — list of skill directories to improve (all belong to you)
- `$IDENTITY_PATH` — path to the agent's IDENTITY.md
- `$MAX_ITERATIONS` — hard cap per skill (default: 3)
- `$DRY_RUN` — if true, report findings without editing
- `$DATA_DIR` — persistent storage root (default: `/data/improve`)

## Progress Tracking

Training runs can be long-running and may survive context compression. Write a manifest
to `$DATA_DIR/<agent>/manifest.json` on start and update it throughout:

```json
{
  "agent": "<agent-name>",
  "run_id": "<timestamp>",
  "status": "in-progress",
  "started_at": "ISO-8601",
  "completed_at": null,
  "phase": "portfolio-review",
  "portfolio_findings": [],
  "skills_planned": ["skill-a", "skill-b"],
  "skills_completed": [],
  "test_repos": [],
  "error": null
}
```

Update `phase`, `skills_completed`, and `test_repos` as you progress. On error, set
`status: "failed"` with an `error` field. On completion, set `status: "complete"`.

If you lose context after compaction, read this manifest to recover your state.

---

## Phase 1 — Portfolio Review

Before touching individual skills, assess whether your skill portfolio is the right set
of skills for your responsibilities. This phase produces strategic findings that inform
Phase 2.

### Step 1.1 — Load Identity and Inventory

Read `$IDENTITY_PATH` to extract:
- Your **role** (the one-line description of what you do)
- Your **responsibilities** (capabilities, consultation topics, rules)
- Your **skills table** (what skills you claim to have)

Then read all skill SKILL.md files in `$SKILL_PATHS` — just the frontmatter and first
section, not supporting files yet. Build an inventory:

| Field | Source |
|-------|--------|
| Skill name | frontmatter `name` |
| Description | frontmatter `description` |
| Line count | `wc -l` |
| Supporting files | sibling files in the skill directory |
| 3rd-layer resources | files referenced from SKILL.md body (scripts, templates, schemas) |

### Step 1.2 — Launch Background Research (one-time)

Kick off a single web search for inspiration. This runs once per improve-loop invocation,
not per skill. Use WebSearch to find community skills, patterns, or tools relevant to your
domain:

```
WebSearch("Claude Code skills for <your-domain> — community patterns, automation approaches, best practices")
```

Do not wait for results — continue to Step 1.3. Read results in Step 1.6.

This step is slow. It runs once to gather ideas, not as a repeated lookup. If the search
fails or returns nothing useful, proceed without it.

### Step 1.3 — Portfolio Analysis

Compare your identity responsibilities against your skill inventory. Answer each question
honestly — the goal is self-awareness, not self-congratulation:

| Analysis | Question |
|----------|----------|
| **Alignment** | Does each skill directly serve a responsibility in my identity? Are any skills tangential to my role? |
| **Coverage gaps** | Which responsibilities in my identity have no skill covering them? What do I get asked to do manually that a skill could automate? |
| **New skill needs** | Based on my role, what skills am I missing entirely? What would make me significantly more useful? |
| **Split candidates** | Which skills are >400 lines or cover multiple distinct workflows that could be independent? |
| **Merge candidates** | Which skills have overlapping triggers, duplicated instructions, or shared supporting files? |
| **Misplacements** | Do any of my skills belong to a different agent's domain? Do other agents have skills that belong to me? |
| **Staleness** | Do any skills reference tools, paths, commands, or patterns that no longer exist or have changed? |
| **Resource gaps** | Are my 3rd-layer resources (scripts, templates, schemas, reference docs) sufficient? Am I missing automation that would make skills more reliable? |
| **Quality of thought** | Do my skills explain *why* behind their instructions, or do they just list rigid steps? Would an intelligent agent understand the reasoning? |

Check your memory (loaded at boot) for evidence. Past scratchpad entries about recurring
manual work, failed approaches, or workarounds are signals for gaps.

### Step 1.4 — Gemini Peer Review

Write your portfolio assessment to a temp file, then send it to Gemini for a second opinion.
Run in background:

```bash
cat > /tmp/improve-portfolio-<agent>.md << 'EOF'
<your portfolio assessment from Step 1.3>
EOF

gemini -m gemini-2.5-pro -o json -p "Review this agent self-assessment. The agent's role: <role summary>. Current skills: <skill list>. Assessment: $(cat /tmp/improve-portfolio-<agent>.md). What did it miss? What do you disagree with? Are there blind spots? Be specific and constructive." > /tmp/improve-gemini-<agent>.json &
```

Continue to Step 1.5. Read Gemini's response in Step 1.6.

### Step 1.5 — Clone Test Repos

Select 2-3 repos to test your skills against real codebases. Use GitHub CLI:

```bash
gh search repos --language=<relevant-lang> --stars=100..5000 --sort=updated --limit=10 \
  --json nameWithOwner,description,primaryLanguage,stargazerCount
```

Pick repos that are likely to exercise your skills (e.g., for an observability agent, pick
repos with monitoring code; for an architecture agent, pick repos with clear design patterns).

Check the repo database at `$DATA_DIR/repo-database.json` — avoid repos already tested
in the last 30 days (to broaden coverage). Clone:

```bash
git clone --depth 1 https://github.com/<nameWithOwner>.git /data/repos/<owner>--<name>
```

Record each repo in the manifest's `test_repos` array:
```json
{"nameWithOwner": "owner/repo", "language": "python", "stars": 1200, "cloned_at": "ISO-8601"}
```

### Step 1.6 — Incorporate External Input

Read results from Step 1.2 (web search) and Step 1.4 (Gemini review):

- **Web research**: extract specifically relevant patterns or community approaches. Tag
  findings as `source: research` so they are distinguishable from self-assessment.
- **Gemini review**: incorporate valid critiques. Discard opinions that contradict evidence
  from the actual codebase or your memory. Gemini's opinion is a second signal, not gospel.

### Step 1.7 — Check Improvement History

Read `$DATA_DIR/<agent>/history.json` if it exists. This file accumulates findings across
runs. Check for:

- **Recurring findings** — the same gap or issue flagged in multiple runs means it's real
  and hasn't been addressed. Escalate its priority.
- **Previously proposed items** — findings that were "proposed" in past runs but never
  acted on. Re-surface them with a note: "proposed N runs ago, still unresolved."
- **Trends** — are skills improving or degrading over time? Are new gaps opening as the
  agent's responsibilities grow?
- **Plateau detection** — compare this run's portfolio findings against the last 2 runs.
  If all three runs produced the same findings (same gaps, same split/merge candidates,
  same staleness issues) and no new findings emerged, the portfolio is stable. Set
  `plateau: true` in the manifest.

If the file doesn't exist, this is the first run — skip to Step 1.8.

#### Early Stop — Portfolio Plateau

If `plateau: true` and no "immediate" or "scaffold" findings differ from prior runs:

1. Skip Phase 2 entirely — there is nothing new to improve.
2. Go directly to Phase 3 (Sleep) to update history with the plateau observation.
3. Report: "Portfolio stable — no new findings in N consecutive runs. Stopping early."

This prevents burning tokens re-reviewing skills that haven't changed. The plateau
breaks when: the agent's identity changes, new skills are added externally, or a
skill file is edited outside the improve loop.

### Step 1.8 — Portfolio Decision

Classify each finding:

- **Immediate** — can be done during this improve run: staleness fixes, resource additions,
  minor refactoring, supporting file improvements. Execute these in Phase 2.
- **Scaffold** — new skills or skill splits that can be created now with a minimal SKILL.md.
  These don't require human approval because they're additive — they don't change or remove
  anything. Scaffold them in Phase 2 (see Step 2.8).
- **Proposed** — requires human approval: agent reassignment, major merges, destructive
  restructuring, responsibility changes. Record for the summary.

Update the manifest: `phase: "per-skill-iteration"`, `portfolio_findings: [...]`.

If `$DRY_RUN`: record all findings, skip to Output.

---

## Phase 2 — Per-Skill Iteration

Process each skill in `$SKILL_PATHS` sequentially, running the iteration loop below.
Portfolio findings from Phase 1 inform your review criteria.

For each iteration (1 to `$MAX_ITERATIONS`):

### Step 2.1 — Read

Read `$SKILL_PATH/SKILL.md` and all supporting files. Also read the agent's other skills
for cross-reference (overlaps, inconsistencies, shared patterns).

Pull in any Phase 1 findings relevant to this skill (e.g., "this skill was flagged as a
split candidate" or "missing 3rd-layer resources").

### Step 2.2 — Test Against Real Repos and Assess Output Quality

If test repos were cloned in Step 1.5, run the skill against one of them AND evaluate
whether the output is correct. Running the skill is not enough — you must assess the
quality of what it produces.

#### 2.2a — Run the Skill

Execute the skill's procedure against a cloned repo. Capture the full output (save to
`$DATA_DIR/<agent>/test-outputs/<skill>-<repo>/`).

| Skill type | How to run |
|------------|-----------|
| **Scan/detect** (detect-concepts, detect-patterns, scan-observability, assess-debt) | Run the full procedure. Save the output artifact (concepts.md, patterns report, etc.) |
| **Generate** (architect, analyze, map-dependencies, review-api) | Run the full procedure. Save the generated artifact (architecture.yaml, dependency graph, API report) |
| **Transform** (edit-based skills) | Dry-run on a copy of the repo. Save proposed changes as a patch. |
| **Deploy/infra** | Skip — trace the procedure mentally instead. |
| **Meta** (improve, train-detection) | Skip — these are tested by running them. |

#### 2.2b — Build Ground Truth

For each skill output, build independent ground truth to compare against. Use multiple
oracles to avoid circularity (the agent both running the skill AND judging its own output
is circular). At least two oracles must agree for high-confidence ground truth.

**Oracle 1 — Gemini (primary).** Send the repo's key source files to Gemini with a
targeted prompt. Run in background:

```bash
gemini -m gemini-2.5-pro -o json -p "<oracle prompt for skill type>" \
  @/data/repos/<repo>/src/ > $DATA_DIR/<agent>/ground-truth/<skill>-<repo>-gemini.json &
```

Oracle prompts by skill type:

| Skill | Gemini oracle prompt |
|-------|---------------------|
| **detect-concepts** | "List every architectural concept, pattern, and anti-pattern present in this codebase. For each, cite the specific file and line range as evidence. Look for BEHAVIOR, not naming." |
| **detect-patterns** | Same as detect-concepts (they share the same catalog). |
| **review-api** | "List every API endpoint in this codebase — method, path, handler function, file. Note any inconsistencies in naming, authentication, error handling, or response format." |
| **assess-debt** | "Identify every instance of tech debt in this codebase — code smells, anti-patterns, missing tests, hardcoded values, dead code. For each, cite the file and describe the impact." |
| **map-dependencies** | "List every dependency: internal module imports, external packages, infrastructure services (databases, caches, queues), and external API calls. Cite the import statement or connection string." |
| **architect/analyze** | "Describe the architecture of this codebase: main components, their responsibilities, how data flows between them, state management, and failure modes. Cite specific files for each component." |
| **scan-observability** | "List every observability signal: log statements (with level and message), metrics (with names), health check endpoints, and tracing spans. Cite file and line." |

**Oracle 2 — Mechanical verification.** Use grep/glob/AST to independently verify
specific claims. This catches hallucinations from both the skill and Gemini:

| Skill | Mechanical checks |
|-------|------------------|
| **detect-concepts** | Grep for import statements, decorators, config files that confirm/deny each detected concept |
| **review-api** | Grep for route decorators (`@app.get`, `@router.post`, `http.HandleFunc`, etc.) and count — does the skill's endpoint count match? |
| **assess-debt** | Verify cited files exist. Grep for the specific patterns flagged (e.g., `TODO`, hardcoded strings, bare excepts) |
| **map-dependencies** | Parse `requirements.txt`/`go.mod`/`package.json` — does the skill's external dep list match? Grep for imports — does the internal module list match? |
| **architect/analyze** | Verify every component name maps to a real file/directory. Check that stated data flows have matching import/call chains. |
| **scan-observability** | Grep for `log.`, `logger.`, `metrics.`, `/health`, `/ready` — does the count match the skill's output? |

**Oracle 3 — Cross-skill validation.** If multiple skills ran on the same repo, their
outputs should be consistent:
- Components in `architect` output should appear in `map-dependencies` output
- Endpoints in `review-api` should align with routes found by `detect-concepts`
- Debt flagged by `assess-debt` should reference real components from `architect`

#### 2.2c — Score

Compare the skill's output against ground truth. Compute per-item:

- **True Positive** — skill found it AND ground truth confirms it
- **False Positive** — skill found it BUT ground truth says it's not there (hallucination)
- **False Negative** — skill missed it BUT ground truth says it exists (gap)
- **True Negative** — neither found it (not applicable for most skills)

Compute:
- **Precision** = TP / (TP + FP) — "when the skill says something, is it right?"
- **Recall** = TP / (TP + FN) — "does the skill find everything that's there?"
- **F1** = 2 * (P * R) / (P + R) — balanced score

For skills where items aren't countable (e.g., architect produces a narrative), score
on a rubric instead:

| Dimension | 1 (poor) | 3 (adequate) | 5 (excellent) |
|-----------|----------|-------------|--------------|
| **Completeness** | Major components missing | Most components present, some gaps | All components identified |
| **Accuracy** | Multiple hallucinated components | Minor inaccuracies | All claims verifiable in code |
| **Specificity** | Vague descriptions, no file refs | Some file refs, some vague | Every claim cites specific files |
| **Consistency** | Contradicts other skill outputs | Mostly consistent | Fully consistent with other skills |

#### 2.2d — Record Results

Save to `$DATA_DIR/<agent>/test-results/<skill>-<repo>.json`:

```json
{
  "skill": "<name>",
  "repo": "<nameWithOwner>",
  "tested_at": "ISO-8601",
  "ground_truth": {
    "gemini_oracle": "<path to gemini output>",
    "mechanical_checks": {"endpoints_found": 12, "skill_reported": 10, "match": false},
    "cross_skill": {"consistent_with": ["architect", "map-dependencies"], "conflicts": []}
  },
  "scores": {
    "precision": 0.85,
    "recall": 0.70,
    "f1": 0.77
  },
  "rubric_scores": null,
  "false_positives": ["skill claimed X but it doesn't exist"],
  "false_negatives": ["skill missed Y which is clearly present at path/to/file.py"],
  "issues_found": ["step 3 failed to detect FastAPI routes using include_router()"],
  "notes": ""
}
```

The `false_positives` and `false_negatives` lists are the most actionable — they tell
you exactly what to fix in the skill's detection logic, grep patterns, or procedure steps.

#### 2.2e — Feed Scores Back to Skill Improvement

If F1 < 0.70 (or rubric average < 3), the skill has significant quality issues. In Step
2.3 (Review), prioritize the specific false positives and false negatives over general
quality criteria. The test results tell you exactly what's wrong — fix those first.

If F1 >= 0.90 (or rubric average >= 4.5), the skill is performing well. Focus Step 2.3
on resource gaps and edge cases rather than core logic.

### Step 2.3 — Review

Evaluate the skill against these criteria:

| Category | What to look for |
|----------|-----------------|
| **Completeness** | Missing steps, undefined terms, gaps between steps where an implementer would be stuck |
| **Correctness** | Wrong commands, incorrect flags, outdated references, steps that would fail |
| **Clarity** | Ambiguous instructions, unclear conditionals, missing context for decisions |
| **Consistency** | Naming mismatches with other skills, inconsistent formatting, frontmatter issues |
| **Actionability** | Steps that say "handle X" without saying how, vague verbs like "process" or "manage" |
| **Alignment** | Does this skill serve the agent's identity? Is it in the right place? (from Phase 1) |
| **Resources** | Are 3rd-layer resources sufficient? Missing scripts, templates, schemas? |

Do NOT look for:
- Style preferences (Oxford commas, heading levels, bullet vs number)
- Missing features the skill doesn't claim to have (but DO flag features it SHOULD claim based on Phase 1)
- Hypothetical edge cases that don't arise in practice

### Step 2.4 — Classify and decide

If you found issues, classify them:

- **Structural** — missing steps, wrong commands, logical gaps, incorrect information,
  incomplete output specifications, missing resources. These materially affect whether
  someone following the skill would succeed.
- **Cosmetic** — rewording for clarity without changing meaning, reformatting tables,
  reordering sections, fixing typos.

Decision:
- If no issues found → stop, report "no-changes"
- If only cosmetic issues → apply them, then stop, report "cosmetic-only"
- If structural issues → apply fixes, continue to next iteration

### Step 2.5 — Apply changes

Edit the skill files to address the structural issues. Make the minimum change needed
to fix each issue — don't rewrite surrounding paragraphs or restructure sections
unless the structure itself is the problem.

When adding 3rd-layer resources (scripts, templates, schemas), create them as supporting
files referenced from SKILL.md, not inline content.

### Step 2.5b — Gemini diff review (structural changes only)

For structural changes that touch multiple files or alter a skill's procedure flow,
send the diff to Gemini for a quick review before committing. Skip this for cosmetic-only
or single-line fixes.

```bash
git diff --no-color > /tmp/improve-diff-<agent>-<skill>.patch
gemini -m gemini-2.5-flash -p "Review this diff to a Claude Code skill definition. Flag: instructions that contradict themselves, steps that reference nonexistent tools or files, changes that break the skill's output format, or regressions (removing something that was correct). Be terse — just list issues or say 'looks good'." @/tmp/improve-diff-<agent>-<skill>.patch
```

Use `gemini-2.5-flash` (not pro) to keep this fast. If Gemini flags a real issue, fix it
before proceeding. If it flags style preferences, ignore them.

### Step 2.6 — Anti-oscillation check

Before committing to the changes, compare your diff against diffs from previous
iterations. If you are reverting or undoing a change you made in a prior iteration,
discard your changes for this iteration, stop, and report "revert-detected".

### Step 2.7 — Log iteration

Record for the final summary:
- Iteration number
- Classification (structural / cosmetic / no-changes)
- One-line summary of each change made
- Test results from Step 2.2 (if applicable)

Update manifest: add skill to `skills_completed`.

Then proceed to the next iteration (or stop if conditions are met).

### Step 2.8 — Scaffold New Skills

After completing per-skill iteration, create any skills classified as "scaffold" in
Step 1.8. For each new skill:

1. Create the directory: `$KORDINATE_HOME/agents/<agent>/skills/<skill-name>/`
2. Write a minimal `SKILL.md` with:
   - Frontmatter: `name`, `description`, `curated: true`
   - A clear statement of purpose (what and when)
   - A numbered procedure with concrete steps
   - Output format specification
3. Keep it under 100 lines — this is a starting point, not a finished product. Future
   improve runs will iterate on it.
4. Reference it in the agent's IDENTITY.md skills table.

Do NOT scaffold skills that duplicate existing functionality in other agents. If unsure,
classify as "proposed" instead.

---

## Phase 3 — Sleep

Persist findings so the next improvement run starts with awareness of what was assessed.

### Step 3.1 — Update Repo Database

Append tested repos to the persistent database at `$DATA_DIR/repo-database.json`:

```json
[
  {
    "nameWithOwner": "owner/repo",
    "language": "python",
    "stars": 1200,
    "tested_by": "<agent-name>",
    "tested_at": "ISO-8601",
    "skills_tested": ["skill-a", "skill-b"],
    "results_path": "$DATA_DIR/<agent>/test-results/"
  }
]
```

Create the file if it doesn't exist. Append to the array if it does.

### Step 3.2 — Update Improvement History

Append this run's summary to `$DATA_DIR/<agent>/history.json`. Each entry captures
what was found and done, enabling trend analysis across runs:

```json
{
  "run_id": "<timestamp>",
  "date": "YYYY-MM-DD",
  "portfolio_findings": {
    "coverage_gaps": ["..."],
    "split_candidates": ["..."],
    "new_skills_scaffolded": ["..."],
    "staleness_fixes": ["..."]
  },
  "per_skill_results": {
    "skill-a": {"iterations": 2, "stop_reason": "cosmetic-only", "test_result": "pass"},
    "skill-b": {"iterations": 1, "stop_reason": "no-changes", "test_result": "pass"}
  },
  "proposed_actions": ["..."],
  "repos_tested": ["owner/repo-1", "owner/repo-2"]
}
```

Create the file as `[]` if it doesn't exist. Append to the array. Keep the last 20 entries
(trim oldest if over).

### Step 3.3 — Persist Portfolio Findings

For each finding classified as "proposed" (needs human approval):
```
/kord remember <agent-name> portfolio review: <finding description>
```

For domain insights discovered during improvement:
```
/kord remember <agent-name> learned during self-improvement: <insight>
```

### Step 3.4 — Commit and Push

Commit all changes and push. The worktree-push hook will automatically merge
to main on push.

```bash
git -C $KORDINATE_HOME add -A
git -C $KORDINATE_HOME commit -m "improve: <agent> — <one-line summary of changes>"
git -C $KORDINATE_HOME push 2>/dev/null || true
```

If the push triggers a merge conflict, the hook will report it. The next `/merge`
run will resolve it.

### Step 3.5 — Finalize Manifest

Update manifest:
```json
{
  "status": "complete",
  "completed_at": "ISO-8601",
  "phase": "done"
}
```

---

## Output

Return a structured summary covering all phases:

```
Agent: <agent-name>

## Portfolio Review
  Coverage gaps: <list or "none">
  New skill proposals: <list or "none">
  Split candidates: <list or "none">
  Merge candidates: <list or "none">
  Misplacements: <list or "none">
  Staleness: <list or "none">
  Resource gaps: <list or "none">
  Research insights: <list or "none">
  Gemini critiques incorporated: <list or "none">
  Immediate actions taken: <list or "none">
  Proposed actions (needs approval): <list or "none">

## Test Repos
  <repo-1>: <language>, <stars> stars — tested <N> skills
  <repo-2>: <language>, <stars> stars — tested <N> skills

## Per-Skill Results

Skill: <skill-name>
  Iterations: <N>/<MAX>
  Stop reason: no-changes | cosmetic-only | revert-detected | max-iterations
  Test results: <pass/fail summary against repos>
  Changes:
  - [iteration 1] (structural) Added missing verification step after kubectl apply
  - [iteration 2] (cosmetic) Clarified wording in secrets section — stopping

Skill: <skill-name>
  Iterations: <N>/<MAX>
  Stop reason: no-changes
  Changes: —

## Cross-Cutting Analysis

Synthesize findings across all skills and all repos. This is the most valuable part
of the report — patterns that only emerge when looking at the portfolio as a whole:

- **Common weaknesses**: issues that appeared in 3+ skills (e.g., "most skills lack
  error handling guidance", "no skill specifies output format")
- **Repo-specific patterns**: did certain repos expose more issues than others? Why?
  (e.g., "Go repos exposed missing language-specific steps in 4 skills")
- **Structural themes**: are the issues mostly completeness, correctness, clarity, or
  resources? This tells the agent where to focus next time.
- **Test coverage assessment**: which skills were testable vs. skipped? What would make
  untestable skills testable?
- **Improvement velocity**: how many structural issues were found and fixed vs. how many
  remain as proposed? Is the agent getting better or accumulating debt?
- **Top 3 recommendations**: the single most impactful thing to do next, ranked.

## Persisted
  Memories written: <count>
  Repos added to database: <count>
  Manifest: $DATA_DIR/<agent>/manifest.json
```

If `$DRY_RUN`, return the same format but under "Findings (dry-run):" headers
and do not edit any files, clone repos, or write to the database.
