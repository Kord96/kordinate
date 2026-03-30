---
description: Versioned document pattern with revision history and conflict resolution
type: domain-model
abstraction: [data, collaboration]
---
# Versioned Document

## Recognition

How to identify this pattern in code.

### Signatures

- `revision`, `version`, or `version_number` fields tracking document iterations
- `version_history` or `revisions` array/table storing past states
- `diff` and `patch` functions computing and applying changes between versions
- CRDT imports: `yjs`, `automerge`, `diamond-types`, `loro`
- Operational Transform: `ot`, `operational_transform`, `ShareDB`, `sharedb`
- Python: `diff_match_patch`, `deepdiff`, custom `Revision` model classes
- JS/TS: `yjs`, `automerge`, `Yjs.Doc`, `prosemirror` with collaboration plugin
- Go: `sergi/go-diff`, `revision` structs with parent hash references
- Rust: `automerge-rs`, `diamond-types`, `similar` crate for diff computation
- `snapshot` and `restore` methods for materializing a specific version

### Confidence

- **high** -- CRDT or OT library with real-time collaboration, plus a revision history table with immutable snapshots and diff-based change tracking
- **medium** -- Version number field with a revisions table storing full document snapshots on each edit
- **low** -- Simple `updated_at` timestamp or `version` integer used for optimistic locking without actual content history

## Architecture

### When to use
- Collaborative editing where multiple users modify the same document concurrently
- Content management systems requiring full revision history and rollback capability
- Legal, regulatory, or compliance contexts where every change must be preserved

### Anti-patterns
- Storing only the latest version, making rollback impossible without backups
- Using optimistic locking version numbers but never actually persisting revision content
- Implementing custom merge logic instead of using proven CRDT/OT libraries for real-time collaboration

### Complements
- [event-sourcing](/concepts/event-sourcing) — document revisions can be modeled as an event stream
- [block-content](/concepts/block-content) — versioned documents often use block-based content structures
- [optimistic-locking](/concepts/optimistic-locking) — version fields serve double duty for concurrency control

## Impact

Versioned documents create storage growth proportional to edit frequency and require merge conflict resolution strategies. Testing must cover concurrent edit scenarios, and monitoring should track revision chain integrity and storage consumption over time.
