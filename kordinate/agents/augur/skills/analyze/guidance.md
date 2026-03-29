# Component Identification Guidance

Level 3 resource for the analyze skill. Referenced from step 5 (identify components and groups). Defines what to extract, how to filter, and how to assign groups.

## Filtering Criteria

The goal is to surface abstractions that define the system's shape, not every module.

**Include as top-level components:**
- Entry points (servers, CLI, main) -- where actors meet the system
- Data stores and external integrations -- system boundaries
- Business-domain abstractions -- the core "what it does"

**Skip as top-level components:**
- Utilities, logging, config modules -- high fan-in plumbing, not structure
- When in doubt, prefer business-domain over infrastructure

## Per-Component Extraction

For each component, capture:
- **id**: kebab-case, unique
- **name**: human-readable (not a module path)
- **type**: one of `service | library | worker | api | frontend | cli | scheduler | store | gateway | broker`
- **description**: one sentence of what it does
- **modules**: source files that implement it
- **abstraction**: levels from `abstractions.md` (e.g., `[data, messaging]`) -- these drive which viewpoints downstream skills generate
- **patterns**: from detect-concepts output or concept catalog
- **depends_on**: other component ids (directional: A depends_on B means A calls/imports/consumes from B)

## Relationship Mapping

`depends_on` captures directional dependencies: if A calls, imports, or consumes from B, then A depends_on B. To decide whether a relationship belongs in `depends_on`:

- **Yes**: A imports B's module, A calls B's API, A reads from B's store, A consumes B's events
- **No**: both A and B import a shared utility (incidental coupling, not structural)
- **No**: A and B happen to run in the same process (co-location, not dependency)

For richer relationship detail (what flows, transport, direction), use `data_flows` and `events` rather than trying to encode it in `depends_on`.

## Group Assignment

After identifying components, assign each to exactly one of **3-5 top-level groups**. This is a hard constraint.

Groups are structural clusters — not business capabilities, not deployment units. A group should contain components that share a deployment boundary, data flow path, or architectural concern.

Rules:
- Follow C4 Container model: top-level groups are runtime boundaries (Server, Browser, External), not code modules
- Synthetic `external` and `actors` groups count toward the 3-5 limit
- Small projects (<15 nodes) should aim for 3 groups
- If two groups have only 1-2 nodes each, they belong together
- After drafting, count groups. If >5, merge the two most closely related. Repeat until ≤5

Each group becomes a structure story in Phase 2. The groups you create here directly determine how the architecture is narrated — choose groupings that tell a coherent story about the system's shape.