---
description: Actor Model architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [concurrency, architectural]
---
# Actor Model

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
