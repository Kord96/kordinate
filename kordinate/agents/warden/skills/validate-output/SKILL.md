---
name: validate-output
description: >
  Run a validator script against an output directory, manage validation locks,
  and report results. Any skill can request validation — warden handles enforcement.
argument-hint: "<dir> --validator <script>"
curated: true
scope: global
---

Run a validator script against an output directory, manage the validation lock, and report results. Skills call this to validate their output — they never interact with locks directly.

## Arguments

`$ARGUMENTS` — Required: `<dir>` (directory containing output to validate). Required: `--validator <script>` (path to a validator script that accepts `<dir>` as its first argument and exits 0 on success, non-zero on failure).

## How It Works

### For calling skills

Skills request validation:

```
/kord warden validate-output <dir> --validator <script>
```

If validation fails, the skill sees the errors and fixes them. The skill does not know about locks — it just knows writes are blocked until validation passes.

### Lock mechanism

Warden manages `.validate-lock` files transparently via two hooks:

- **PreToolUse** (Write/Edit): if `.validate-lock` exists in the target directory, the write is blocked with an error telling the agent to fix validation errors first.
- **PostToolUse** (Bash): after any validator script run, the hook silently re-runs it with `VALIDATE_LOCK=1` to create or remove the lock based on the result.

The agent never creates, checks, or removes locks. The hooks do it automatically.

### Validator contract

A validator script must:

1. Accept a directory path as its first argument
2. Print human-readable errors/warnings to stdout
3. Exit 0 if valid, non-zero if errors found
4. When `VALIDATE_LOCK=1` is set: create `<dir>/.validate-lock` on failure, remove it on success (the orchestrator script handles this, so custom validators only need to support the env var if they want custom lock paths)

## Procedure

1. **Parse** `<dir>` and `--validator <script>` from `$ARGUMENTS`. If either is missing, show usage and exit.
2. **Verify** the directory exists and the validator script exists and is executable.
3. **Run** the validator:
   ```bash
   python3 <script> <dir>    # or bash <script> <dir>, detected from shebang/extension
   ```
4. **Report** the output to the calling agent.
5. If validation fails: the PostToolUse hook silently manages the lock. The calling agent sees the errors and should fix them, then re-run validation.
6. If validation passes: the PostToolUse hook removes the lock. Writes to `<dir>` are unblocked.

## Integration

To add validation to a skill:

1. Write a validator script that checks your output format (see augur's `validate_output.py` as an example)
2. In your SKILL.md procedure, add a validation step:
   ```bash
   python3 $SKILL_DIR/scripts/validate_output.py $OUTPUT_DIR
   ```
3. The shared hooks detect the validator run and manage locks automatically. No hook registration needed per-skill — the hooks are global.
