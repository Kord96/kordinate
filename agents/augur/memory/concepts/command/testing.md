---
description: Command — testing guidance
type: supplementary
---
## Testing

Verify command execution, undo capability, and correct decoupling of invoker from receiver.

### Unit Tests

- Execute a command and assert the receiver's state changes as expected
- Test undo: execute then undo a command and verify the receiver returns to its prior state
- Verify command serialization: serialize and deserialize a command, then execute it with the same result

### Integration Tests

- Queue multiple commands and execute them in order — verify the cumulative state is correct
- Test macro commands (composite): execute a macro and verify all sub-commands run in sequence
- Verify command history: replay a sequence of commands and assert the final state matches

### Failure Injection

- Inject a failure mid-execution in a macro command and verify partial undo rolls back completed sub-commands
