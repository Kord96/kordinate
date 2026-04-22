# Audit Loop — Per-Agent Prompt

Prompt for each team agent launched by `/audit <target> --mode loop`.
Each agent is spawned as its own `subagent_type` so it brings domain expertise and memories.

## Setup

Run `/boot` first to load your memories and context.

## Input

- `$SKILL_PATHS` — list of skill directories to audit and refine (all belong to you)
- `$IDENTITY_PATH` — path to the agent's IDENTITY.md
- `$MAX_ITERATIONS` — hard cap per skill (default: 3)
- `$DRY_RUN` — if true, report findings without editing
- `$DATA_DIR` — persistent storage root (default: `/data/audit`)

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

Kick off a single web search for inspiration. This runs once per audit-loop invocation,
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
| **Resource extraction** | Does any SKILL.md contain methodology or reference material that should be its own supporting file? A SKILL.md should be orchestration (what to do in what order), not methodology (how to do each thing). If a section could be loaded independently, it should be a separate file. |
| **Resource unification** | Are any supporting files duplicating content across skills? Do small files (<60 lines) that are always used together belong in one file? Does any supporting file repeat content from another instead of referencing it? |
| **Quality of thought** | Do my skills explain *why* behind their instructions, or do they just list rigid steps? Would an intelligent agent understand the reasoning? |

Check your memory (loaded at boot) for evidence. Past scratchpad entries about recurring
manual work, failed approaches, or workarounds are signals for gaps.

### Step 1.4 — Clone Test Repos

Always clone **fresh repos** — never reuse repos from previous runs. Testing against the same repos repeatedly causes overfitting to their specific patterns. Fresh repos expose new edge cases, new concept gaps, and new architectural styles.

Use GitHub CLI to find candidates:

```bash
gh search repos --language=<relevant-lang> --stars=100..5000 --sort=updated --limit=10 \
  --json nameWithOwner,description,primaryLanguage,stargazerCount
```

Pick 2-3 repos that are likely to exercise your skills (e.g., for an architecture agent, pick repos with clear design patterns across different stacks).

Check the repo index to exclude all previously tested repos:

```bash
python3 $KORDINATE_HOME/shared/scripts/repo-index.py check <nameWithOwner>
```

Exit code 0 = already exists (skip it). Exit code 1 = new repo (use it). Clone and register new repos via the index script:

```bash
python3 $KORDINATE_HOME/shared/scripts/repo-index.py add <nameWithOwner> <language> --tested-by <agent-name>
```

This clones to `/data/repos/<owner>--<name>` and updates `/data/repos/index.json` in one step.

Record each repo in the manifest's `test_repos` array:
```json
{"nameWithOwner": "owner/repo", "language": "python", "stars": 1200, "cloned_at": "ISO-8601"}
```

### Step 1.5 — Incorporate External Input

Read results from Step 1.2 (web search):

- **Web research**: extract specifically relevant patterns or community approaches. Tag
  findings as `source: research` so they are distinguishable from self-assessment.

### Step 1.6 — Check Improvement History

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

1. Skip Phase 2 entirely — there is nothing new to refine.
2. Go directly to Phase 3 (Sleep) to update history with the plateau observation.
3. Report: "Portfolio stable — no new findings in N consecutive runs. Stopping early."

This prevents burning tokens re-reviewing skills that haven't changed. The plateau
breaks when: the agent's identity changes, new skills are added externally, or a
skill file is edited outside the audit loop.

### Step 1.8 — Portfolio Decision

Classify each finding:

