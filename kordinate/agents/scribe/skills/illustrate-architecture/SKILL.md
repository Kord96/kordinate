---
name: illustrate-architecture
description: >
  Generate an interactive architecture explorer page from Designer's project analysis.
  Reads architecture.yaml, patterns.md, dependencies.md, api-review.md, and debt-assessment.md
  from project memory, then produces an Astro page with Cytoscape.js graph, narrative sidebar,
  and bottom drawer.
argument-hint: "<project> [--narrative <dir>]"
curated: true
scope: global
context: fork
---

Generate an interactive architecture explorer page by reading all of Designer's project memory artifacts and producing a self-contained Astro page with a Cytoscape.js graph, a narrative sidebar, and a bottom drawer for detail inspection.

## Arguments

`$ARGUMENTS` — Required: `<project>` (e.g., `logbd`, `stoik`, `sous-storefront`). Optional: `--narrative <dir>` to supply hand-written narrative markdown files instead of auto-generated stubs.

## Procedure

### 1. Parse and locate

Parse project name from `$ARGUMENTS`. Extract `--narrative <dir>` if present.

Locate the project directory by checking paths in order:
- `/kord/projects/<project>/`
- `~/<project>/`
- If `$ARGUMENTS` starts with `/`, treat it as an absolute path

If not found, report which paths were checked and exit.

### 2. Ensure fresh analysis via kord

**This step is mandatory — never skip it.** Invoke `/kord designer project-analysis <project-path>` to ensure Designer's analyses are up to date. The kord's expiry.sh handles caching: if the project source hasn't changed since the last analysis, Designer returns immediately without re-running. You do not decide whether to skip — the cache does.

Do not check for existing files, existing architecture.json in the docs site, or any other indicator to bypass this step. Always invoke the kord. The presence of old outputs does not mean they are fresh.

If the kord returns an error (e.g., Beorn unreachable), report the error and proceed with whatever artifacts already exist at the primary path. Mark the output as "stale — kord failed" in the final report.

### 3. Read project artifacts

Read from `<project>/.kord/agents/designer/memory/` — this is the only authoritative location. Do not read from the project root, the docs site, or any other path.

| File | Required | Purpose |
|------|----------|---------|
| `architecture.yaml` | **yes** | Core structure — abort if missing |
| `patterns.md` | no | Enriches nodes with pattern badges |
| `dependencies.md` | no | Enriches external service nodes |
| `api-review.md` | no | Adds API endpoint mapping to nodes |
| `debt-assessment.md` | no | Adds health coloring per node |

If `architecture.yaml` is missing after the kord attempt, report and suggest running `/architect <project>` directly. Exit.

### 4. Build architecture.json

Transform `architecture.yaml` into the JSON format described in [explorer-schema.md](explorer-schema.md). This is the data file the ArchExplorer component consumes at build time.

**Key field names** — the component reads these exact keys:
- Nodes use `name` (not `label`) for display text
- Nodes use `hasChildren: true` for parent/group nodes, `parent` for nesting
- Nodes use `file` (not `modules`) for source file path, `exports` for exported symbols
- Top-level `data_flows` (not `flows`) for flow objects
- Top-level `state` (not `stores`) for state/store objects
- Top-level `failure_modes` (not `failures`) for failure objects
- Edges use `flowId` to associate with a data flow; edges without `flowId` are dependency edges

**Hierarchy constraint — 3-5 top-level groups maximum.** The graph should feel spacious, not cluttered. Follow the C4 Container model: top-level groups are runtime boundaries (e.g., Server, Browser, External), not every module or directory. Everything else nests inside as children or grandchildren. If the architecture.yaml has more than 5 top-level components, consolidate them into broader containers. Groups beyond depth 2 should become regular component nodes, not groups — the user drills down by expanding, not by seeing a flat sea of boxes.

Reference: the existing sous-storefront explorer uses 3 groups (Server, Browser, External) with 83 nodes nested inside. That's the right density.

**Base transform** (from architecture.yaml alone):

