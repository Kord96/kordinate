# Diagram Description Schema

Level 3 resource for the illustrate skill. Defines the structured output format for diagram descriptions.

## Format

```yaml
project: "<project-name>"
generated: "<YYYY-MM-DD>"
source: "<path to architecture.yaml>"

diagrams:
  - viewpoint: structural | behavioral | data | deployment | failure
    zoom: <integer>                      # 1 = highest level, 2+ = deeper
    focus: "<component-id>"              # optional — which subtree to zoom into
    id: "<kebab-case-unique-id>"
    title: "<Human Readable Diagram Title>"
    reason: "<why this diagram is useful>"

    # Content depends on viewpoint:

    # structural: nodes + edges + groups (component relationships)
    groups:                              # optional logical groupings (subgraphs)
      - id: "<group-id>"
        label: "<Group Label>"
        components: ["<component-id>"]
    nodes:
      - id: "<component-id>"            # references architecture.yaml component
        label: "<display label>"
        type: "<component type>"
        group: "<group-id>"             # optional
        annotations: ["<pattern>"]      # optional
    edges:
      - from: "<node-id>"
        to: "<node-id>"
        label: "<short description>"
        style: solid | dashed           # dashed for optional/async

    # behavioral: actors + steps (sequence/flow diagrams)
    actors:                              # ordered left to right
      - id: "<component-id or actor-id>"
        label: "<display label>"
        position: left | center | right  # hint for layout
    steps:
      - from: "<actor-id>"
        to: "<actor-id>"
        action: "<verb phrase>"
        data: "<what moves>"             # optional
        style: solid | dashed | reply    # reply = return arrow
        note: "<annotation>"             # optional

    # data: stores + connections (what's stored where, who reads/writes)
    stores:
      - id: "<state-id>"                # references architecture.yaml state
        label: "<display label>"
        technology: "<tech name>"
        purpose: "<source-of-truth | cache | derived | staging>"
        component: "<component-id>"      # which component owns it
    connections:
      - from: "<component-id>"
        to: "<store-id>"
        label: "<read | write | read-write>"

    # deployment: infrastructure + workloads + connections (where things run)
    infrastructure:
      - id: "<node-or-namespace>"
        label: "<display label>"
        type: node | namespace | cluster
    workloads:
      - id: "<component-id>"
        label: "<display label>"
        kind: "<Deployment | StatefulSet | CronJob>"
        replicas: <count>
        infrastructure: "<node-or-namespace id>"
    connections:
      - from: "<workload-id>"
        to: "<workload-id>"
        label: "<protocol>"
        port: "<port number>"            # optional

    # failure: trigger + severity + affected + unaffected (blast radius)
    trigger: "<what fails>"
    severity: critical | high | medium | low
    affected_nodes:
      - id: "<component-id>"
        label: "<display label>"
        impact: "<what happens to this component>"
    unaffected_nodes:
      - id: "<component-id>"
        label: "<display label>"
```

## Conventions

- All `id` fields reference IDs from `architecture.yaml` — no new IDs invented
- Labels are short (3-5 words). Detail goes in `annotations` or `note` fields
- Sequence diagram steps follow the order in `architecture.yaml` data flows
- Groups in component diagrams map to logical tiers (frontend, backend, storage, external)
- Infrastructure diagrams use `style: dashed` for connections with no resilience configured — visual warning
- Failure blast radius shows affected components highlighted, unaffected components grayed — the contrast tells the story
- Each diagram has a `reason` field explaining why it was generated — this helps the user decide if they want to render it
- `viewpoint` determines the lens: structural (what connects to what), behavioral (what happens when), data (what's stored where), deployment (where things run), failure (what breaks)
- `zoom` determines depth: 1 = system overview, 2 = one level deeper, 3+ = focused detail. Higher zoom typically requires a `focus` component.
- `focus` narrows to a subtree: at zoom 1 you see everything, at zoom 3 focused on "enrichment-services" you see its children and their connections
- Not every viewpoint needs to be generated. Skip viewpoints that would be trivial (e.g., no deployment viewpoint if there are no k8s manifests)

## Example

For a simple frontend app:

```yaml
project: "sous-storefront"
generated: "2026-03-26"
source: ".claude/agent-memory/designer/architecture.yaml"

diagrams:
  - viewpoint: structural
    zoom: 1
    id: system-overview
    title: "sous-storefront — System Overview"
    reason: "9 components with clear tiered dependencies — shows the SSR/client split and external API dependency"
    groups:
      - id: server
        label: "Server (Node.js SSR)"
        components: ["ssr-server", "query-layer"]
      - id: client
        label: "Browser"
        components: ["ui-shell", "catalog-views", "checkout-module", "client-state"]
      - id: external
        label: "External"
        components: ["product-catalog-api"]
    nodes:
      - id: ssr-server
        label: "SSR Server"
        type: frontend
        group: server
      - id: query-layer
        label: "Data Fetching"
        type: library
        group: server
        annotations: ["dehydrate/hydrate"]
      - id: ui-shell
        label: "UI Shell"
        type: frontend
        group: client
      - id: catalog-views
        label: "Catalog Views"
        type: frontend
        group: client
      - id: checkout-module
        label: "Checkout"
        type: frontend
        group: client
      - id: client-state
        label: "Zustand Stores"
        type: library
        group: client
        annotations: ["cart", "theme"]
      - id: product-catalog-api
        label: "dummyjson.com"
        type: gateway
        group: external
    edges:
      - from: ssr-server
        to: query-layer
        label: "prefetch in loader"
      - from: query-layer
        to: product-catalog-api
        label: "GET products"
        style: dashed
      - from: catalog-views
        to: query-layer
        label: "infinite queries"
      - from: catalog-views
        to: client-state
        label: "add to cart"
      - from: ui-shell
        to: client-state
        label: "cart badge, theme"
      - from: checkout-module
        to: client-state
        label: "clear cart"

  - viewpoint: behavioral
    zoom: 1
    id: catalog-browse-flow
    title: "Product Catalog Browsing (SSR → Hydration)"
    reason: "The SSR dehydrate/hydrate bridge is the most architecturally non-obvious flow — worth diagramming"
    actors:
      - id: shopper
        label: "Shopper"
        position: left
      - id: ssr-server
        label: "SSR Server"
        position: center
      - id: query-layer
        label: "TanStack Query"
        position: center
      - id: product-catalog-api
        label: "dummyjson.com"
        position: right
    steps:
      - from: shopper
        to: ssr-server
        action: "GET /products"
      - from: ssr-server
        to: query-layer
        action: "Create server QueryClient, prefetch"
      - from: query-layer
        to: product-catalog-api
        action: "GET /products?select=...&limit=12"
        style: dashed
      - from: product-catalog-api
        to: query-layer
        action: "Product[] JSON"
        style: reply
      - from: query-layer
        to: ssr-server
        action: "Dehydrate cache"
        style: reply
      - from: ssr-server
        to: shopper
        action: "HTML + dehydrated state"
        style: reply
      - from: shopper
        to: shopper
        action: "HydrationBoundary rehydrates cache"
        note: "Client takes over — subsequent pages fetched directly"
```
