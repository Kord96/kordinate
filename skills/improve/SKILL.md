---
name: improve
description: Improve skills, agents, or the whole team — run evals, benchmark, iterate, and optimize. Use for skill quality testing, A/B benchmarks, iterative improvement loops, or description optimization.
argument-hint: "skill <name> | agent <name> | all | optimize <skill> | audit [--fix] | benchmark <skill>"
curated: true
scope: global
---

Improve skills, agents, or the whole team. Combines static quality analysis, eval-driven testing, benchmarking, and iterative improvement loops.

## Subcommands

| Subcommand | Command | Purpose |
|------------|---------|---------|
| `skill` | `/improve skill <name>` | Eval + iterate on one skill |
| `agent` | `/improve agent <name>` | Improve-loop on all of an agent's skills |
| `all` | `/improve all` | Improve-loop across all agents |
| `optimize` | `/improve optimize <skill>` | Optimize description for triggering accuracy |
| `audit` | `/improve audit [--fix]` | Static quality checks on skills |
| `benchmark` | `/improve benchmark <skill>` | Multi-run benchmark with variance |

Common flags: `--skill <name>`, `--agent <name>`, `--fix` (audit mode only).

If a required argument is missing (e.g. `skill` without a skill name), prompt the user for it rather than guessing. If the target skill path does not exist or has no SKILL.md, report the error clearly and exit.

---

## Subcommand: audit

Static analysis of all SKILL.md files for quality, completeness, and best practices. Read-only by default.

### Procedure

1. **Parse arguments** — defaults: read-only, scan all agents and global skills. Restrict with `--agent` or `--skill`.

2. **Discover skills** — find every `SKILL.md` under `$KORDINATE_HOME/agents/*/skills/` and `$KORDINATE_HOME/skills/`. Build inventory: skill name, agent, path, file size.

3. **Run per-skill checks** — for each skill, run the Structure, Quality, and Security checks in [checks.md](checks.md):
   - **Structure** — frontmatter presence, required fields, file organization
   - **Quality** — description clarity, instruction completeness, supporting files
   - **Security** — tool restrictions, invocation control, argument validation

4. **Run cross-reference checks** — after all skills are scanned, run the Cross-reference checks in [checks.md](checks.md): name collisions, orphaned supporting files, description budget overflow.

5. **Group findings** by severity (`ERROR` > `WARNING` > `INFO`), then agent, then skill.

6. **Output report** — structured table with summary counts, per-skill findings, and a "Quick wins" section.

7. **Fix mode** (`--fix`) — apply safe corrections: add missing frontmatter, add argument-hints. Never change skill logic. Show diffs before applying.

### Rules

- Default is read-only — never modify files without `--fix`.
- `ERROR` = broken. `WARNING` = degraded. `INFO` = improvement opportunity.

---

## Subcommand: skill

Run a skill against test prompts and grade the results, then iterate to improve it.

### Procedure

1. **Locate the skill** — resolve `<skill>` to its SKILL.md path. If it has existing `evals/evals.json`, use those. Otherwise, create test cases.

2. **Create test cases** (if needed) — write 2-3 realistic test prompts. Save to `<skill>-workspace/evals/evals.json`. See [references/schemas.md](references/schemas.md) for the schema. Don't write assertions yet — just prompts.

3. **Spawn runs** — for each test case, spawn two subagents in the same turn:
   - **With-skill**: execute the prompt with the skill loaded. Save outputs to `<workspace>/iteration-1/eval-<ID>/with_skill/outputs/`.
   - **Baseline**: same prompt, no skill. Save to `without_skill/outputs/`.

4. **Draft assertions** while runs are in progress — write verifiable expectations for each test case. Update `evals.json`.

5. **Capture timing** — when each subagent completes, save `total_tokens` and `duration_ms` to `timing.json` immediately. This data is only available from the task notification.

6. **Grade** — spawn a grader subagent using [agents/grader.md](agents/grader.md) for each run. Save `grading.json` per run. For assertions checkable programmatically, write and run a script.