- **Top-level groups**: Create 3-5 group nodes representing runtime/deployment boundaries. Typical: `server` (SSR, API, loaders), `browser` (client app, UI, state), `external` (third-party services, APIs). Map each architecture.yaml component to the appropriate group based on where it runs.
- Each **component** becomes a node: `{ id, name, description, type, parent, file, exports, hasChildren }`. Set `parent` to the containing group. Components that contain children become nested group nodes, but only at depth 1-2. At depth 3+, use regular nodes.
- Each **depends_on** relationship becomes an edge: `{ source, target, label }`
- Each **external_dependency** becomes a node with `type: "external"`, grouped under the `external` top-level group
- Each **data_flow** from the YAML becomes a `data_flows[]` entry with `{ id, name, description, trigger, steps[] }`. Each step: `{ component, action, data, to, technology }`. Also create edges with `flowId` linking the step components.
- Each **state** entry becomes a `state[]` entry: `{ id, name, description, purpose, technology, component, persistence, readers[], writers[] }`
- Each **failure_mode** becomes a `failure_modes[]` entry: `{ id, trigger, severity, impact, cascade[], detection[], recovery[] }`

**Enrichments** (from optional files):

- **Pattern badges** (from `patterns.md`): Match patterns to component nodes. Add a `patterns` array with `{ name, category }`.
- **Debt markers** (from `debt-assessment.md`): Map debt items to affected nodes. Add a `debt` object with `{ severity, items: [{ title, description }] }`. Severity drives node border coloring.
- **API endpoints** (from `api-review.md`): Map routes to component nodes. Add `endpoints` array with `{ method, path, description }`.
- **External deps enrichment** (from `dependencies.md`): Add `resilience` object `{ timeout, retry, circuitBreaker, fallback }` and `criticality` to external nodes.

Write `architecture.json` to `<docs-content-dir>/<project>/architecture.json`. See step 7 for path resolution.

### 5. Write narrative

The sidebar narrative is the story that guides readers through the architecture. It is not a bullet-point list — it is **prose that Scribe writes**, using everything learned from the Designer memories.

The narrative follows three complementary approaches:

**C4 multi-level structure** — Each tab's narrative starts at the highest level of abstraction and drills down. The reader should be able to stop at any depth and have a coherent understanding.

**Scenario-driven writing** — Instead of describing components abstractly, trace them through real user journeys. Name concrete actors and actions: "When Sarah browses the category page, the **CategoriesQuery** fires a prefetch from the **root loader**..." This makes architecture tangible — readers understand *what happens*, not just *what exists*.

**Decision anchors** — When a pattern or architectural choice is mentioned, briefly explain *why* it was chosen and what was traded off. Draw from detected patterns and debt data: "The team uses **circuit-breaker** on the DummyJSON client rather than simple retry — the API has long failure windows where retrying would just queue up timeouts." If Designer found anti-patterns or debt, frame them as open decisions: "The **ProductService** currently bypasses the port layer and queries the API directly. This creates coupling that the hexagonal pattern was meant to prevent — a candidate for refactoring."

Write one markdown file per tab into `<docs-content-dir>/<project>/narrative/`:

- **`structure.md`** — Start with a C4 Context-level paragraph: what this system does in the world, who uses it, what it connects to. Then zoom to Container level: the major runtime boundaries (server, browser, external services) and how they communicate. Then Component level: one section per module group, written through the lens of a user journey. Reference component names in bold for graph linking. Weave in patterns, debt, and decisions naturally — don't list them separately.

- **`flows.md`** — Each flow is a mini-story with a named protagonist. "When a shopper opens the home page, the **SSR server** runs three loaders in sequence. The **root loader** fetches categories from DummyJSON — this call is protected by a **circuit breaker** because..." Explain what happens at each step, why the data moves that way, and what would happen if a step failed. Cross-reference the resilience tab for failure scenarios.

- **`data.md`** — Frame around the question "where does truth live?" Group stores by purpose. For each: what state it holds, who reads it, who writes it, what happens on conflict, and why this storage choice was made. "Cart state lives in **localStorage** rather than server-side — the team traded session persistence for offline capability and zero-latency adds."