- **Immediate** — can be done during this audit run: staleness fixes, resource additions,
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
| **Analyze** (augur /analyze) | Run the full procedure. Save atlas.json, stories/*.yaml, narratives.yaml |
| **Scan** (sauron /monitor, warden /scan-secrets) | Run the full procedure. Save the output artifact |
| **Transform** (edit-based skills) | Dry-run on a copy of the repo. Save proposed changes as a patch |
| **Deploy/infra** | Skip — trace the procedure mentally instead |
| **Meta** (improve, train-detection) | Skip — these are tested by running them |

#### 2.2b — Build Ground Truth

For each skill output, build independent ground truth to compare against. Use multiple
oracles to avoid circularity (the agent both running the skill AND judging its own output
is circular). At least two oracles must agree for high-confidence ground truth.

**Oracle 1 — Mechanical verification.** Use grep/glob/AST to independently verify
specific claims:

| Output | Mechanical checks |
|--------|------------------|
| **atlas components** | Verify every component's `modules[]` paths exist. Grep for imports to confirm `depends_on` edges. |
| **atlas flows** | Verify `grounded_in` file:line references exist. Trace step sequences via import chains. |
| **atlas concepts** | Grep for import statements, decorators, config files that confirm/deny each detected concept. Run ast-grep rules to cross-check. |
| **atlas API surface** | Grep for route decorators (`@app.get`, `@router.post`, `http.HandleFunc`) — does endpoint count match? |
| **atlas debt** | Verify cited files exist. Grep for flagged patterns (`TODO`, hardcoded strings, bare excepts). |
| **atlas state** | Verify `readers`/`writers` component IDs exist. Check `grounded_in` references. |
| **stories** | Every `**bold ref**` resolves to an atlas node ID. Every `grounded_in` file exists. Structure node IDs exist in atlas. |
| **narratives** | Every story ID in each narrative exists in `stories/`. Order makes pedagogical sense (doesn't reference concepts before they're introduced). |

**Oracle 2 — Schema compliance.** Validate the output against the v4 schema:

- Run `python3 $KORDINATE_HOME/agents/augur/skills/analyze/validator/validate.py` on atlas.json
- Check: version is "4", 3-5 groups, 5-10 components, flow types are valid enum values
- Check: all cross-references resolve (component IDs in flows, state readers/writers, failure cascade components)
- Check: `grounded_in` references on flows, state, and failure_modes are present
- Check: stories have required `summary` block, valid `parent`/`children` tree structure
- Check: narratives reference valid story IDs, have 3-8 stories each

**Oracle 4 — Story and narrative quality.** Assess the narrative output:

| Dimension | What to check |
|-----------|--------------|
| **Story groundedness** | Does each story's `evaluation.groundedness` score >= 0.85? For scores below, which claims are ungrounded? |
| **Story coverage** | Are all critical atlas nodes (components + critical external deps + source-of-truth state) referenced in at least one story? |
| **Story tree coherence** | Does each child story zoom into a subset of its parent's nodes? Do children reference fewer nodes than parents? |
| **Story summary quality** | Are summaries scenario-driven (not passive descriptions)? Do they lead with action? Are they within word limits (root: 50-80, child: 80-120)? |
| **Narrative teaching order** | Does the getting-started narrative build understanding progressively? Would a reader at story N have enough context from stories 1..N-1? |
| **Narrative coverage** | Does getting-started touch all atlas groups? Are there groups with no story in any narrative? |
| **Observation attachment** | Are observations attached to the right nodes/steps (not just story-wide when they could be specific)? |
| **Rationale presence** | Do stories about non-obvious architectural choices include rationale blocks? |

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

For outputs where items aren't countable, score on a rubric:

**Atlas rubric:**

| Dimension | 1 (poor) | 3 (adequate) | 5 (excellent) |
|-----------|----------|-------------|--------------|
| **Completeness** | Major components missing | Most components present, some gaps | All components identified |
| **Accuracy** | Multiple hallucinated components | Minor inaccuracies | All claims verifiable in code |
| **Specificity** | Vague descriptions, no file refs | Some file refs, some vague | Every claim cites specific files via `grounded_in` |
| **Schema compliance** | Missing required sections, wrong types | Minor schema issues | Passes validator with zero errors |
| **Flow typing** | Flows untyped or wrong type | Most flows correctly typed | Every flow uses the right category with correct step fields |

**Story rubric:**

| Dimension | 1 (poor) | 3 (adequate) | 5 (excellent) |
|-----------|----------|-------------|--------------|
| **Groundedness** | < 0.70 | 0.70-0.85 | >= 0.85 |
| **Coverage** | Major components undocumented | Most covered, some gaps | >= 0.80 of critical nodes covered |
| **Tree coherence** | Children don't zoom in, random scoping | Most children scope correctly | Every child is a clean subset of parent |
| **Summary quality** | Passive, verbose, no action | Adequate but generic | Scenario-driven, leads with action, within word limits |
| **Observation placement** | All story-wide, none attached | Some attached to nodes/steps | Observations attached at the most specific applicable level |

**Narrative rubric:**

| Dimension | 1 (poor) | 3 (adequate) | 5 (excellent) |
|-----------|----------|-------------|--------------|
| **Teaching order** | Random or alphabetical | Reasonable but some gaps | Progressive — each story builds on prior context |
| **Group coverage** | Misses multiple groups | Most groups touched | All atlas groups represented |
| **Audience fit** | Generic, no clear audience | Audience stated but stories not tailored | Stories clearly selected and ordered for the stated audience |
| **Length** | < 3 or > 8 stories | 3-8 stories | Right number for the concern — neither rushed nor padded |

#### 2.2d — Record Results

Save to `$DATA_DIR/<agent>/test-results/<skill>-<repo>.json`:

```json
{
  "skill": "<name>",
  "repo": "<nameWithOwner>",
  "tested_at": "ISO-8601",
  "ground_truth": {
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

**For augur's `/analyze` specifically**, also ask:

| Category | What to look for |
|----------|-----------------|
| **Concept coverage** | Did the test run detect patterns that have no concept file? Should new concepts be created? |
| **Detection gaps** | Were patterns visible in the code but missed by all 3 detection steps? What grep keywords, AST rules, or questions would catch them? |
| **AST rule quality** | Did any ast-grep rules produce false positives? Did rules fail to parse? Should new rules be written for high-value concepts that currently rely on grep only? |
| **Question quality** | Did diagnostic questions produce the right answer? Were any questions misleading or ambiguous? Should signal hints be added or refined? |
| **New concept proposals** | Did the test repo exhibit patterns not in the catalog at all? Propose new concept files with type, signatures, and questions. |
| **Schema compliance** | Does the atlas output pass the v4 validator? Are new atlas sections (observability, security, devex) populated when the code has them? |
| **Story grounding** | Are story claims traceable to atlas findings? Do `grounded_in` references point to real files? |
| **Narrative coherence** | Does the getting-started narrative cover all groups? Does the teaching order make sense? |

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

### Step 2.5b — Anti-oscillation check

Before committing to the changes, compare your diff against diffs from previous
iterations. If you are reverting or undoing a change you made in a prior iteration,
discard your changes for this iteration, stop, and report "revert-detected".

### Step 2.6 — Validate Behavior on Tests

Re-run the tests from Step 2.2 that exercise the changed behavior. Confirm the skill now
produces the expected output on the same repo(s) that exposed the issue. If the change was
structural rather than behavioral, verify the procedure still executes cleanly end-to-end.

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

### Step 3.1 — Update Repo Index

Mark all tested repos in the central index:

```bash
python3 $KORDINATE_HOME/shared/scripts/repo-index.py mark-tested <nameWithOwner> <agent-name>
```

This updates `/data/repos/index.json` so future audit runs know which repos have been tested and by whom. If the repo was already added via `repo-index.py add` during Step 1.5, it's already registered — this just adds the agent to `tested_by`.

### Step 3.2 — Write Run Report

Write a detailed run report to `$DATA_DIR/<agent>/runs/<run_id>.json`. This is the permanent record — every number, every change, every finding. One file per run, never overwritten.

```json
{
  "run_id": "<timestamp>",
  "date": "YYYY-MM-DD",
  "duration_minutes": 45,
  "status": "complete | plateau | failed",

  "repos_tested": [
    {
      "nameWithOwner": "owner/repo",
      "language": "python",
      "stars": 1200,
      "files_scanned": 87,
      "loc": 12400
    }
  ],

  "detection_scores": {
    "<repo>": {
      "concepts": {"precision": 0.88, "recall": 0.74, "f1": 0.80, "true_positives": 14, "false_positives": 2, "false_negatives": 5},
      "components": {"precision": 0.90, "recall": 0.82, "f1": 0.86, "count_expected": 11, "count_produced": 10},
      "flows": {"precision": 1.00, "recall": 0.67, "f1": 0.80, "count_expected": 3, "count_produced": 2},
      "api_endpoints": {"precision": 0.95, "recall": 0.80, "f1": 0.87, "count_expected": 20, "count_produced": 19},
      "debt_items": {"precision": 0.85, "recall": 0.60, "f1": 0.70, "count_expected": 10, "count_produced": 7}
    }
  },

  "story_scores": {
    "groundedness": {"min": 0.85, "max": 0.95, "avg": 0.90},
    "coverage": 0.82,
    "total_stories": 12,
    "root_stories": 4,
    "child_stories": 8
  },

  "narrative_scores": {
    "getting_started": {"story_count": 6, "groups_covered": 4, "groups_total": 4},
    "additional_narratives": 1
  },

  "schema_validation": {
    "passed": true,
    "errors": [],
    "warnings": ["observability section empty — flagged as gap"]
  },

  "changes_made": [
    {
      "iteration": 1,
      "type": "structural",
      "description": "Added bounded context detection to Phase 1 checklist",
      "files_changed": ["SKILL.md"],
      "lines_added": 12,
      "lines_removed": 3
    }
  ],

  "new_concepts_proposed": [
    {
      "name": "connection-draining",
      "type": "pattern",
      "evidence": "Found in owner/repo at src/server.py:45 — graceful shutdown drains connections before exit",
      "created": true
    }
  ],

  "detection_improvements": [
    {
      "concept": "circuit-breaker",
      "change": "Added tenacity library signature to grep keywords",
      "before_recall": 0.60,
      "after_recall": 0.80
    }
  ],

  "portfolio_findings": {
    "coverage_gaps": [],
    "staleness_fixes": [],
    "resource_additions": [],
    "proposed_actions": []
  }
}
```

Create the `runs/` directory if it doesn't exist.

### Step 3.3 — Update History Index

Append a summary line to `$DATA_DIR/<agent>/history.json` for quick trend analysis. This is the lightweight index — the full data is in `runs/<run_id>.json`.

```json
{
  "run_id": "<timestamp>",
  "date": "YYYY-MM-DD",
  "repos_tested": 2,
  "avg_f1": {"concepts": 0.80, "components": 0.86, "flows": 0.80},
  "story_coverage": 0.82,
  "story_groundedness_avg": 0.90,
  "changes_count": 3,
  "new_concepts": 1,
  "detection_improvements": 1,
  "stop_reason": "cosmetic-only",
  "status": "complete"
}
```

Create as `[]` if it doesn't exist. Append. Keep the last 50 entries.

### Step 3.4 — Persist Portfolio Findings

For each finding classified as "proposed" (needs human approval):
```
/kord remember <agent-name> portfolio review: <finding description>
```

For domain insights discovered during improvement:
```
/kord remember <agent-name> learned during self-improvement: <insight>
```

### Step 3.5 — Commit and Push

Commit all changes and push the branch explicitly. This does **not** update `main`.

```bash
git -C $KORDINATE_HOME add -A
git -C $KORDINATE_HOME commit -m "audit: <agent> — <one-line summary of changes>"
git -C $KORDINATE_HOME push 2>/dev/null || true
```

When the branch is ready to land, run `/integrate` explicitly.

### Step 3.6 — Finalize Manifest

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
