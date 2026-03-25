# Contract Template

Level 3 resource for the remember skill.

## Template

```markdown
---
description: <what this kord provides>
requester: <agent or "any">
provider: <agent>
mode: <borrow or delegate>
skill: <skill-name>          # required if mode is borrow
---

## Provider Guidelines

<Instructions for how the provider should respond.>
<The provider already knows its domain — guidelines shape the output, not the process.>

### Response Format

| Field | Required |
|-------|----------|
| <field> | yes/no |

## Provider State Invalidation

Invalidate when:
- <condition>
```

## Modes

- **borrow** — the requester runs the provider's skill directly in its own context. No agent spawn. Fast. The `skill` field specifies which skill to borrow. Scribe adds the skill to requester agents during onboard/sync.
- **delegate** — the requester hands off to the full provider agent (via Beorn or native subagent). The agent has identity, memory, skills, full context.

## Template Rules

- Provider Guidelines tell the provider how to behave, not how to do its job
- Response Format defines expected output structure so requesters can rely on it
- Never include procedure ("check this file", "run this command") — the provider knows its domain
- Keep guidelines concise and specific
- Use `mode: borrow` for stateless actions (remember, authenticate). Use `mode: delegate` for work requiring agent context (deployments, diagnosis).