- **`resilience.md`** — Each failure mode is a scenario: "At 2am, the DummyJSON API starts returning 503s. The **circuit breaker** opens after 5 failures in 30 seconds. The **API client** switches to cached responses via **graceful degradation**. Users see slightly stale category data but the site stays up. The **health check** reports degraded status, and the Grafana alert fires..." Connect back to architecture decisions — this is where those choices pay off (or don't).

**If `--narrative <dir>` is provided**: read existing markdown files from that directory. Use them as-is for the tabs they cover. For tabs without a file, write new narrative as above.

Each heading in the narrative should use `{#component-id}` syntax to anchor it to a graph node for bidirectional linking. For example: `## API Layer {#api-gateway}`.

**Gemini review** — after writing the first tab's narrative, kick off a background review of it while you write the remaining tabs:
```bash
gemini -m gemini-2.5-pro -o json -p "Review this architecture narrative against the source data. Flag: inaccuracies (narrative says X but data shows Y), missing context (important components or flows not mentioned), misleading simplifications, and broken component name references. Also flag if the narrative reads like a bullet list instead of a story." @architecture.yaml < structure.md > /tmp/gemini-review-narrative.json &
```
Continue writing `flows.md`, `data.md`, `resilience.md`. Before finalizing, read the Gemini review and revise the narrative where critiques are valid. Then kick off a review of the remaining tabs if time permits. The goal is not perfection — it's catching factual errors and blind spots that a second perspective reveals.

### 6. Write the explorer page

Write a self-contained Astro page to `<docs-pages-dir>/<project>/index.astro`.

The page structure:

```
+------------------------------------------------------------------+
|  [project name] Architecture Explorer          [tab1][tab2][tab3] |
+-------------------------------------------+----------------------+
|                                           |                      |
|                                           |  Narrative Sidebar   |
|           Cytoscape.js Graph              |  (tabbed markdown)   |
|           (interactive)                   |                      |
|                                           |  - Structure         |
|                                           |  - Flows             |
|                                           |  - Data              |
|                                           |  - Resilience        |
+-------------------------------------------+----------------------+
|  Bottom Drawer (click a node to inspect)                         |
|  - Component detail, patterns, debt, endpoints, failure modes    |
+------------------------------------------------------------------+
```

**Graph panel** (Cytoscape.js):
- Load `architecture.json` at build time via Astro's content layer or inline as a `<script>` data blob
- Nodes colored by type: service=blue, library=gray, api=green, store=amber, frontend=purple, external=red, actor=teal, worker=indigo
- Debt-affected nodes get a colored border ring (red/orange/yellow by severity)
- Pattern badges shown as small pill labels below node name
- Edges styled by relationship: solid for depends_on, dashed for async/event
- Layout: `dagre` (top-to-bottom) for structural view, `breadthfirst` for flow view
- Click a node to populate the bottom drawer
- Hover shows tooltip with component description
- Zoom, pan, fit-to-screen controls

**Narrative sidebar**:
- Tabbed interface: Structure | Flows | Data | Resilience
- Render the narrative markdown for each tab
- Clicking a component name in the narrative highlights the node in the graph

**Bottom drawer**:
- Hidden by default, slides up on node click
- Shows: component name, description, type, patterns (as pills), debt items (as warnings), API endpoints (as a mini table), failure modes affecting this node, dependencies (in and out)
- Close button to dismiss

**Technical requirements for the Astro page**:
- Self-contained: inline all JS/CSS, load Cytoscape.js and dagre layout from CDN (`https://unpkg.com/cytoscape@3/dist/cytoscape.min.js`, `https://unpkg.com/cytoscape-dagre@2/cytoscape-dagre.js`, `https://unpkg.com/dagre@0.8/dist/dagre.min.js`)
- Use Astro's `<script>` tag for client-side interactivity
- Use CSS custom properties for theming (works with Starlight's dark/light mode)
- Responsive: sidebar collapses to overlay on mobile
- The page should work both in dev mode and as a built static page

### 7. Path resolution for output

The docs site content lives at (resolve in order):
1. If `$KORDINATE_HOME/../site/` exists, use it (PVC layout: `kordinate/site/`)
2. If a `site/` directory exists in the kordinate repo root, use it
3. Otherwise create output at `<project>/.kord/agents/scribe/output/architecture-explorer/`

Within the resolved docs root:
- Pages: `src/pages/<project>/index.astro`
- Content: `src/content/docs/<project>/architecture.json`
- Narrative: `src/content/docs/<project>/narrative/*.md`

If the docs site path does not exist (option 3 fallback), write all files into the project-local output directory and report that the user should copy them to the docs site manually.

### 8. Report

Output a summary:

```
## Architecture Explorer: <project>

**Page**: <path to index.astro>
**Data**: <path to architecture.json>
**Narrative**: <path to narrative dir> (N files)

### Enrichments included
- Patterns: yes/no (N patterns mapped to M nodes)
- Debt: yes/no (N items across M nodes)
- API endpoints: yes/no (N endpoints mapped)
- External deps: yes/no (N services)

### Graph stats
- Nodes: N (components: X, external: Y, actors: Z)
- Edges: N
- Flows: N
- Failure modes: N

### Notes
- <any warnings, stale data notices, missing optional files>
```
