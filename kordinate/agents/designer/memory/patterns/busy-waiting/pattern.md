---
description: Busy Waiting anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Busy Waiting

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `while True: sleep(0.1); if condition: break` polling loops
- Polling loops with `time.sleep()` or `Thread.sleep()` checking a flag or state
- CPU spin waiting for a state change without yielding (`while not ready: pass`)
- `setTimeout`/`setInterval` polling for a value that could be pushed via events or callbacks
- Repeated database or API polling in a loop instead of using webhooks, subscriptions, or message queues
- Retry loops with fixed sleep intervals and no exponential backoff

### Confidence

- **high** -- a `while` loop contains only a `sleep()` call and a condition check, running continuously in a thread or process, confirmed by CPU profiling showing time spent in the polling function
- **medium** -- `time.sleep()` or `Thread.sleep()` appears inside a loop that checks an external condition (file existence, API response, flag variable)
- **low** -- a `setInterval` or scheduled task polls a resource at a fixed interval where an event-driven alternative exists (webhooks, pub/sub, filesystem watchers)

## Impact

Wasted CPU cycles, delayed response times (up to the sleep interval), and battery/resource drain on constrained environments.

### Symptoms

- CPU usage remains elevated even when the system is idle
- Response to state changes is delayed by the polling interval (latency floor)
- Thread or process pool is consumed by polling loops, reducing capacity for real work
- Battery drain on mobile or edge devices from constant wake-ups
- Unnecessary load on polled services (database, API) from repeated queries

### Remediation

- Replace polling with event-driven mechanisms: callbacks, promises/futures, condition variables, or message queues
- Use OS-level or framework-level waiting primitives (`threading.Event.wait()`, `asyncio.Event`, `select()`, `epoll`)
- For file system changes, use watchers (`inotify`, `fswatch`, `watchdog`) instead of polling loops
- If polling is unavoidable, use exponential backoff with jitter to reduce load and improve responsiveness
- For inter-service communication, prefer webhooks or pub/sub over periodic API polling
