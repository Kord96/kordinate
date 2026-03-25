# Contract Template

Level 3 resource for the kord skill.

## Template

```markdown
---
description: <what this kord provides>
requester: <agent or "any">
provider: <agent>
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

## Template Rules

- Provider Guidelines tell the provider how to behave, not how to do its job
- Response Format defines expected output structure so requesters can rely on it
- Never include procedure ("check this file", "run this command") — the provider knows its domain
- Keep guidelines concise and specific
