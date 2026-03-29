# Runtime

Level 3 resource for the register skill. Install or update kordinate in a Claude Code runtime.

Handles first install, updates from a package source, and dev-mode linking for local development.

## Prerequisites

- `jq` and `sha256sum` available on PATH
- Claude Code installed (`claude` command, `~/.claude/` directory)
- Package source: local directory path or git remote URL

## Procedure

### 1. Detect runtime

Verify Claude Code is available:

- Check `claude` command exists on PATH
- Check `~/.claude/` directory exists
- If either missing: abort with instructions to install Claude Code first

### 2. Determine source

Parse from arguments:

- `--dev <path>` — local development repo (enables dev mode)
- `--from <url>` — git remote URL
- No flag — auto-detect: if `$KORDINATE_HOME` exists and has `.manifest.json`, read source from manifest. Otherwise prompt for source.

### 3. Set kordinate home

- Default: `~/.kord/`
- Override: `--home <path>`
- Create directory if it does not exist

### 4. Pull package from source

**Local (--dev or --from <local-path>):**

- Resolve to absolute path
- Validate that `kordinate/` subdirectory exists (the installable package)
- Package dir = `<path>/kordinate/`

**Remote (--from <url>):**

- `git clone --depth 1 <url>` into a temp directory
- Validate that `kordinate/` subdirectory exists
- Package dir = `<tmpdir>/kordinate/`
- Clean up temp directory after install

### 5. Generate manifest

If `.manifest.json` does not exist (first install):

- Copy all files from package dir to `$KORDINATE_HOME`
- Run `manifest_init <kordinate_home> <source_type> <source_ref> [--dev]`

If `.manifest.json` exists (update):

- Run `manifest_update <kordinate_home> <package_dir>`
- Report actions: files copied, updated, skipped, removed

Source the manifest library:

```bash
source "$KORDINATE_HOME/lib/manifest.sh"
```

On first install, the library is not yet at `$KORDINATE_HOME` — source from the package dir instead:

```bash
source "<package_dir>/lib/manifest.sh"
```

### 6. Initialize git

If `$KORDINATE_HOME/.git` does not exist:

```bash
cd "$KORDINATE_HOME"
git init
git add -A
git commit -m "Initial kordinate install"
```

This gives the user a baseline to diff against and a safety net for recovery.

### 7. Link to runtime

Delegate to [link.md](link.md) — this writes agent files, skills, hooks, CLAUDE.md, and KORD.json to the Claude Code native paths.

### 8. Git backup (optional)

If the user wants backup to a remote:

```bash
cd "$KORDINATE_HOME"
git remote add origin <backup-url>
git push -u origin main
```

This is optional and informational — do not push without explicit user consent.

### 9. Dev mode setup

If `--dev` was specified:

- Write `.dev-source` file containing the absolute path to the dev repo
- Install post-commit hook in the dev repo that triggers `manifest_update`:
  ```bash
  #!/bin/bash
  # .git/hooks/post-commit — auto-sync kordinate on commit
  KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"
  PKG_DIR="$(git rev-parse --show-toplevel)/kordinate"
  source "$KORDINATE_HOME/lib/manifest.sh"
  manifest_update "$KORDINATE_HOME" "$PKG_DIR"
  ```
- Make hook executable

Dev mode means the runtime stays in sync with the local repo without manual `/install` calls.

### 10. Verify

Run [smoke-test.sh](smoke-test.sh) for automated structural checks:

```bash
bash "$KORDINATE_HOME/agents/scribe/skills/register/smoke-test.sh"
```

If structural checks pass and user wants full verification, run with `--runtime` flag (uses API calls).

## Report

After completion, summarize:

- Source: local path or remote URL
- Mode: fresh install or update
- Dev mode: active or inactive
- Files: count of copied, updated, skipped, removed
- Verification: smoke-test pass/fail
- Next steps: `/boot` in a fresh session to start using kordinate
