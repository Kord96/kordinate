---
name: architect
description: Produce a unified architectural understanding of a project as architecture.yaml — components, flows, state, events, dependencies, failure modes.
curated: true
scope: global
---

Produce a structured architectural understanding of a project.

## Arguments

`$ARGUMENTS` — Required: `<project>`. The project directory must exist at `~/<project>/`, `~/repos/<project>/`, or `~/test-repos/<project>/`.

## Steps

1. Parse project name. Locate the project directory. If not found, report and exit.

2. **Detect stack** — check for package manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.). Note the primary language and framework.

3. **Gather file contents** — collect source files for analysis. See [extractors.md](extractors.md) for include/exclude patterns. Cap at 100KB per file. For large projects (>500 files), prioritize entry points, hub modules, config, and manifests.

4. **Gather existing analysis** — read from `<project>/.claude/agent-memory/designer/` if available (`patterns.md`, `dependencies.md`, `api-review.md`, `debt-assessment.md`). Also check concept catalog at `agents/designer/memory/concepts/*/pattern.md` for pattern matching. Use concept names as vocabulary for `state[].concept`, `external_dependencies[].concept`, and `components[].patterns`. If none exist, proceed — file contents are sufficient.

5. **Organize into groups** — identify the architecturally significant abstractions and organize them into a hierarchy:

   Identify **3-5 root groups** — abstract containers for the system's major layers. These are NOT modules — they're organizational boundaries. 3 is often enough. More than 5 means you're not abstracting enough.

   Nest every concrete abstraction under a root group via `children`. Create sub-groups for closely related components. The goal is a 3-4 level deep tree.

   Filtering:
   - Entry points, data stores, and external integrations ARE core abstractions
   - Utilities, logging, and config modules are NOT — skip them
   - No leaf components at the top level — wrap them in a group

6. **Map relationships** — for each pair of abstractions, determine if a significant relationship exists. Label it in a few words. Only include relationships backed by actual code. Exclude trivial shared utility imports.

7. **Identify actors** — who/what interacts with the system from outside: users, services, scheduled jobs, data sources.

8. **Map data flows** — trace the critical paths through the system. Each flow answers: "what happens when [trigger]?" and traces to a **user-visible outcome**.

   Each flow must trace the **full reactive chain**, not just direct calls:
   - Follow through state updates, cache invalidations, re-renders, and side effects
   - Include serialization boundaries and persistence points
   - End at what the user sees change
   - 5-10 steps per flow. Fewer than 4 means you stopped too early.
   - Short labels (3-5 words). Detail goes in `action` and `data` fields.
   - Specify `technology` on each step for the transport mechanism.

9. **Catalog state** — for each data store: technology (generic concept + specific implementation), what it stores, purpose (source-of-truth/cache/derived/staging), persistence (persistent/ephemeral).

10. **Map events** — for each event/topic/signal: producer, consumer(s), payload, rough frequency.

11. **Catalog external dependencies** — for each: concept + implementation, which component, purpose, criticality, resilience patterns present.

12. **Identify failure modes** — for each external dependency and stateful component: what breaks, cascade, user impact, detection, severity.

13. **Write architecture.yaml** — assemble into the schema at [schema.md](schema.md). Write to `<project>/.claude/agent-memory/designer/architecture.yaml`. Delegate to scribe if blocked.

14. **Report** — purpose, component count, root groups, flow count, failure modes, output path.
