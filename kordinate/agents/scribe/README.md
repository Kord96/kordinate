# Scribe

Documentation gate and runtime linker — sole authority for writing to kordinate and memory paths.

## Skills

| Skill | Command | Mode | Purpose |
|-------|---------|------|---------|
| [remember](skills/remember/SKILL.md) | `/remember <what>` | stateless | Write a memory for an agent — handles scope, paths, and KORD.md |
| [sanitize](skills/sanitize/SKILL.md) | `/sanitize <content>` | stateless | Classify content as config, credential, or memory — routes correctly |
| [onboard](skills/onboard/SKILL.md) | `/onboard <name>` | stateful | Add a new agent or sync existing agents to the runtime |
| [create-kord](skills/create-kord/SKILL.md) | `/create-kord <name>` | stateful | Define a new kord between agents |

## Kords Provided

| Kord | Mode | Requesters | Description |
|------|------|-----------|-------------|
| [scribe-default](../../kords/scribe-default/contract.md) | stateful | any | General documentation and template questions |
| [create-kord](../../kords/create-kord/contract.md) | stateful | any | Define a new kord between agents |
| [onboard](../../kords/onboard/contract.md) | stateful | any | Onboard a new agent to the team |
| [remember](../../kords/remember/contract.md) | stateless | any | Write a memory — handles scope, paths, registry updates |
| [sanitize](../../kords/sanitize/contract.md) | stateless | any | Classify and route content to correct destination |

## Memory

| File | Description |
|------|-------------|
| [tools.md](memory/tools.md) | Tools reference — Gemini MCP for doc review |
| [workflow.md](memory/workflow.md) | Authentication and write workflow |
| [scratchpad.md](memory/scratchpad.md) | Working notes and observations |
| [templates/](memory/templates/) | Templates for other agents (sauron metrics, vitals) |

## Rules

- Always read the target file before editing
- Never delete existing content unless explicitly asked
- Always authenticate before writing (use `/authenticate`)
- Keep edits minimal — change only what was requested
- When writing memory, decide global vs project scope based on content
- Write to both kordinate and runtime-native paths in one operation
