# Kording Guide

How to add a specialized agent to your team.

"Kording" means organizing a new agent into the kordinate framework -- giving it a role, memory, commands, consultation rules, and guard hooks so it operates safely alongside the rest of the team.

This guide uses the **designer** agent as a worked example. By the end, you should be able to follow the same steps to add any new agent.

## What You Create

Every agent needs these files:

| File / Directory | Purpose |
|-----------------|---------|
| `agents/<name>/AGENT.md` | Identity -- role, triggers, commands, rules |
| `agents/<name>/instructions/consultation.md` | What the agent answers when consulted, cache source dirs |
| `agents/<name>/instructions/workflow.md` | Step-by-step procedures for the agent's work |
| `agents/<name>/instructions/tools.md` | Which tools the agent uses and how |
| `agents/<name>/memory/static/` | Pre-defined knowledge the agent needs (patterns, configs, etc.) |
| `agents/<name>/commands/` | Slash command definitions (one `.md` file per command) |

Optional:

| File / Directory | Purpose |
|-----------------|---------|
| `agents/<name>/memory/dynamic/` | Auto-managed -- agent notes, generated MEMORY.md, cache hashes |
| Guard hook in `hooks/` | If the agent has exclusive access to a tool or resource |

## Step 1: Define the Agent (AGENT.md)

The `AGENT.md` is the agent's identity card. It has YAML frontmatter for the runtime and markdown for rules.

**Designer example** -- `agents/designer/AGENT.md`:

```yaml
---
name: designer
model: sonnet
color: purple
memory: user
tools:
  - Read
  - Write
  - Grep
  - Glob
  - Bash
triggers:
  - "review architecture"
  - "design review"
  - "check design consistency"
---
```

The frontmatter tells the runtime:

| Field | What it controls |
|-------|-----------------|
| `name` | Agent identifier -- used in hook auth, commit messages, cache keys |
| `model` | Which model to use (sonnet, opus, haiku) |
| `color` | Terminal color for visual distinction |
| `memory` | Memory scope -- `user` for global agents |
| `tools` | Which tools the agent can access |
| `triggers` | Phrases that cause the orchestrator to spawn this agent |

Below the frontmatter, write the agent's role, commands table, rules, and a pointer to its consultation scope:

```markdown
# Designer

You review project architecture and design consistency. You are the pattern authority.

## Commands

| Command | Purpose |
|---------|---------|
| `/designer:detect-patterns` | Scan a project for recognized patterns |

## Rules

- Framework-first: if a framework primitive exists, use it
- Convention over configuration: follow established patterns
- Proportional effort: don't rewrite working code for marginal improvement
- Concrete: always include specific file paths and what should change
- Validate with Gemini MCP for complex architectural decisions

## Consultation

Component topology, design patterns, pattern perspectives, data flow, failure modes,
dependencies. See `memory/consultation.md`.
```

## Step 2: Define Consultation (instructions/consultation.md)

This file tells the agent what to answer when another agent `/consult`s it, and which directories to hash for cache invalidation.

**Designer example** -- `agents/designer/instructions/consultation.md`:

```markdown
# Consultation

## Cache Sources

Directories to hash for cache invalidation -- if any change, cached answers are stale:

- `instructions/`
- `memory/static/`
- `memory/dynamic/`

When consulted, answer about:
- Component topology -- processes, what they do, how they connect
- Design patterns -- which framework each component uses
- Pattern perspectives -- read from `patterns/<pattern>.md`, return the requested section
- Data flow -- how data moves through the system
- Failure modes -- what can go wrong and the blast radius
- Dependencies -- what each component depends on

## How to answer

1. For pattern perspectives: read `patterns/<pattern>.md`, return the requested section
2. For project questions: look for `docs/architecture.md` in that project
3. If no architecture doc: scan project source to infer architecture
4. Answer concisely -- the caller needs facts, not explanations
5. Keep responses under 50 lines
```

The **Cache Sources** section is critical -- the framework's hash-based invalidation uses these paths to decide whether a cached consultation answer is still valid.

## Step 3: Add Static Memory (memory/static/)

Static memory is the pre-defined knowledge the agent needs to do its job. It is committed to the repo and reviewed like any other code.

**Designer example** -- the designer's static memory holds pattern definitions and library documentation:

