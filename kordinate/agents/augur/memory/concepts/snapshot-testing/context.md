# Testing

- Normalize volatile data (timestamps, UUIDs, absolute paths) before taking snapshots to avoid false diffs
- Review snapshot updates in PRs — never commit bulk `--update-snapshot` without inspecting the changes
- Use inline snapshots for small, focused assertions; file-based snapshots for larger structured output
- Test that obsolete snapshot files are cleaned up when corresponding tests are removed
- Run snapshot tests in CI to catch unintended output changes before merge
- Avoid snapshotting implementation details (internal state, DOM trees) — snapshot observable outputs only
- Combine snapshot testing with targeted assertions for critical fields to prevent snapshot blindness

