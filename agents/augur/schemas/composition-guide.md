# Story & Journey Composition Guide

Shared instructions for composing stories and journeys from an atlas — whether the atlas describes existing code (from /analyze) or a proposed design (from /design).

## Story Tree

Build a tree of stories that mirrors the atlas structure. Top-down:

**1. Root stories (3-5, one per atlas group).** For each group, write a root story that orients the reader: what components this group contains, how they relate, why this grouping exists. Root summaries are 2 paragraphs max, ~50-80 words. Set `parent: null`, list `children`.

**2. Child stories (2-5 per root).** For each root, identify the concerns worth zooming into — a key flow, a data store, a failure mode, a design decision. Write a child story for each. Child summaries are 3 paragraphs max, ~80-120 words. Set `parent: "<root-id>"`. Children can reference atlas nodes from outside the parent's group when the concern crosses boundaries.

**3. Journeys.** Always create `getting-started.yaml` — a teaching-order journey for someone new to the system, pulling stories from all groups in the sequence they should be read. Beyond that, create additional journeys for cross-cutting concerns (e.g., resilience review, security audit, data flow walkthrough). 3-8 stories per journey.

**Getting-started journey requirements:**
- The first story must orient with the domain model and purpose — what this system is and one concrete thing to follow through it.
- Each story must identify its anchor — the single best reference point (a file, an interface, or a component).
- Include bridge text between each story — one sentence question that pulls the reader forward. Pattern: "[What you just learned]. But [question that pulls you forward]?"
- Bridge text is not required for other journeys.

## Building Blocks

Each story is assembled from:
- **summary** (required) — short paragraphs, depth-dependent length
- **structures** — nested components + typed edges
- **flows** — ordered steps, typed
- **observations** — evidence-backed findings (for /analyze) or design rationale (for /design)
- **rationale** — design decisions, trade-offs, alternatives

All prose follows [writing-guide.md](writing-guide.md). For failure flows: include trigger, severity, detection, recovery. For data structures: use `reads`/`writes` edge types.

## Typical Output

- 3-5 root stories
- 8-20 child stories
- 1-3 journeys

## Refinement

Review each story. If a summary makes a claim not directly supported by the atlas data, verify or correct it. For /design, ensure all design decisions have rationale.
