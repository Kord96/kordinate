# Component Identification Guidance

Level 3 resource for the architect skill. Referenced from step 4 (identify components). Defines what to extract and how to filter.

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
- **patterns**: from detect-patterns output or concept catalog
- **depends_on**: other component ids (directional: A depends_on B means A calls/imports/consumes from B)

## Relationship Mapping

`depends_on` captures directional dependencies: if A calls, imports, or consumes from B, then A depends_on B. To decide whether a relationship belongs in `depends_on`:

- **Yes**: A imports B's module, A calls B's API, A reads from B's store, A consumes B's events
- **No**: both A and B import a shared utility (incidental coupling, not structural)
- **No**: A and B happen to run in the same process (co-location, not dependency)

For richer relationship detail (what flows, transport, direction), use `data_flows` and `events` rather than trying to encode it in `depends_on`.