---
description: Memento architectural pattern
curated: true
scope: global
preloaded: none
---
# Memento

## Recognition

How to identify this pattern in code.

### Signatures

- Capturing and restoring object state without exposing internal structure
- Undo/redo history stacks
- State snapshots stored as opaque objects
- `save_state()` / `restore_state()` method pairs
- `createMemento()` / `setMemento()` on originator objects
- Editor undo stack implementations
- Caretaker class managing a list of mementos
- Serialized state checkpoints for rollback

### Confidence

- **high** -- Originator with `createMemento()`/`setMemento()` and a caretaker managing a stack of opaque state snapshots
- **medium** -- Undo/redo stack storing serialized state snapshots with restore capability
- **low** -- State serialization for persistence that resembles memento but lacks the undo/restore workflow

## Architecture

Look for an originator that creates opaque state snapshots managed by a caretaker for undo/restore operations.

### Review Checklist

- Memento is opaque to the caretaker (no direct access to internal state)
- Memory usage is bounded (limited history depth or incremental snapshots)
- Restore operation returns the originator to a fully valid state
- Concurrent access to the memento stack is synchronized if applicable
- Large state objects use incremental or compressed snapshots to control memory

### Anti-patterns

- Caretaker reaching into the memento to read or modify internal state
- Unbounded memento history consuming excessive memory
- Memento capturing references to external mutable objects instead of copying state
- Restoring state without validating that the memento is compatible with the current version