7. **Aggregate** — run:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-1 --skill-name <name>
   ```
   Produces `benchmark.json` and `benchmark.md`.

8. **Analyze** — read benchmark data and surface patterns per [agents/analyzer.md](agents/analyzer.md): non-discriminating assertions, high-variance evals, time/token tradeoffs.

9. **Launch viewer**:
   ```bash
   python ${CLAUDE_SKILL_DIR}/eval-viewer/generate_review.py <workspace>/iteration-1 --skill-name "<name>" --benchmark <workspace>/iteration-1/benchmark.json
   ```
   For headless environments, use `--static <output_path>` for standalone HTML.

10. **Report** — present findings. Tell the user to review in the viewer.

11. **Collect feedback** — read `feedback.json` from the viewer. Empty feedback = looks good.

12. **Improve the skill** based on feedback. Key principles:
    - **Generalize** from feedback — don't overfit to test cases. Use different metaphors or patterns rather than adding rigid constraints.
    - **Keep it lean** — read transcripts to find unproductive steps. Remove what isn't pulling its weight.
    - **Explain the why** — explain reasoning instead of heavy-handed MUSTs. Models with good theory of mind respond better to understanding than to commands.
    - **Bundle repeated work** — if test transcripts all independently write similar scripts, bundle that script into the skill's `scripts/` directory.

13. **Rerun** into `iteration-<N+1>/`. Launch viewer with `--previous-workspace` pointing at prior iteration.

14. **Repeat** until: user is satisfied, feedback is empty, or improvements plateau.

### Blind comparison (optional)

For rigorous A/B testing between two skill versions:
1. Spawn blind comparator per [agents/comparator.md](agents/comparator.md) — judges output quality without knowing which skill produced it.
2. Run post-hoc analysis per [agents/analyzer.md](agents/analyzer.md) — unblinds results and generates improvement suggestions.

---

## Subcommand: agent

Run the full improve loop on an agent: portfolio review, per-skill iteration with real-repo testing, and memory persistence. The agent boots with its own domain knowledge and evaluates whether its skills serve its identity.

### Procedure

1. **Discover skills** — find all SKILL.md files under the agent's skills directory.
2. **Resolve identity** — locate the agent's IDENTITY.md.
3. **Spawn improve loop** — spawn a subagent using the prompt in [agents/improve-loop.md](agents/improve-loop.md) with `$SKILL_PATHS`, `$IDENTITY_PATH`, `$MAX_ITERATIONS`, and `$DATA_DIR` (`/data/improve`). The agent brings its own domain expertise, memories, and identity awareness.
4. **The agent executes three phases**:
   - **Phase 1 — Portfolio Review**: loads identity, inventories skills, launches background web research and Gemini peer review, analyzes alignment/gaps/splits/merges/staleness/resources, clones test repos, incorporates external input, classifies findings as immediate or proposed.
   - **Phase 2 — Per-Skill Iteration**: for each skill, tests against cloned repos, reviews against quality criteria plus portfolio findings, applies structural fixes, checks for oscillation.
   - **Phase 3 — Sleep**: updates the repo database at `$DATA_DIR/repo-database.json`, persists portfolio findings and domain insights to memory via `/kord remember`, finalizes the manifest.
5. **Report** — the agent returns a structured summary covering portfolio findings, test repos used, per-skill iteration results, and what was persisted.

### Progress Tracking

The agent writes a manifest to `$DATA_DIR/<agent>/manifest.json` that survives context compaction. If the main agent loses track after compaction, read the manifest to recover state.

---

## Subcommand: all

Improve-loop across all agents. Spawns each team agent to improve its own skills portfolio.

### Procedure

1. **Discover agents** — find all agents with skills directories and IDENTITY.md files.
2. **Spawn per-agent improve loops** — for each agent, spawn a subagent using the prompt in [agents/improve-loop.md](agents/improve-loop.md). Each agent boots with its domain expertise and memories, then runs the full 3-phase loop (portfolio review → per-skill iteration → sleep). Limit concurrency to 2 agents at a time.
3. **Monitor via manifests** — each agent writes progress to `$DATA_DIR/<agent>/manifest.json`. After context compaction, read these manifests to recover the state of all running agents.
4. **Collect results** — aggregate summaries from all agents.
5. **Cross-agent reconciliation** — after all agents report, resolve conflicts that no single agent can see:
   - **Misplacement conflicts**: if agent A says "skill X belongs to agent B" and agent B didn't claim it, flag for human review.
   - **Overlap resolution**: if agents A and B both cover the same domain, propose which agent should own it (based on identity alignment) or whether the skills should be merged.
   - **Shared resource gaps**: if multiple agents flag the same missing resource (e.g., a shared script, a common schema), propose creating it once in `$KORDINATE_HOME/shared/` rather than duplicating per-agent.
   - **Coverage map**: produce a matrix of responsibilities × agents showing which are covered, which have gaps, and which have redundant coverage.

   This step runs in the orchestrator (the main improve agent), not in the per-agent subagents.

---

## Subcommand: benchmark

Multi-run benchmark with variance analysis. Like `skill` but runs each test case multiple times (default 3) per configuration.

### Procedure

1. **Locate skill and evals** — same as skill mode. Evals must have assertions.

2. **Run N times per config** — spawn `runs_per_configuration` (default 3) runs for each test case in both `with_skill` and `without_skill` configs. Launch all in parallel.

3. **Grade all runs** — use [agents/grader.md](agents/grader.md).

4. **Aggregate** — produces `run_summary` with mean, stddev, min, max per metric per configuration, plus delta.

5. **Analyze** — surface per-assertion patterns, cross-eval patterns, metrics patterns.

6. **Launch viewer** with benchmark data.

7. **Report** — highlight delta between with-skill and baseline, flag high-variance results.

---

## Subcommand: optimize

Optimize a skill's description for triggering accuracy.

### Procedure

1. **Generate trigger eval queries** — create 20 queries: ~10 should-trigger, ~10 should-not-trigger. Save as `trigger-eval.json`. See [references/schemas.md](references/schemas.md).

   Queries must be realistic — concrete, specific, with file paths, context, casual speech. Focus on edge cases. Near-miss negatives are most valuable (share keywords but need something different).

2. **Review with user** — present queries using the HTML template at [assets/eval_review.html](assets/eval_review.html). Replace `__EVAL_DATA_PLACEHOLDER__`, `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`. Write to temp file and open.

3. **Run optimization loop** in background:
   ```bash
   python -m scripts.run_loop \
     --eval-set <trigger-eval.json> \
     --skill-path <skill-path> \
     --model <current-model-id> \
     --max-iterations 5 \
     --verbose
   ```
   This splits 60/40 train/test, evaluates current description (3x per query), proposes improvements, iterates up to 5 times. Selects best by test score to avoid overfitting.

4. **Apply result** — take `best_description` from output and update the skill's SKILL.md frontmatter. Show before/after and report scores.

---

## Skill Writing Guide

When improving skills (in `skill`, `agent`, `all`, or `audit --fix` modes), follow these principles:

### Structure
- Keep SKILL.md under 500 lines. Move reference material to supporting files.
- Use progressive disclosure: metadata (always loaded) -> SKILL.md body (on trigger) -> supporting files (on demand).
- Reference supporting files clearly with guidance on when to read them.

### Descriptions
- Include both what the skill does AND specific contexts for when to use it.
- Make descriptions slightly "pushy" — Claude tends to undertrigger, so include extra context about when the skill applies.
- Avoid vague terms. Be specific about the task domain.

### Instructions
- Use imperative form.
- Explain the why behind instructions — models respond better to understanding than rigid rules.
- Avoid ALWAYS/NEVER in all caps; reframe as reasoning.
- Include examples with input/output pairs.

### Frontmatter
Required (Claude-native): `name`, `description`. Optional: `argument-hint` (when args accepted).

Recall property: `curated: true` (protects skill files via guard). Do not put `scope` on skills — scope is determined by file path (`~/.kord/` = global, `.kord/` = project).

Use `disable-model-invocation: true` for destructive/deployment skills. Use `allowed-tools` to restrict read-only skills. Use `context: fork` for heavy analysis that could overflow context.

---

## Reference Files

- [checks.md](checks.md) — Static audit check registry (20 checks across 4 categories)
- [agents/grader.md](agents/grader.md) — Grading agent for evaluating skill outputs
- [agents/comparator.md](agents/comparator.md) — Blind A/B comparison agent
- [agents/analyzer.md](agents/analyzer.md) — Post-hoc analysis and benchmark analysis agent
- [agents/improve-loop.md](agents/improve-loop.md) — Per-agent improve prompt for `all` mode
- [references/schemas.md](references/schemas.md) — JSON schemas for evals, grading, benchmark, comparison, analysis
- `eval-viewer/` — `generate_review.py` + `viewer.html` for interactive result review
- `assets/eval_review.html` — Template for trigger eval query review

### Scripts

Python utilities in `scripts/`. Run via `python -m scripts.<name>` from the skill directory.

| Script | Purpose |
|--------|---------|
| `run_eval.py` | Run trigger evaluation: tests whether a description causes Claude to invoke the skill for a set of queries |
| `run_loop.py` | Orchestrate the optimize mode: eval + improve loop with train/test split and live HTML report |
| `improve_description.py` | Generate an improved description by calling Claude with eval failures and history |
| `aggregate_benchmark.py` | Aggregate grading.json files from benchmark runs into summary statistics (mean, stddev, delta) |
| `generate_report.py` | Generate standalone HTML report from run_loop output showing per-iteration results |
| `quick_validate.py` | Minimal frontmatter validation: checks name, description, allowed properties |
| `package_skill.py` | Package a skill directory into a distributable .skill zip file |
| `utils.py` | Shared helper: `parse_skill_md()` extracts name, description, and content from SKILL.md frontmatter |
