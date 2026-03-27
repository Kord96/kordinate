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

