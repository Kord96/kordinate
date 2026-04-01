# Dev Sync

Level 3 resource for the register skill.

Automatic synchronization of package files from a kordinate dev repo to the runtime installation at `~/.kord/`. Eliminates the need to run `/install --local` after every change during development.

## What Dev Mode Is

Dev mode designates a local clone of the kordinate repo as the authoritative package source. When active, a git post-commit hook copies any changed files under `kordinate/` to `$KORDINATE_HOME` (default `~/.kord/`) immediately after each commit.

## Activation

```
/register runtime --dev <repo-path>
```

This writes the absolute path of the dev repo root to `$KORDINATE_HOME/.dev-source` and symlinks the hook into the repo's `.git/hooks/`.

### What .dev-source contains

A single line: the absolute path to the dev repo root (e.g., `/kord/projects/kordinate`). The hook reads this file to confirm it is running inside the registered repo. If the file is missing, the hook exits silently -- dev mode is off.

## How Auto-Sync Works

The hook (`hooks/dev-sync.sh` in the repo root) runs as a git `post-commit` trigger:

1. Checks `.dev-source` exists and matches the current repo root.
2. Runs `git diff-tree` on HEAD to find files changed under `kordinate/`.
3. For each changed file:
   - If the file exists in the commit, copies it to the corresponding path under `$KORDINATE_HOME`.
   - If the file was deleted and is tracked in `.manifest.json`, removes it from the installation.
4. Updates `.manifest.json` hashes for all changed files.
5. Updates the `source.ref` field in `.manifest.json` to the current short commit SHA.
6. Prints a summary to stderr: `[kordinate] dev-sync: N copied, M removed`.

## Hook Installation

The hook is symlinked into the repo's git hooks directory:

```bash
ln -sf ../../hooks/dev-sync.sh .git/hooks/post-commit
```

If a `post-commit` hook already exists, append the call instead:

```bash
echo '#!/bin/bash' > .git/hooks/post-commit  # only if no hook exists
echo './hooks/dev-sync.sh' >> .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

The `register runtime --dev` command handles this automatically.

## Disabling Dev Mode

1. Delete the dev-source marker: `rm ~/.kord/.dev-source`
2. Remove the hook symlink: `rm .git/hooks/post-commit` (or edit to remove the dev-sync line)

After disabling, commits no longer trigger syncing. The installation at `~/.kord/` remains as-is until the next `/install --local`.

## Manual Sync Fallback

`/register --sync` (the link procedure in [link.md](link.md)) still works as a full re-sync. Use it when:

- You need to sync uncommitted changes.
- The hook was not installed or was bypassed (`--no-verify`).
- You want to re-link agents and skills, not just copy files.

## Limitations

- **Commit-scoped**: only syncs on commit, not on save. Uncommitted edits are not reflected.
- **Package files only**: only files under `kordinate/` are synced. Root-level files (hooks, docs, CI configs) are dev tools and are not installed.
- **Manifest dependency**: deleted-file cleanup requires `.manifest.json` and `jq`. Without them, deletions are skipped (additions still work).
- **Single repo**: only one dev repo can be registered at a time. The last `--dev` registration wins.
