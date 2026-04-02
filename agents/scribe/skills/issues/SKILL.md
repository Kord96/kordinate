---
name: issues
description: >
  Create GitHub Issues from augur's analysis findings. Reads atlas + stories,
  deduplicates against existing issues, classifies as bug/enhancement/suggestion,
  and presents a proposed list for confirmation before creating.
argument-hint: "<project> [--dry-run] [--auto]"
context: inherit
---

Create GitHub Issues from augur's analysis output. Reads violations, recommendations, failure modes, gaps, and story observations. Deduplicates against existing GitHub issues. Classifies each finding and presents for user confirmation before creating.

## Arguments

`$ARGUMENTS` — Required: `<project>` (project directory path or name). Optional: `--dry-run` (show proposed issues without creating), `--auto` (skip confirmation, create all proposed issues).

---

## Procedure

### Step 1 — Resolve project and repo

Resolve the project directory using the same rules as augur: `~/<project>/`, `~/repos/<project>/`, `~/test-repos/<project>/`, `/kord/projects/<project>/`, or absolute path. Confirm it exists.

Detect the GitHub repo by running `gh repo view --json nameWithOwner -q .nameWithOwner` from the project directory. If no repo is found, report and exit.

### Step 2 — Load augur findings

Read augur output from `$MEM/` (augur's project memory):

| Source | File |
|--------|------|
| Atlas | `atlas.json` — violations, recommendations, failure_modes, gaps |
| Stories | `stories/*.yaml` — observations from each story |

If atlas.json is missing, suggest running `/analyze <project>` first. Exit.

Extract all actionable findings into a flat list. Each finding gets:

| Field | Source |
|-------|--------|
| `source_id` | `augur:<type>:<id>` (e.g., `augur:violation:no-timeout`, `augur:observation:obs-no-form-validation`) |
| `title` | From finding title/anti_pattern/id |
| `body` | Description, evidence, affected files, recommendation |
| `classification` | Determined in Step 4 |
| `labels` | Determined in Step 4 |

### Step 3 — Load existing GitHub issues

Fetch open issues from the repo:
```bash
gh issue list --repo <owner/repo> --state open --limit 200 --json number,title,body,labels
```

Also fetch recently closed issues (last 30 days) to avoid re-filing resolved items:
```bash
gh issue list --repo <owner/repo> --state closed --limit 100 --json number,title,body,labels
```

### Step 4 — Classify and deduplicate

**Classification rules:**

| Augur source | Severity/type | Classification | Labels |
|---|---|---|---|
| `debt.violations` | CRITICAL or HIGH | `bug` | `bug`, `priority:high` |
| `debt.violations` | RECOMMENDED or LOW | `enhancement` | `enhancement`, `debt` |
| `debt.recommendations` | any | `enhancement` | `enhancement`, `debt` |
| `failure_modes` | critical or high | `bug` | `bug`, `reliability` |
| `failure_modes` | medium or low | `enhancement` | `enhancement`, `reliability` |
| `concepts.gaps` | — | `suggestion` | `suggestion`, `gap` |
| Story observations | has recommendation | `enhancement` | `enhancement`, `observation` |
| Story observations | informational only | skip | — |

**Skip rules** — do NOT create issues for:
- Observations without a recommendation (purely informational)
- Findings about expected demo/test behavior (e.g., "simulated checkout" in a demo app)
- Observations with `confidence: low`

**Deduplication** — for each finding, check if an existing issue already covers it:
1. Search existing issue titles for similar keywords (fuzzy match — at least 2 significant words overlap)
2. Search existing issue bodies for the `source_id` string (exact match from prior runs)
3. Search existing issue bodies for the same file paths mentioned in the finding

If a match is found, mark the finding as `duplicate` with the matching issue number. Do not create it.

### Step 5 — Present proposed issues

Format the proposal as a table:

```
## Proposed Issues for <project>

### Will create (N)

| # | Type | Title | Files | Labels |
|---|------|-------|-------|--------|
| 1 | bug | Add timeout to DummyJSON API client | app/api.ts | bug, priority:high |
| 2 | enhancement | Add form validation to checkout | shipping-form.tsx, payment-form.tsx | enhancement, debt |
| ... | ... | ... | ... | ... |

### Skipped — duplicates (N)

| Title | Matches issue |
|-------|---------------|
| ... | #42 |

### Skipped — informational (N)

| Title | Reason |
|-------|--------|
| Simulated checkout action | Demo app — expected behavior |
```

If `--dry-run`: stop here, do not create issues.

If not `--auto`: wait for user confirmation before proceeding. The user may ask to remove items, change classifications, or edit titles.

### Step 6 — Create issues

For each confirmed finding, create a GitHub issue:

```bash
gh issue create --repo <owner/repo> --title "<title>" --body "$(cat <<'EOF'
## Finding

<description>

## Affected files

<file list as code blocks>

## Recommendation

<recommendation text>

## Evidence

<grounded_in references, code snippets if available>

---

<sub>Source: `<source_id>` | Generated by [augur](https://github.com/kord-network/kordinate) analysis</sub>
EOF
)" --label "<label1>,<label2>"
```

**Label creation**: before creating issues, check if required labels exist. Create any missing labels:
```bash
gh label create "<label>" --repo <owner/repo> --description "<desc>" --color "<hex>" 2>/dev/null || true
```

Label colors:
- `bug`: `d73a4a`
- `enhancement`: `a2eeef`
- `suggestion`: `c5def5`
- `debt`: `fbca04`
- `reliability`: `e4e669`
- `priority:high`: `b60205`
- `gap`: `d4c5f9`
- `observation`: `bfdadc`

### Step 7 — Report

```
## Issues: <project>

**Repo**: <owner/repo>
**Created**: N issues (N bugs, N enhancements, N suggestions)
**Skipped**: N duplicates, N informational
**Labels**: N created, N existing

Issues:
  #<number> — <title> [<labels>]
  #<number> — <title> [<labels>]
  ...
```
