---
description: Memento — testing guidance
type: supplementary
---
## Testing

Verify that state snapshots are correct, opaque to the caretaker, and restore the originator faithfully.

### Unit Tests

- Create a memento, modify the originator, restore from the memento, and assert the originator returns to the saved state
- Verify the caretaker cannot access or modify the memento's internal state (opaqueness)
- Test undo/redo stack: perform multiple operations, undo each, and assert state reversal at each step

### Edge Cases

- Restore from a memento when the originator has not changed and verify no-op behavior
- Test memory bounding: exceed the history limit and verify the oldest memento is discarded
- Create a memento with large state and verify incremental or compressed snapshots control memory usage

### Compatibility Tests

- Save a memento, upgrade the originator's schema, and verify restoration handles version mismatch gracefully
