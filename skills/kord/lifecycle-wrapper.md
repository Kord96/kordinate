# Lifecycle Wrapper

Level 3 resource for the kord skill. Defines the prompt wrapper that injects lifecycle steps around stateful agent tasks.

## Why

Subagents ignore lifecycle instructions placed in MEMORY.md (auto-loaded context). They only follow instructions in the task prompt. The kord skill wraps every stateful agent spawn with a checklist that includes memory loading and insight saving.

## Wrapper Template

When building the prompt for a stateful kord spawn (whether via Beorn or local Agent tool), wrap the caller's message:

```
Follow this checklist exactly. Create tasks for each item using TaskCreate:

1. Read your memory index at $KORDINATE_HOME/agents/<agent>/memory/MEMORY.md
2. <task steps derived from the caller's message and contract guidelines>
3. Run `/kord remember <insight>` with any non-obvious insights you learned

Mark each task complete as you go. Do not return your final answer until all tasks are done.
```

Where:
- `<agent>` is the provider agent name from the contract
- Step 2 is the caller's message, prefixed with the contract's Provider Guidelines if present
- `$KORDINATE_HOME` is resolved to its absolute path

## When to Apply

| Kord mode | Apply wrapper? | Why |
|-----------|---------------|-----|
| stateful | yes | Agent does autonomous work, may learn something |
| stateless | no | Skill runs locally, no agent spawned |

## When NOT to Apply

- Skip step 1 (read memory) if the contract has `cache_inputs` and the response is cached — the agent isn't spawning at all
- Skip step 3 (remember) if the task is trivially short (single-fact lookup) — there's nothing non-obvious to learn
