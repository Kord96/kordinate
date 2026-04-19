---
description: Augur roadmap — prioritized product plan for analysis metadata, ask, evolution, feedback, and design
---
# Roadmap

## Ordering

1. **Analysis metadata and run telemetry**
2. **Ask / grounded architectural Q&A**
3. **Timeline / architectural evolution across commits**
4. **User edits and feedback capture**
5. **Design mode using the same validation and memory engine**

This order is intentional:
- step 1 creates the trust, cost, and regression substrate for everything else
- step 2 turns existing analysis artifacts into an interactive product surface
- step 3 is a second major workflow and should be a sibling to `analyze`, not an overloaded extension of it
- steps 4 and 5 depend on a strong feedback and edit model, so they come later

## Phase 1 — Analysis Metadata and Telemetry

Goal:
- make every analysis auditable, comparable, and operationally measurable

Required outputs:
- `meta.json` stores:
  - execution identity: provider, runtime, model, models, bundle/runtime versions
  - validation identity: attempts, pass/fail, repair status
  - telemetry:
    - wall time
    - CPU time
    - peak RAM / RSS
    - token usage
    - estimated cost when available
- docs and API expose this cleanly per analysis

Why first:
- needed for trust, ops, cost tracking, regressions, and future evaluation

## Phase 2 — Ask

Goal:
- let users ask grounded architectural questions against atlas, stories, narratives, facts, and symbols

Key requirements:
- GUI selection should auto-reference components, flows, state, dependencies, failure scenarios, and symbols
- the ask path must know which analysis and overlay it is grounded in
- decide hosted-model vs bring-your-own-model boundary

Likely outputs:
- grounded question context builder
- explicit exposed artifacts contract
- answer provenance / grounding UI

## Phase 3 — Evolution / Timeline

Goal:
- analyze how architecture changed across commits, PRs, and issues

Important principle:
- this should likely become a sibling workflow such as `evolve`, not just a larger `analyze`

Inputs likely needed:
- stronger git diff
- commit messages
- PR titles/bodies/discussions
- open issues
- analysis-to-analysis comparison

Outputs likely needed:
- pivotal moments
- architectural drift
- change narratives
- why a structure appeared, split, or disappeared

## Phase 4 — Edits and Feedback

Goal:
- let users correct Augur naturally and persist those corrections so future analyses improve

First-class feedback should prefer structure over raw prose:
- wrong grouping
- missing component
- wrong dependency
- bad summary
- weak narrative
- missing failure path

Longer term:
- graph interactions
- drag/drop refinement
- explicit overlay learning pipeline back into Augur

## Phase 5 — Design

Goal:
- reuse the atlas/story/narrative/validation engine for systems that do not exist yet

Flow:
- user explains intent
- Augur produces the same kind of artifacts
- user edits/refines them
- validated artifacts can be handed to an implementation agent for scaffolding

Design depends on:
- mature edit mode
- strong feedback learning loop
- robust validation and memory reuse

## Immediate Next Work

Now:
1. complete phase 1 end to end
2. surface metadata in docs per analysis
3. then design the ask substrate around selection and grounding
