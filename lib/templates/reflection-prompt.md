Reflect on the work you just did. Save any insights worth remembering by posting them to the memory endpoint.

For each insight, decide the scope:
- **global** — reusable knowledge that applies across projects (patterns, techniques, anti-patterns, lessons learned)
- **project** — findings specific to the project you just worked on (its architecture, files, bugs, dependencies, debt, decisions)

Post each insight using python3 to avoid shell quoting issues:

```bash
python3 -c "
import json, urllib.request
data = json.dumps({
    'path': '<topic>.md',
    'content': '''<your insight>''',
    'scope': '<global|project>',
    'project': '{{PROJECT}}'
}).encode()
req = urllib.request.Request('http://localhost:9090/memory-update', data=data, headers={'Content-Type': 'application/json'}, method='POST')
print(urllib.request.urlopen(req, timeout=5).read().decode())
"
```

Where `<topic>` groups related insights (e.g., `architecture.md`, `debt.md`, `patterns.md`, `resilience.md`).

{{NO_PROJECT_NOTICE}}

Rules:
- Only save non-obvious insights that would be valuable in future work
- Do not repeat things you have already read from your memory files
- One post per topic — batch related insights into a single post
- If you have nothing worth remembering, say so and move on
