---
description: "Optimistic Update \u2014 immediately reflecting expected state changes\
  \ in the UI before server confirmation"
type: pattern
testable: true
graphable: true
abstraction:
- frontend
- data
- resilience
status: primary
scope: frontend
relationships:
  related_to:
  - optimistic-locking
  - reactive-store
  - event-notification
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Optimistic Update

## Recognition

How to identify this pattern in code.

### Signatures

- `onMutate` / `onError` / `onSettled` callbacks in TanStack Query mutations
- `optimisticResponse` in Apollo Client mutations
- Manual state rollback on error (`previousData` pattern)
- `useSWRMutation` with `optimisticData` option
- Zustand/Redux: update store immediately, revert on API failure
- UI shows success state before server response, reverts on failure

### Confidence

- **high** -- mutation with `onMutate` setting cache/store + `onError` rolling back to previous state
- **medium** -- immediate UI update on action but no explicit rollback mechanism
- **low** -- fire-and-forget mutations that update UI without waiting (may not be intentionally optimistic)

## Architecture

Look for a mutation flow that updates client-side state immediately upon user action, captures previous state for rollback, and reconciles with the server response on success or failure.

### Review Checklist

- Previous state is captured before the optimistic update for rollback
- Error handler reverts to the captured state
- Success handler reconciles server response with optimistic state (server is source of truth)
- User receives feedback on rollback (toast, error message -- not silent revert)
- Optimistic updates are only applied for low-risk mutations (add to cart: yes, payment: no)

### Anti-patterns

- No rollback mechanism -- optimistic state persists even after server failure
- Optimistic updates on critical operations (payments, deletes) where false positives are harmful
- Race conditions -- multiple optimistic updates to the same entity without sequencing
- Silent rollback -- user doesn't know their action failed

### Relationship To Other Concepts

- Related to [optimistic-locking](/concepts/optimistic-locking) because optimistic UI updates often rely on later conflict detection and rollback if the backend disagrees.
- Related to [reactive-store](/concepts/reactive-store) because pending optimistic state is frequently managed in client-side reactive stores.
- Related to [event-notification](/concepts/event-notification) when asynchronous confirmations or rejections later reconcile provisional client state.

### Boundary

Use `optimistic-update` when the system intentionally shows an anticipated successful state before the authoritative write is confirmed.

Do not use it for normal eventual consistency or background refresh unless the UI or caller is proactively applying the change ahead of confirmation.
