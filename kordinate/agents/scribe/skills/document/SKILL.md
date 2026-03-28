---
name: document
description: Generate documentation — architecture diagrams, tutorials, and other doc artifacts. Use for generating visual docs, architecture explorers, or project documentation.
argument-hint: "architecture <project> [--narrative <dir>] | (future: api, onboarding, narrative)"
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

### 2. Invoke Designer analysis

Spawn a Designer subagent to analyze the project:

```
Agent(subagent_type="designer", prompt="Run full project analysis on <project-path>. Execute in order: /detect-patterns, /map-dependencies, /review-api, /assess-debt, /architect. Write all outputs to <project-path>/.kord/agents/augur/memory/. Return a manifest of what was produced.")
```

Wait for the result. If the agent fails or times out, proceed with whatever artifacts already exist at `<project>/.kord/agents/augur/memory/` and mark the report as `stale — Designer failed`.

### 3. Read project artifacts

Read from `<project>/.kord/agents/augur/memory/` — this is the only authoritative location. Do not read from the project root, the docs site, or any other path.

| File | Required | Purpose |
|------|----------|---------|
| `architecture.yaml` | **yes** | Core structure — abort if missing |
| `patterns.md` | no | Enriches nodes with pattern badges |
| `dependencies.md` | no | Enriches external service nodes |
| `api-review.md` | no | Adds API endpoint mapping to nodes |
| `debt-assessment.md` | no | Adds health coloring per node |

If `architecture.yaml` is missing after the kord attempt, report and suggest running `/architect <project>` directly. Exit.

### 4a. Produce architecture.json — write

This is the core creative step. Prose quality is the priority — write first, annotate in step 4b.

Produce this as **one thought**, not a mechanical transform. Hold the full picture and express it as a single coherent artifact.

**Output structure:**

```json
{
  "nodes": [...],
  "edges": [...],
  "data_flows": [
    {
      "id": "flow-id",
      "name": "Human-readable name",
      "narrative": "When a shopper opens the home page, **root-loader** fires...",
      "steps": [
        { "component": "root-loader", "action": "fetches categories", "to": "api-client" }
      ]
    }
  ],
  "state": [
    {
      "id": "store-id",
      "name": "Cart Store",
      "narrative": "Cart state lives in **localStorage** rather than server-side...",
      "purpose": "source-of-truth",
      "readers": ["cart-drawer", "checkout-page"],
      "writers": ["add-to-cart-handler"]
    }
  ],
  "failure_modes": [
    {
      "id": "failure-id",
      "severity": "critical",
      "narrative": "At 2am, DummyJSON starts returning 503s. The **circuit-breaker** opens...",
      "cascade": [{ "component": "api-client", "effect": "..." }],
      "detection": [...],
      "recovery": [...]
    }
  ],
  "overview": "Brief C4 Context paragraph — what this system does, who uses it.",
  "structure_narrative": "The system runs across **server**, **browser**, and **external**..."
}
```

**Constraints — every reference must resolve:**
- Every `component` in a flow step must exist in `nodes[].id`
- Every flow step pair (step N → step N+1) creates an edge with `flowId` — do not create flows without connected edges
- Every `**bold-text**` in any narrative must match a `nodes[].id` or `nodes[].name`
- Every `cascade[].component` in failure modes must exist in `nodes[].id`
- Every `readers[]` and `writers[]` in state must exist in `nodes[].id`
- Do not reference components that don't exist in the nodes array

**Hierarchy — 3-5 top-level groups maximum.** Follow the C4 Container model: top-level groups are runtime boundaries (Server, Browser, External), not modules. Everything nests inside. Groups beyond depth 2 become regular nodes.

**Narrative approach — all narratives are one coherent story:**

The `overview`, `structure_narrative`, flow narratives, state narratives, and failure narratives are not independent texts. They are chapters of the same story, written in one pass. A flow narrative should reference what the structure narrative established. A failure narrative should reference the flows it disrupts. A state narrative should explain why a particular flow stores data the way it does.

Write them as if you're explaining the entire system to a smart colleague who's never seen it. Start with the big picture (overview), zoom into how things are organized (structure), trace what happens when users interact (flows), explain where truth lives (state), and finally show what happens when things break (failures). Each section assumes the reader has read the previous ones.

Follow the voice, formatting, and structure rules in [narrative-style.md](narrative-style.md). Read it before writing any narrative content. Key points: short paragraphs separated by `\n\n`, scenario-driven voice, lead with action, em dashes not hyphens, ~100-150 words per flow/failure/store narrative.

**Enrichments from Designer artifacts** (integrate into nodes, don't list separately):
- Pattern badges from `patterns.md` → `node.patterns[]`
- Debt markers from `debt-assessment.md` → `node.debt`
- API endpoints from `api-review.md` → `node.endpoints[]`
- External dep resilience from `dependencies.md` → `node.resilience`

### 4b. Annotate narratives — match paragraphs to structure

Re-read all narratives from step 4a. For each one, produce a `narrative_map` array that tags each paragraph with the structural elements it describes. **Do not change the prose** — just annotate it.

Split each narrative on `\n\n` into paragraphs. For each paragraph, identify what it covers:

- **Flow narratives** → `"steps": [1, 2, 3]` — which step indices (1-based) the paragraph describes. A paragraph covers a step if it mentions any component involved in that step.
- **State narratives** → `"refs": ["cart-drawer", "checkout-page"]` — which component IDs the paragraph references.
- **Failure narratives** → `"cascade_steps": [1, 2]` and/or `"refs": [...]` — which cascade steps and components.
- **Structure narrative** → `"refs": ["server", "root-loader"]` — which node IDs (groups or components).

Add `narrative_map` alongside the existing `narrative` string:

```json
{
  "narrative": "para1\n\npara2\n\npara3",
  "narrative_map": [
    { "text": "para1", "steps": [1, 2, 3] },
    { "text": "para2", "steps": [4, 5] },
    { "text": "para3", "steps": [6, 7, 8] }
  ]
}
```

For `structure_narrative`, add a top-level `structure_narrative_map`:

```json
{
  "structure_narrative_map": [
    { "text": "The system runs across three boundaries...", "refs": ["server", "browser", "external"] },
    { "text": "The **Agent System** coordinates...", "refs": ["agent-system", "main-agent"] }
  ]
}
```

**Validation:**
- Every paragraph must appear in `narrative_map`
- Every step/cascade index must be covered by at least one paragraph
- Every `refs[]` value must exist in `nodes[].id`

**Gemini review** — after completing both 4a and 4b, run a background Gemini review per `~/.kord/shared/gemini-protocol.md`. Verify: references resolve, narrative is a story not a list, step ranges are correct. Fix valid critiques.

Write to `<docs-content-dir>/<project>/architecture.json`.

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
