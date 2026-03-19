# Kordinate

Multi-cluster k8s infrastructure managed by specialized agents.

## The Big Picture

```
┌─────────────────────────────────────────────────┐
│                   kordinate                      │
│                                                  │
│  ┌──────────┐  ┌────────┐  ┌──────────┐        │
│  │  Agents  │  │ Hooks  │  │ Commands │        │
│  │          │  │        │  │          │        │
│  │ deployer │  │ guard  │  │ /boot    │        │
│  │ sauron   │◄─┤ every  │  │ /consult │        │
│  │ designer │  │ tool   │  │ /merge   │        │
│  │ scribe   │  │ call   │  │ /roll    │        │
│  └─────┬────┘  └────────┘  └──────────┘        │
│        │                                         │
│  ┌─────▼──────────────────────────┐              │
│  │            Memory              │              │
│  │                                │              │
│  │  static/    instructions/      │              │
│  │  (knowledge) (procedures)      │              │
│  │                                │              │
│  │  dynamic/                      │              │
│  │  (auto-managed, encrypted)     │              │
│  └────────────────────────────────┘              │
│                                                  │
│  ┌────────────────────────────────┐              │
│  │           Profile              │              │
│  │  config, locks, keys           │              │
│  │  (site-specific, encrypted)    │              │
│  └────────────────────────────────┘              │
│                                                  │
│            linking layer                         │
│  ┌────────────────────────────────┐              │
│  │  maps kordinate → ~/.claude/   │              │
│  │  (symlinks, copies, renames)   │              │
│  └────────────────────────────────┘              │
└─────────────────────────────────────────────────┘
```

## How They Connect

**Agents** do the work. Each has a role, commands, and memory. They're spawned when the user's message matches a trigger word.

**Hooks** enforce safety. Every tool call an agent makes passes through hooks. Guards check that only the authorized agent performs protected operations (kubectl, grafana, .md edits).

**Memory** is what agents know. Static knowledge is curated and generic. Dynamic memory is auto-managed and site-specific. The `agent-memory.sh` hook combines both into a single file before each agent spawns.

**Profile** is site-specific config — cluster IPs, credentials, MCP servers. Encrypted via git-crypt. Agents read it but don't own it.

**Linking** maps kordinate's internal layout to whatever AI agent runtime is in use (currently Claude Code). The framework stays agent-agnostic; only the linking layer knows about Claude's conventions.

## Explore

<div class="grid cards" markdown>

-   **[Getting Started](getting-started.md)**

    Installation, profile config, link mapping between kordinate and Claude Code.

-   **[Agents](agents.md)**

    Who does what, shared rules, per-agent specifics, and commands.

-   **[Hooks](hooks.md)**

    Safety guards, automation, request flow, and the shared cache library.

-   **[Consultation](consultation.md)**

    Cross-agent queries, the consultation matrix, and result caching.

-   **[Memory](memory.md)**

    How agents store and discover knowledge — static, dynamic, and project layers.

-   **[Reference](reference/patterns/index.md)**

    Design patterns, shared libraries, and infrastructure documentation.

</div>
