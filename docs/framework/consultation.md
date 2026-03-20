# Consultation

Ask an agent a question without transferring full control.

## Usage

```bash
/consult deployer "Is logbd healthy on vandc?"
/consult sauron "what metrics does the enricher expose?"
/consult designer "what are logbd's main components?"
```

## How It Works

```mermaid
flowchart TD
    Q["/consult agent question"] --> CH{cache fresh?}
    CH -->|yes, same question| R[return cached result]
    CH -->|stale or new question| SP[spawn agent]
    SP --> A[agent reads memory, answers]
    A --> W[write result to cache]
    W --> RR[return result]
```

Results are cached per consulter-consultant pair at `agents/shared/memory/dynamic/`. The cache uses the framework's [hash-based invalidation](memory.md#cache-system) — if the consultant's source files change, the cache goes stale automatically.

!!! tip "Force re-consultation"
    ```bash
    /invalidate deployer
    ```
    Removes hash files where the given agent is the consultant. Cache content is preserved as fallback — refreshed on next `/consult`.

!!! note "Consultation Matrix"
    The consultation matrix — which agents can consult which, and what each provides — is defined by each team's agent configuration. See your team's agents page for the specific matrix.

## Cache Invalidation

Each consultant declares its **cache source directories** in the `## Cache Sources` section of its `instructions/consultation.md`. These are the directories whose content determines whether a cached consultation answer is still valid.

A PostToolUse hook automatically invalidates cached answers when the consultant's source files change. The hook hashes the declared source directories after each tool use — if the hash differs from the stored hash, the cache entry is marked stale and the next `/consult` call will re-invoke the agent instead of returning the cached answer.

!!! tip "Manual invalidation"
    Use `/invalidate <agent>` to force-clear a specific agent's cached answers without waiting for source changes.
