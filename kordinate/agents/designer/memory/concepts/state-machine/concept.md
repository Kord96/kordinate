---
description: State Machine architectural pattern
type: pattern
testable: true
observable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [design, lifecycle]
---
# State Machine

## Recognition

How to identify this pattern in code.

### Signatures

- Enum or constants defining states: `State`, `Status`, `Phase`
- Transition table/map: dict or map from `(state, event)` to `next_state`
- Lifecycle hooks: `on_enter`, `on_exit`, `before_transition`, `after_transition`
- State classes with `handle()` or `process()` methods
- Python: `transitions` library, `statemachine` library, enum-based state tracking
- JS/TS: XState (`createMachine`, `interpret`), state pattern with class-per-state
- Go: state as `int`/`string` const with transition function, `looplab/fsm`
- Rust: typestate pattern (different types per state), enum-based FSM
- Java: Spring State Machine (`StateMachineBuilder`, `StateMachineConfigurer`), `enum State` with explicit transition methods

### Negative signals (not sufficient for detection)

- An `enum State` or `enum Status` used purely as a data label (e.g., `Status.ACTIVE`/`Status.INACTIVE`) without transition logic is not a state machine
- Simple boolean or enum flags (`isProcessing`, `ConnectionState.OPEN`) that are set directly without guarded transitions are status tracking, not state machines
- The word `transition` in comments, documentation, or generic context (CSS transitions, data format transitions, team transitions) is NOT a state machine
- Java: `enum` types alone (even named `State` or `Status`) without transition logic are data types, not state machines
- Database migration "transitions" (schema transitions, Flyway state transitions) are database-migration, not state machine
- `FSM` as an unrelated acronym (financial, filesystem) without state machine library imports is not this pattern
- Go: `transition` as a function name in non-lifecycle contexts (data transformation, format conversion) is not this pattern
- `StateMachine` in Kafka Streams or Spring Batch internal state management is framework internals, not an application-level state machine
- Go: `iota` constants for states without a transition function or guard logic are enums, not state machines
- `handle()` or `process()` methods without state-aware dispatching are generic handlers, not state machine handlers

### Confidence

- **high** -- explicit transition table mapping `(state, event)` pairs to next states, with guard conditions
- **medium** -- enum state variable with switch/match on transitions and entry/exit hooks
- **low** -- status field updated in multiple places with ad-hoc if/else transitions

## Architecture

Look for a complete and well-defined transition table with no implicit state changes.

### Review Checklist

- All valid transitions are explicitly defined (no implicit state changes via direct assignment)
- Invalid transitions are rejected with clear errors, not silently ignored
- Entry/exit actions are tied to transitions, not scattered through business logic
- State is persisted correctly if the machine must survive restarts
- Guard conditions on transitions are pure (no side effects in guards)
- Terminal states are defined and reachable

### Anti-patterns

- State modified by direct assignment instead of through the transition mechanism
- Missing transitions causing the machine to get stuck in unexpected states
- Business logic embedded in transition guards (guards should only evaluate conditions)
- No protection against concurrent transitions (race between two events)
