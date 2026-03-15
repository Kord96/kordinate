Update an agent's documentation files under `agents/<name>/`, including creating or rewriting the agent's `CLAUDE.md`.

**Input**: $ARGUMENTS (expect: agent name and what to update)

## Steps

1. Confirm the agent exists: check `agents/<name>/` directory
2. Read the target file(s) under `agents/<name>/`
3. Understand the current content before making changes
4. `chmod u+w` the target file
5. Apply the requested changes — this can be:
   - Updating the agent's knowledge docs (e.g., `monitoring.md`, `logging.md`, `patterns.md`)
   - Updating the agent's `CLAUDE.md` (workflow, triggers, tools, frontmatter)
   - Creating a new agent `CLAUDE.md` from the unified template (see below)
6. `chmod 444` the target file
7. Commit: `docs: update <agent> agent docs [scribe]`

## Creating or rewriting an agent CLAUDE.md

When the request is to create or fully rewrite an agent's `CLAUDE.md`, use the unified template:

```
---
name: <agent-name>
model: <inherit|sonnet|opus|haiku>
color: <color>
tools:
  - <tool1>
  - <tool2>
triggers:
  - "<trigger phrase 1>"
  - "<trigger phrase 2>"
---

# <Name> — <Role> Agent

<One-line mission statement>

## Context

<What to read/consult before acting — including /consult calls to other agents>

## Tools

| Tool | Type | Purpose |
|------|------|---------|
| <tool> | <repo/script/MCP/PyPI> | <what it does> |

## Workflow

1. **Step** — description
2. **Step** — description

## Rules

Shared:
- Read CLAUDE.md before every operation.
- Never write .md files directly — delegate to scribe.
- Commit with `[<agent-name>]` in the message.
- Project-specific artifacts go in the project repo, not the profile repo.

Agent-specific:
- <rules unique to this agent>

## Memory

On every invocation, run /boot before proceeding with your task.
```

Template rules:
- Shared rules are IDENTICAL across all agents (copy verbatim)
- Memory section is IDENTICAL across all agents (copy verbatim)
- Frontmatter has all required fields
- Tools table lists every tool the agent uses
- Every section heading must be present in order: Context, Tools, Workflow, Rules, Memory
- If the agent has no tools beyond standard Claude Code tools, write "Standard Claude Code tools only (Read, Edit, Write, Bash, Grep, Glob)" in the Tools table
- When updating an existing CLAUDE.md, preserve agent-specific content; only restructure to match template

## Restrictions

- Only edit files under the specified agent's directory
- Never edit another agent's files in the same operation
- Never edit root `CLAUDE.md`
- Never remove existing content unless explicitly asked to replace it
