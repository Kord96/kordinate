---
description: Command architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design]
---
# Command

## Recognition

How to identify this pattern in code.

### Signatures

- Classes/interfaces with `execute()` method paired with `undo()` or `rollback()` for reversible operations
- Command queue, command history, or command stack storing operation objects for replay/undo
- Classes explicitly named `*Command` with an `execute()` interface and an invoker that triggers them
- Undo/redo functionality with a history list of executed command objects
- Python: command objects with `execute()`/`undo()`, `cmd` module patterns
- JS/TS: command classes with `execute()`/`undo()`, not Redux actions (those are flux, not command)
- Go: structs implementing a `Command` interface with `Execute()` method
- CLI command frameworks (e.g., `commander`, `yargs`, AdonisJS Ace `BaseCommand`) implementing `run()`

**Not this pattern:** CLI subcommands in files named `commands/` that are just route handlers for a CLI framework are not the command pattern -- they are simply framework-organized entry points. The command pattern requires encapsulation of operations as first-class objects that can be queued, undone, or replayed. Also, Redux/Flux actions are the flux pattern, not command.

### Confidence

- **high** -- command objects with both `execute()` and `undo()`, stored in a history stack for replay
- **medium** -- objects encapsulating an operation with `execute()` method, queued or batched for later execution
- **low** -- action objects dispatched to a handler (overlaps with event sourcing and flux)

## Architecture

Look for proper encapsulation of operations as objects, enabling queuing, logging, and undo.

### Review Checklist

- Commands are self-contained (carry all parameters needed for execution)
- Undo restores state completely (not just partially reverting)
- Command history has bounded size to prevent unbounded memory growth
- Commands are serializable if they need to cross process boundaries or be persisted
- Invoker is decoupled from concrete command types

### Anti-patterns

- Commands that reach into global state instead of carrying their own parameters
- Undo that only works if commands are undone in exact reverse order (fragile)
- Bloated command objects containing business logic that belongs in a service
- Command queue with no error handling or dead-letter mechanism for failed commands
