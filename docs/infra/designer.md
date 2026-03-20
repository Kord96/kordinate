# Designer

Reviews architecture and owns design patterns. The pattern authority — validates that implementations follow recognized patterns.

| | |
|---|---|
| **Triggers** | `review architecture`, `design review`, `check design consistency` |
| **Authority** | Pattern definitions, architecture review |
| **Exclusive Tools** | Gemini (design validation) |

### Commands

| Command | Description |
|---------|-------------|
| `/designer:detect-patterns` | Scan a project for recognized patterns |

### Memory

| | Static | Dynamic |
|---|---|---|
| **Global** | patterns/*.md, libraries/*.md | auto-managed |

### Consultation

When consulted, answers about: component topology, design patterns, pattern perspectives, data flow, failure modes, dependencies.

Consults: [deployer](infrastructure.md) (infrastructure reality), [sauron](monitoring.md) (observability gaps).

---

!!! tip "Kording new agents"
    Designer is an example of a kord'd agent. To add your own, run `/scribe:kord <name> "<description>"` — it interactively creates all required files.
