---
name: validate-output
description: >
  Validate an output directory with an explicit validator script. Returns a completion token on
  success that the calling workflow should include in its report.
argument-hint: "<target-dir> --validator <script>"
curated: true
scope: global
---

Validate an agent's output directory with the validator that lives next to the schema or output
format it owns. On success, return a completion token. On failure, return errors. The calling
workflow should not finish until validation passes.

## Arguments

`$ARGUMENTS` — Required:
- `<target-dir>`: directory containing the output to validate
- `--validator <script>`: validator script path

Example:

```bash
/validate-output $MEM --validator $AUGUR_HOME/skills/analyze/validator/validate.py
```

## Contract

The validator script must:

1. live inside the repo under an approved path such as:
   - `agents/*/skills/*/validator/validate.py`
   - `agents/*/skills/*/validator/validate.sh`
   - `shared/skills/*/validator/validate.py`
   - `shared/skills/*/validator/validate.sh`
2. accept the target directory as its first argument
3. exit `0` on success, non-zero on failure
4. when `VALIDATE_LOCK=1` is set, create `<target-dir>/.validate-lock` on failure and remove it on success

Validator scripts stay next to the schemas and outputs they validate. This skill owns the protocol,
not the validation logic itself.

Shared parent validators for cross-cutting validation domains live under `validators/`. These are
not compatibility shims; they are the parent validation modules for shared validation concerns that
do not belong to a single agent output schema.

## Procedure

1. Verify that the validator path is inside the repo and matches the allowed validator naming pattern.
   If not, return:

   ```text
   INVALID_VALIDATOR: Refusing to run validator outside approved locations.
   ```

2. Run the validator:

   ```bash
   python3 <validator-script> <target-dir>
   ```

   If the script ends in `.sh`, run it with `bash` instead.

3. If validation fails:
   - Return the validator errors
   - Instruct the caller to fix the output and rerun `/validate-output`
   - Do not return a token

4. If validation passes:
   - Compute a completion token as the `sha256` of the validated directory contents
   - Return:

   ```text
   VALIDATED — token: <sha256-hex>
   Include this token in your report to confirm validation passed.
   ```

## Locking

Locks are scoped to the validated output root, not the whole agent.

- lock file: `<target-dir>/.validate-lock`
- effect: blocks writes inside that output root until validation passes

The lock is managed by the shared validation hooks. This skill only defines the protocol the hooks
rely on.

## How Calling Workflows Use This

When a workflow requires validation:

```text
Step N — Validate:
  Call /validate-output <target-dir> --validator <script>
  If errors: fix them and run /validate-output again
  Repeat until you receive a token
  Record the token for your report
```

## Verification

Downstream consumers can recompute the token from the same validated output directory and compare it
against the reported value.
