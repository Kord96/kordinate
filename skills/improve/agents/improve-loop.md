# Improve Loop — Per-Agent Prompt

Prompt for each team agent launched by `/improve all`. Each agent is
spawned as its own `subagent_type` so it brings domain expertise and memories.

## Setup

Run `/boot` first to load your memories and context.

## Input

- `$SKILL_PATHS` — list of skill directories to improve (all belong to you)
- `$MAX_ITERATIONS` — hard cap per skill (default: 3)
- `$DRY_RUN` — if true, report findings without editing

Process each skill in `$SKILL_PATHS` sequentially, running the iteration loop below
on each one before moving to the next.

## Iteration Loop

For each iteration (1 to `$MAX_ITERATIONS`):

### Step 1 — Read

Read `$SKILL_PATH/SKILL.md` and all supporting files in `$SKILL_PATH/`. Also read
the agent's other skills for cross-reference (are there overlaps, inconsistencies?).

### Step 2 — Review

Evaluate the skill against these criteria:

| Category | What to look for |
|----------|-----------------|
| **Completeness** | Missing steps, undefined terms, gaps between steps where an implementer would be stuck |
| **Correctness** | Wrong commands, incorrect flags, outdated references, steps that would fail |
| **Clarity** | Ambiguous instructions, unclear conditionals, missing context for decisions |
| **Consistency** | Naming mismatches with other skills, inconsistent formatting, frontmatter issues |
| **Actionability** | Steps that say "handle X" without saying how, vague verbs like "process" or "manage" |

Do NOT look for:
- Style preferences (Oxford commas, heading levels, bullet vs number)
- Missing features the skill doesn't claim to have
- Hypothetical edge cases that don't arise in practice

### Step 3 — Classify and decide

If you found issues, classify them:

- **Structural** — missing steps, wrong commands, logical gaps, incorrect information,
  incomplete output specifications. These materially affect whether someone following
  the skill would succeed.
- **Cosmetic** — rewording for clarity without changing meaning, reformatting tables,
  reordering sections, fixing typos.

Decision:
- If no issues found → stop, report "no-changes"
- If only cosmetic issues → apply them, then stop, report "cosmetic-only"
- If structural issues → apply fixes, continue to next iteration

### Step 4 — Apply changes

Edit the skill files to address the structural issues. Make the minimum change needed
to fix each issue — don't rewrite surrounding paragraphs or restructure sections
unless the structure itself is the problem.

### Step 5 — Anti-oscillation check

Before committing to the changes, compare your diff against diffs from previous
iterations. If you are reverting or undoing a change you made in a prior iteration,
discard your changes for this iteration, stop, and report "revert-detected".

### Step 6 — Log iteration

Record for the final summary:
- Iteration number
- Classification (structural / cosmetic / no-changes)
- One-line summary of each change made

Then proceed to the next iteration (or stop if conditions are met).

## Output

Return a structured summary covering all skills processed:

```
Agent: <agent-name>

Skill: <skill-name>
Iterations: <N>/<MAX>
Stop reason: no-changes | cosmetic-only | revert-detected | max-iterations
Changes:
- [iteration 1] (structural) Added missing verification step after kubectl apply
- [iteration 2] (cosmetic) Clarified wording in secrets section — stopping

Skill: <skill-name>
Iterations: <N>/<MAX>
Stop reason: no-changes
Changes: —
```

If `$DRY_RUN`, return the same format but under a "Findings (dry-run):" header
instead of "Changes:", and do not edit any files.
