---
description: Snapshot Testing architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
---
# Snapshot Testing

## Recognition

How to identify this pattern in code.

### Signatures

- `toMatchSnapshot()`, `toMatchInlineSnapshot()` in Jest tests
- `__snapshots__` directories containing `.snap` files
- `syrupy` assertions (`assert snapshot == result`) in Python tests
- `approve_tests` or `ApprovalTests` library usage with `.approved.txt` files
- Snapshot update commands in CI or package scripts (`--update-snapshot`, `-u` flag)
- `.snap` or `.snapshot` file extensions tracked in version control

### Confidence

- **high** — Snapshot files committed to version control with corresponding test assertions, and a CI step that fails on snapshot drift
- **medium** — Snapshot assertions present but snapshot files are in `.gitignore` or frequently bulk-updated without review
- **low** — String comparison tests against large expected outputs that function like manual snapshots

## Architecture

Look for snapshot assertions that capture complex output and detect unintended changes through diff comparison.

### Review Checklist

- Snapshots capture meaningful output (serialized components, API responses, CLI output) not implementation internals
- Snapshot updates are reviewed in PRs -- bulk updates without explanation are flagged
- Volatile data (timestamps, random IDs, absolute paths) is masked or normalized before snapshotting
- Inline snapshots are used for small, focused assertions; file-based snapshots for larger outputs
- Obsolete snapshots are cleaned up when corresponding tests are removed

### Anti-patterns

- Blindly running `--update-snapshot` and committing without reviewing what changed
- Snapshotting entire DOM trees or large JSON blobs where small unrelated changes cause noisy diffs
- No normalization of non-deterministic values, causing snapshots to break on every run
- Using snapshots as a substitute for targeted assertions when specific field checks would be clearer
