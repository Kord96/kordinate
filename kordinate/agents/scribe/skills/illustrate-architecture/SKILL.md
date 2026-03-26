---
name: illustrate-architecture
description: Generate diagram descriptions and optional tutorials from a project's architecture.yaml — decides which diagrams are useful and at what abstraction level.
curated: true
scope: global
---

Generate structured diagram descriptions and optional brief tutorials from a project's architectural understanding.

## Arguments

`$ARGUMENTS` — Required: `<project>` (e.g., `logbd`, `stoik`, `sous-storefront`). Optional: `--tutorial` to also generate a brief tutorial.

The project must have an `architecture.yaml` at `<project>/.claude/agent-memory/designer/architecture.yaml`. If it doesn't exist, report and suggest running `/designer:architect` first.

## Procedure

1. Parse project name from `$ARGUMENTS`. Locate the project directory at `~/<project>/`, `~/repos/<project>/`, or `~/test-repos/<project>/`.

2. **Read architecture.yaml** — load the project's architectural understanding. This is the sole input — no code scanning needed.

3. **Decide which diagrams to generate** — not every project needs every diagram type. Use these rules:

   | If architecture.yaml has... | Viewpoint | Zoom | Why |
   |---------------------------|-----------|------|-----|
   | 4+ components with `depends_on` | **structural** | 1 | System overview |
   | Components with `children` | **structural** | 2+ | Zoomed detail per component with children |
   | Any `data_flows` with 3+ steps | **behavioral** | 1 | One diagram per flow |
   | 3+ `state` entries | **data** | 1 | What's stored where |
   | Components with `deployment` info | **deployment** | 1 | Infrastructure topology |
   | Any `failure_modes` with severity critical | **failure** | 1 | Blast radius per critical failure |

   Skip viewpoints that would be trivial. Each viewpoint is generated at the appropriate zoom level.

4. **Generate diagram descriptions** — for each selected diagram type, produce a structured description. See [diagram-schema.md](diagram-schema.md) for the output format.

   Guidelines for abstraction level:
   - Component diagrams: use component names, not module paths
   - Sequence diagrams: one per data flow, actors on the left, external deps on the right
   - State diagrams: group by purpose (source-of-truth vs cache vs derived)
   - Keep labels short (3-5 words max on connections)
   - Annotate patterns on components only if they aid understanding
   - Include failure modes as annotations on the affected connections (dashed lines, warnings)

5. **Generate tutorial** (if `--tutorial` flag) — produce a brief walkthrough document structured as:
   - **What is this?** — from `purpose` + `stack`
   - **Who uses it?** — from `actors`
   - **How does it work?** — one section per `data_flow`, written as a narrative walkthrough referencing components by name
   - **What's stored where?** — from `state`, grouped by purpose
   - **What can go wrong?** — from `failure_modes`, ordered by severity

   Write in plain language. No code snippets. Reference component names as bold text. The goal is "understand the system in 5 minutes."

6. **Write output** — write to `<project>/.claude/agent-memory/scribe/`:
   - `diagrams.yaml` — structured diagram descriptions
   - `tutorial.md` — brief tutorial (only if `--tutorial` flag)

   Create the directory if needed. Delegate write to scribe via beorn if blocked.

7. **Report** — list which diagrams were generated and why, plus the tutorial if applicable.
