---
name: install
description: Install or reinstall kordinate — creates ~/.kord/, links to runtime, optionally bootstraps infrastructure.
argument-hint: "[--local] [--restore <repo-url>]"
curated: true
scope: global
---

Full kordinate installation. Orchestrates scribe (linking) and charon (infrastructure).

## Usage

```
/install                        # full install (interactive)
/install --local                # local only — create ~/.kord/, link to runtime, no infra
/install --restore <repo-url>   # restore from backup repo, then link
```

## Procedure

### 1. Create ~/.kord/

- **Fresh install**: copy from the kordinate repo (`kordinate/kordinate/`) to `~/.kord/`
- **Restore**: `git clone <repo-url> ~/.kord/`
- If `~/.kord/` already exists, ask before overwriting.

### 2. Initialize git

If `~/.kord/` is not already a git repo:

```bash
cd ~/.kord
git init
git add -A
git commit -m "initial kord state"
```

This enables worktree isolation for parallel agent memory writes.

### 3. Backup repo (optional)

Ask: "Back up ~/.kord/ to a private repo? (y/n)"

If yes:
- `gh repo create kordinate-state --private --source ~/.kord/ --push`
- Or user provides an existing repo URL: `git remote add origin <url> && git push -u origin main`

If no: local-only git, no remote. Worktrees still work.

### 4. Link to runtime

Delegate to scribe — invoke the linking procedure at `$KORDINATE_HOME/agents/scribe/skills/onboard/link.md`.

Scribe handles: agents → `~/.claude/agents/`, skills → `~/.claude/skills/`, memory indexes → `~/.claude/agent-memory/`, CLAUDE.md, guard hook, KORD.md generation.

### 5. Bootstrap infrastructure (optional)

Skip if `--local` flag is set. Otherwise ask: "Bootstrap cluster infrastructure? (y/n)"

If yes: delegate to charon — `/bootstrap`. This sets up k3s, namespaces, storage, and deploys the workstation pod (which runs Beorn).

### 6. Verify

Run `$KORDINATE_HOME/agents/scribe/skills/onboard/smoke-test.sh` for structural checks.

## Report

- ~/.kord/ status (fresh/restored, git initialized, backup repo configured)
- Linking results (from scribe)
- Infrastructure status (if bootstrapped)
- Smoke test results
