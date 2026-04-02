Reflect on the work you just did. Save any insights worth remembering by posting them to the memory endpoint.

For each insight, decide the scope:
- **global** — reusable knowledge that applies across projects (patterns, techniques, anti-patterns, lessons learned)
- **project** — findings specific to the project you just worked on (its architecture, files, bugs, dependencies, debt, decisions)

Post each insight using:

```bash
curl -s http://localhost:9090/memory-update \
  -H "Content-Type: application/json" \
  -d '{
    "path": "<topic>.md",
    "content": "<your insight>",
    "scope": "global|project",
    "project": "{{PROJECT}}"
  }'
```

Where `<topic>` groups related insights (e.g., `architecture.md`, `debt.md`, `patterns.md`, `resilience.md`).

Rules:
- Only save non-obvious insights that would be valuable in future work
- Do not repeat things you have already read from your memory files
- One curl per topic — batch related insights into a single post
- If you have nothing worth remembering, say so and move on
