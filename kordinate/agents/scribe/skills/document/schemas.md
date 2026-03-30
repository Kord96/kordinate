# Component Data Schemas

What each pre-built component expects as input. Scribe produces this data — the components handle rendering.

## JourneyPage

The top-level page component. One per journey.

```typescript
{
  project: string,              // project name
  journeys: Journey[],          // all journeys (for tab switching)
  storiesByJourney: {           // journeyId → ordered stories
    [journeyId: string]: Story[]
  },
  atlas: AtlasJson,             // full atlas.json
  rendering: Manifest,          // manifest.json (rendering decisions)
  repoUrl?: string              // optional link to source repo
}
```

## Story (passed to StoryCard via JourneyPage)

Each story is a YAML object from augur's stories/ directory. StoryCard expects:

```typescript
{
  id: string,                   // kebab-case
  title: string,
  summary: string,              // markdown with **bold refs** → atlas node IDs
  tags?: string[],
  parent: string | null,        // root stories have null
  children?: string[],          // child story IDs

  structures?: [{               // → rendered by GraphBlock
    id: string,
    title?: string,
    type?: string,              // "component topology", "data lineage", etc.
    nodes: [{ id: string, children?: string[] }],
    edges: [{ from: string, to: string, label?: string, type?: string }]
  }],

  flows?: [{                    // → SequenceDiagram or TimelineCard
    id: string,
    title?: string,
    type?: string,              // "failure cascade" → TimelineCard, others → SequenceDiagram
    trigger?: string,           // for failure cascades
    severity?: string,          // for failure cascades
    detection?: string[],       // for failure cascades
    recovery?: string[],        // for failure cascades
    steps: [{
      node: string,             // atlas component ID
      to?: string,              // target component ID
      action?: string,          // what happens
      effect?: string,          // alternative to action
      observation_ids?: string[] // inline observations
    }]
  }],

  observations?: [{             // → rendered by ObservationCard
    id: string,
    finding: string,
    confidence: "high" | "medium" | "low",
    component?: string,         // atlas component ID
    evidence?: {
      file?: string,
      lines?: number[],
      snippet?: string          // code snippet for evidence cards
    },
    tags?: string[],
    recommendation?: string,    // if present, renders as warning card
    type?: string,              // "gap" renders as warning card
    observation_ids?: string[]  // for inline attachment to nodes/steps
  }],

  rationale?: [{                // → rendered by RationaleCard
    id: string,
    decision: string,
    context: string,
    trade_offs: string,
    alternatives?: string[]     // dismissed options
  }],

  evaluation?: {
    groundedness: number,
    coverage: number,
    claim_count: number,
    ungrounded_claims: string[]
  }
}
```

## Journey (YAML from augur's journeys/ directory)

```typescript
{
  id: string,
  title: string,
  description?: string,
  audience?: string[],
  stories: string[]             // ordered story IDs — render in this sequence
}
```

## Manifest (rendering decisions by scribe)

Written to `$CONTENT/manifest.json`. Records scribe's visualization choices.

```typescript
{
  project: string,
  generated: string,            // YYYY-MM-DD
  stories: [{
    storyId: string,
    blocks: [{
      type: "structure" | "flow" | "observation" | "rationale",
      sourceId: string,         // matches the block's id in the story
      render: string,           // "dagre" | "cose-bilkent" | "grid" | "sequence" | "timeline" | "evidence-card" | "warning-card" | "decision-card"
      nodeCount?: number        // for structures — determines graph layout
    }]
  }],
  atlas: {
    nodeCount: number,
    groupCount: number,
    coveragePercent: number
  }
}
```

## AtlasPage

Full interactive graph. Expects:

```typescript
{
  project: string,
  atlas: AtlasJson,             // full atlas.json
  storyByNode: {                // nodeId → storyIds that reference it
    [nodeId: string]: string[]
  },
  stories: Story[]              // all stories (for drawer content)
}
```

## Key Rules

- All node/component IDs in stories MUST exist in atlas.json
- **bold refs** in summaries resolve to atlas node IDs (kebab-case)
- `flow.type === "failure cascade"` → TimelineCard, everything else → SequenceDiagram
- GraphBlock auto-selects layout by node count: 1-3 grid, 4-8 dagre, 9+ cose-bilkent
- ObservationCard auto-selects variant: has snippet → evidence, has recommendation → warning, else → compact
