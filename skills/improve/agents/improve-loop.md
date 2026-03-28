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
git clone --depth 1 https://github.com/<nameWithOwner>.git /tmp/improve-repos/<owner>--<name>
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

### Step 1.7 — Portfolio Decision

Classify each finding:

- **Immediate** — can be done during this improve run: staleness fixes, resource additions,
  minor refactoring, supporting file improvements. Execute these in Phase 2.
- **Proposed** — requires human approval: new skills, agent reassignment, major splits/merges,
  fundamental restructuring. Record for the summary.

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

### Step 2.2 — Test Against Real Repos

If test repos were cloned in Step 1.5, run the skill (or simulate its procedure) against
one of the cloned repos. Evaluate:

- Does the skill produce the expected output?
- Are there steps that fail or get stuck on real code?
- Does the skill handle the repo's structure correctly?
- Are there edge cases the skill doesn't account for?

Record results to `$DATA_DIR/<agent>/test-results/<skill>-<repo>.json`:
```json
{
  "skill": "<name>",
  "repo": "<nameWithOwner>",
  "tested_at": "ISO-8601",
  "success": true,
  "issues_found": [],
  "notes": ""
}
```

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

### Step 3.2 — Persist Portfolio Findings

For each finding classified as "proposed" (needs human approval), save to memory:
```
<agent-name> portfolio review: <finding description>
```

For domain insights discovered during improvement, save to memory:
```
<agent-name> learned during self-improvement: <insight>
```

Use the `write_memory` tool for each entry.

### Step 3.3 — Finalize Manifest

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

## Persisted
  Memories written: <count>
  Repos added to database: <count>
  Manifest: $DATA_DIR/<agent>/manifest.json
```

If `$DRY_RUN`, return the same format but under "Findings (dry-run):" headers
and do not edit any files, clone repos, or write to the database.