```
agents/designer/memory/static/
    patterns.md                  # pattern catalog (index)
    patterns/
        hexagonal.md             # per-pattern: architecture, monitoring,
        service-manager.md       #   deployment, testing sections
        stream-to-store.md
        ...
    libraries.md                 # library catalog (index)
    libraries/
        klog.md                  # per-library documentation
        orchestrator.md
        stoik.md
        nokrashi-tools.md
    app-contract.md              # the observability contract from the app's perspective
```

If the static content is 500 lines or fewer, the `agent-memory.sh` hook inlines it into the generated `MEMORY.md`. Larger files are indexed (title + path) so the agent can read them on demand.

## Step 4: Define Commands (commands/)

Each slash command gets its own `.md` file. The file is a step-by-step procedure the agent follows when the command is invoked.

**Designer example** -- `agents/designer/commands/detect-patterns.md`:

```markdown
# detect-patterns

Scan a project's source code to identify which design patterns are in use
and write a patterns report.

## Arguments

`$ARGUMENTS` -- Required: `<project>` (e.g., `logbd`, `stoik`).

## Steps

1. Parse project name from `$ARGUMENTS`. If missing, show usage and exit.
2. Locate the project directory.
3. Read the pattern catalog for recognition signatures.
4. Scan the project for pattern signatures.
5. Assess confidence (high / medium / low).
6. Identify gaps -- patterns that should be present but are missing.
7. Write the report to `<project>/.claude/agent-memory/designer/patterns.md`.
8. Summarize findings to the caller.
```

The command file is the complete specification. The agent reads it and follows the steps. No additional code is needed.

## Step 5: Register the Agent

Three things connect the new agent to the rest of the team:

### 5a. Add to the shared consultation directory

Edit `agents/shared/MEMORY.md` to add a row to the consultation directory so other agents know when to consult your agent:

```markdown
| Need to know about | Consult |
|---|---|
| Design patterns, component topology, data flow, failure modes | **designer** |
```

### 5b. Create guard hooks (if needed)

If the agent has exclusive access to a tool or resource, create a guard hook. The pattern:

1. Create `hooks/guard-<resource>.sh`
2. Check for `/tmp/.<agent>-auth` matching `profile/locks/<agent>`
3. Allow if match, block if not
4. Register the hook in `settings.json` for the relevant tool contexts

Not every agent needs a guard. The designer has no exclusive tools -- it only reads and analyzes. Guards are for agents that write to protected resources (kubectl, Grafana, Redis, `.md` files).

### 5c. Run link-claude.sh

The linking script maps the agent into the AI runtime:

```bash
./installer/link-claude.sh
```

This creates the symlinks, registers hooks, and makes the agent available to the orchestrator. See [Linking](reference/linking.md) for the full mapping.

## Designer Reference

The designer agent, used as the worked example above, has the following complete specification:

| | |
|---|---|
| **Triggers** | `review architecture`, `design review` |
| **Authority** | Pattern definitions, architecture review |
| **Exclusive Tools** | Gemini (design validation) |
| **Commands** | `/designer:detect-patterns` -- scan a project for recognized patterns |
| **Consults** | [deployer](infra/infrastructure.md) (infrastructure reality), [sauron](infra/infrastructure.md) (observability gaps) |

**Memory**

| | Static | Dynamic |
|---|---|---|
| **Global** | patterns/*.md, libraries/*.md | auto-managed |

## Checklist

When you are done, verify:

- [ ] `agents/<name>/AGENT.md` exists with valid frontmatter
- [ ] `agents/<name>/instructions/consultation.md` has Cache Sources + answer scope
- [ ] `agents/<name>/memory/static/` has the knowledge the agent needs
- [ ] `agents/<name>/commands/` has one `.md` per slash command
- [ ] `agents/shared/MEMORY.md` consultation directory includes the new agent
- [ ] Guard hooks created and registered (if the agent has exclusive tools)
- [ ] `link-claude.sh` run successfully
- [ ] Another agent can `/consult <name> "test question"` and get an answer

??? abstract "Troubleshooting"

    | Problem | Check |
    |---------|-------|
    | Agent not spawning on trigger | Verify triggers in AGENT.md frontmatter match your words |
    | `/consult` returns nothing | Check `.claude/agent-state/<name>.json` exists. Verify `instructions/consultation.md` is present |
    | Guard hook blocking unexpectedly | Check `/tmp/.<agent>-auth` exists during the operation. Verify lock secret matches |
    | Memory not regenerating | Run `/invalidate <agent>`. Check `agent-memory.sh` hook is registered in settings.json |
    | Agent can't find static memory | Verify `link-claude.sh` was run. Check symlinks in `~/.claude/agents/<name>/` |
