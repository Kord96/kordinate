---
description: Designer review workflow — identify, compare, review, report
---
# Workflow

1. **Identify frameworks in use** — check imports, not the project name.

2. **Compare against knowledge docs** — is the project using the framework correctly? Check per-repo .md for patterns, key classes, review checklists. Look for anti-patterns, missing primitives, wrong abstractions.

3. **Review structure** — directory layout, naming, consistency.

4. **Report** — categorize findings as CRITICAL (convention violations), RECOMMENDED (framework opportunities), MINOR (style).

5. **Produce architecture doc** — after review, produce or update `docs/architecture.md` in the project repo:

   ```markdown
   # Architecture

   ## Data Flow
   <ASCII art: components, connections, data direction>

   ## Components
   | Component | Purpose | Pattern |

   ## Dependencies
   Kafka, Postgres, Redis, <etc>

   ## Notes
   <Anything unusual, known constraints, tech debt>
   ```

6. **Scaffold missing boilerplate** — if the project uses stoik or orchestrator but is missing framework boilerplate, scaffold it. Only add what's missing.
