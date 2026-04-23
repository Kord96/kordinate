---
kind: concept
name: command
signatures: {}
type: pattern
abstraction:
- design
scope: backend
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Classes with `execute()`, `run()`, `do()` methods, often paired with `undo()` or `rollback()`
- Command queue, command history, or command stack structures
- Classes ending in `Command`, `Action`, `Operation`, `Task`
- Undo/redo functionality with a history list of executed commands
- Python: command objects with `__call__` or `execute()`, `cmd` module patterns
- JS/TS: action objects in Redux/Flux, command classes with `execute()`/`undo()`
- Go: structs implementing a `Command` interface with `Execute()` method

### Confidence

- **high** -- command objects with both `execute()` and `undo()`, stored in a history stack
- **medium** -- objects encapsulating an operation with `execute()` method, queued for later execution
- **low** -- action/event objects dispatched to a handler (overlaps with event sourcing)

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

### Relationship To Other Concepts

- Related to [cqrs](/concepts/cqrs) when commands represent the explicit write-side intent handled separately from queries.
- Related to [workflow-engine](/concepts/workflow-engine) when commands advance a longer-running process or orchestration.
- Related to [event-driven](/concepts/event-driven) when successful command handling emits domain events afterward.

### Boundary

Use `command` when requests or actions are modeled as explicit objects representing an intention to perform work.

Do not use it for every handler or API call. The important signal is explicit command objects or semantics, not just an imperative method.
