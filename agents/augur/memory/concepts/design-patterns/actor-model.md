---
kind: concept
name: actor-model
signatures: {}
type: pattern
abstraction:
- concurrency
- architectural
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Message passing between isolated actors with no shared mutable state
- Mailbox/inbox queues per actor, `receive()` or `handle_message()` methods
- Actor references or PIDs used to address messages, not direct function calls
- Libraries: Python `pykka`, Akka (JVM), Erlang/Elixir processes, `thespian`
- Directory structures with `actors/`, `messages/`, or `mailbox` modules

### Confidence

- **high** -- Actor classes with explicit `receive()`/`on_receive()` handlers and mailbox-based dispatch
- **medium** -- Message-passing between isolated objects with no shared state, but no formal actor library
- **low** -- Isolated workers communicating through any form of async messages

## Architecture

Look for isolated actors communicating exclusively through asynchronous messages with no shared mutable state.

### Review Checklist

- Each actor encapsulates its own state -- no shared mutable data between actors
- Messages are immutable value objects, not references to mutable state
- Supervision hierarchy exists for actor failure recovery
- Mailbox overflow is handled (bounded mailbox, backpressure, or dead letters)
- Actor lifecycle is explicit: creation, restart policy, and termination

### Anti-patterns

- Actors sharing mutable state through closures or global variables
- Synchronous blocking calls between actors (defeats the concurrency model)
- Unbounded mailboxes that grow without limit under load
- Single god-actor that handles all message types instead of decomposing responsibility

### Relationship To Other Concepts

- Related to [worker-pool](/concepts/worker-pool) because both distribute work, though actor systems encapsulate state and mailbox behavior per actor rather than sharing generic tasks across workers.
- Related to [pub-sub](/concepts/pub-sub) because actors communicate by message passing, even though actor routing and ownership are usually more structured than topic fan-out.
- Related to [state-machine](/concepts/state-machine) when actor behavior changes across explicit states or message-handling modes.

### Boundary

Use `actor-model` when concurrency is organized around isolated actors with mailboxes, private state, and asynchronous message passing.

Do not use it for every async worker or queue consumer. The defining property is encapsulated stateful actors communicating only by messages.
