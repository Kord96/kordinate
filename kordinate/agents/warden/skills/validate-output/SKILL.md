---
name: validate-output
description: >
  Validate output against a registered validator. Returns a completion token on success
  that the calling skill needs to include in its report. Without the token, the output
  is considered unvalidated.
argument-hint: "<dir>"
---

Validate an agent's output directory. On success, return a completion token. On failure, return errors. The calling skill cannot finish without the token — this is the enforcement mechanism.

## Arguments

`$ARGUMENTS` — Required: `<dir>` (directory containing output to validate, e.g., `<project>/.kord/agents/augur/memory/`).

## Registry

Warden maintains a registry of validators per agent output directory. Registration happens during install. The registry maps output path patterns to validator scripts:

```yaml
# $KORDINATE_HOME/agents/warden/skills/validate-output/registry.yaml
validators:
  - pattern: ".kord/agents/augur/memory/"
    script: "$KORDINATE_HOME/agents/augur/skills/analyze/scripts/validate_output.py"
    agent: augur
```

If no validator is registered for the given directory, warden reports "no validator registered" and returns no token.

## Procedure

1. **Match** the `<dir>` against the registry to find the validator script. If no match, report and exit.

2. **Run** the validator:
   ```bash
   python3 <script> <dir>
   ```

3. **If validation fails** (non-zero exit):
   - Return the errors to the calling agent
   - Include a clear instruction: "Fix these errors and call `/kord warden validate-output <dir>` again"
   - Do NOT return a token

4. **If validation passes** (exit 0):
   - Compute a completion token: `sha256` hash of the concatenated content of all validated files (atlas.json + sorted story files + sorted journey files)
   - Return the token and a success message:
     ```
     VALIDATED — token: <sha256-hex>
     Include this token in your report to confirm validation passed.
     ```

## Token Properties

- The token is a SHA-256 hash of the validated content
- It's tied to the specific files that were validated — if the agent edits after validation and uses the old token, the hash won't match
- The improve loop can verify: `sha256(current files) == reported token`
- The token cannot be guessed or hallucinated — it depends on file content

## How Calling Skills Use This

In the skill's procedure:

```
Step N — Validate:
  Call /kord warden validate-output <dir>
  If errors: fix them, call again. Repeat until you receive a token.
  Record the token for your report.

Step N+1 — Report:
  Include the validation token in the report.
```

The skill doesn't know about locks, hooks, or enforcement mechanics. It just knows: "I need a token from warden to finish."

## Verification

The improve loop or any downstream consumer can verify the token:

```bash
# Compute expected hash
find <dir> -name "*.json" -o -name "*.yaml" | sort | xargs cat | sha256sum
# Compare with the token in the report
```

If they don't match, the output was modified after validation or the token was fabricated.
