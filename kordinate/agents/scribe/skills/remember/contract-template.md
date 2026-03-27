# Contract Template

Level 3 resource for the remember skill.

## Standard Directory Structure

Stateful kord:
```
<kord-name>/
├── contract.md     # frontmatter + guidelines + cache inputs
├── data.md         # cached response (empty until first consultation)
├── expiry.sh       # two-stage cache check (exit 0/1/2)
└── review.md       # prompt template for stage 2 agent review
```

Stateless kord:
```
<kord-name>/
└── contract.md     # frontmatter + skill field
```

## Template

```markdown
---
description: <what this kord provides>
requester: <agent or "any">
mode: <stateless or stateful>
skill: <skill-name>          # required if mode is stateless
---
<!-- provider is implicit from the directory path: agents/<provider>/kords/<name>/ -->

## Provider Guidelines

<Instructions for how the provider should respond.>
<The provider already knows its domain — guidelines shape the output, not the process.>

### Response Format

| Field | Required |
|-------|----------|
| <field> | yes/no |

## Cache Inputs

Hash these paths to detect staleness:
- `<path-to-hash>`
```

## review.md Template

For stateful kords, `review.md` is the prompt sent to the provider during stage 2 (uncertain expiry). It MUST contain `{{DIFF}}` and `{{CACHED_DATA}}` placeholders, which Beorn fills at runtime.

```markdown
---
description: Cache review prompt — sent to provider when expiry is uncertain
curated: true
scope: global
---

You are reviewing whether your cached response is still valid.

## Changed Inputs

{{DIFF}}

## Cached Response

{{CACHED_DATA}}

## Decision

Based on the changes above, is your cached response still accurate and complete?

- If the changes are irrelevant to your cached response (e.g., comments, formatting, unrelated files), respond: `VALID`
- If the changes affect the accuracy of your cached response, respond: `STALE`

Respond with ONLY `VALID` or `STALE` on the first line, followed by a brief reason.
```

## Modes

- **stateless** — the requester runs the provider's skill directly in its own context. No agent spawn. Fast. The `skill` field specifies which skill to stateless. Scribe adds the skill to requester agents during onboard/sync.
- **stateful** — the requester hands off to the full provider agent (via Beorn or native subagent). The agent has identity, memory, skills, full context. Uses two-stage cache expiry: exit 0 (fresh), exit 1 (stale), exit 2 (uncertain — triggers review.md agent prompt).

## Template Rules

- Provider Guidelines tell the provider how to behave, not how to do its job
- Response Format defines expected output structure so requesters can rely on it
- Never include procedure ("check this file", "run this command") — the provider knows its domain
- Keep guidelines concise and specific
- Use `mode: stateless` for stateless actions (remember, authenticate). Use `mode: stateful` for work requiring agent context (deployments, diagnosis).
