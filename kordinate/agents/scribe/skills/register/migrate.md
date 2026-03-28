# Migrate

Level 3 resource for the register skill. Migrate an existing kordinate installation to manifest-tracked updates.

Existing installations (created before the manifest system) have no `.manifest.json`. This procedure reconstructs one by comparing the live `$KORDINATE_HOME` against a known package source, then hands off to the normal runtime flow.

## When to use

- `$KORDINATE_HOME` (typically `~/.kord/`) exists
- `.manifest.json` does not exist
- User wants to start receiving tracked updates

## Procedure

### 1. Detect migration needed

Check both conditions:

```
[ -d "$KORDINATE_HOME" ] && [ ! -f "$KORDINATE_HOME/.manifest.json" ]
```

If `.manifest.json` already exists, this is a normal update — skip migration and use [runtime.md](runtime.md) step 5 directly.

### 2. Ask user for source

The manifest needs a package source to compare against. Prompt for one of:

- **Dev repo path** — local clone of the kordinate repo (most common for existing users)
- **Remote URL** — git remote to clone

If the user has a `.dev-source` file from a previous dev install, read the path from it as the default.

### 3. Pull package

Same as [runtime.md](runtime.md) step 4:

- Local: resolve absolute path, validate `kordinate/` subdirectory
- Remote: `git clone --depth 1` into temp directory

Package dir = `<source>/kordinate/`

### 4. Reconstruct manifest

Source the manifest library from the package:

```bash
source "<package_dir>/lib/manifest.sh"
```

Compare every file in `$KORDINATE_HOME` against the package:

**For each file in the package:**

- Compute hash of both the package file and the installed file
- **Hashes match** — file is unmodified from package. Add to manifest with the package hash.
- **Hashes differ** — user has modified this file. Add to manifest with the *installed* hash and flag for review:
  ```json
  {"path": "agents/scribe/IDENTITY.md", "hash": "<installed_hash>", "curated": true, "migrated_dirty": true}
  ```
- **File missing from install** — package file not present in `$KORDINATE_HOME`. Copy from package, add to manifest with package hash. Report as new.

**For each file in `$KORDINATE_HOME` not in the package:**

- This is user-created content (custom memory files, project-scoped configs, etc.)
- Do NOT add to manifest — the manifest only tracks package-origin files
- Do NOT delete — these are the user's files

### 5. Write .manifest.json

Build the manifest JSON:

```json
{
  "source": {"type": "<local|remote>", "ref": "<path_or_url>"},
  "dev_mode": false,
  "created": "<now>",
  "updated": "<now>",
  "migrated_from": "<kordinate_version_or_unknown>",
  "files": [...]
}
```

The `migrated_from` field records that this manifest was reconstructed, not created fresh. It can be removed after the first successful update.

### 6. Report migration results

Summarize what was found:

- **Matched**: N files identical to package (clean tracking)
- **Modified**: N files differ from package (flagged `migrated_dirty`)
- **New from package**: N files copied from package (not previously installed)
- **User-only**: N files in `$KORDINATE_HOME` not in package (left untouched)

For modified files, list them so the user can review:

```
Modified files (your edits preserved, flagged for review):
  agents/designer/memory/scratchpad.md
  agents/main/memory/scratchpad.md
  shared/credentials-protocol.md
```

### 7. Continue with normal flow

After migration completes, proceed with [runtime.md](runtime.md) from step 6 (initialize git) onward. The manifest is now in place and future updates use the standard `manifest_update` path.

## Notes

- Migration is non-destructive — no files are deleted, no user edits are overwritten
- The `migrated_dirty` flag is informational only. On the next `manifest_update`, these files follow normal curated/non-curated rules: curated files get overwritten (the user accepted this by updating), non-curated files with local edits are skipped
- If the user's `$KORDINATE_HOME` is radically different from the package (e.g., very old version), many files will appear as "modified". This is expected — the manifest captures the current state as the baseline
