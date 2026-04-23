---
name: analyze
description: >
  Semantic phase for Augur /analyze. Consumes a prepared run directory, follows
  the prepared full or incremental guidance, writes atlas/stories/narratives,
  and runs the validator until clean.
---

# Analyze

Semantic phase for Augur `/analyze`.

The deterministic phase is already done. Work from the prepared run directory, produce semantic outputs, and own the local validate-fix loop until the output is clean.

Operational path rules for this runtime:
- the runtime provides one canonical repo root and one canonical output directory for this request
- if `workspace.agent_root` is present, treat it as the stable base for agent-owned resources
- if `resources.concept_catalog_index` or `resources.framework_catalog_index` are present, start there for on-demand semantic reads instead of browsing the catalogs
- if `workspace.agent_root` is present, treat `workspace.agent_root/schemas/` as the canonical schema base; facts-layer contracts live under `workspace.agent_root/schemas/facts/`, while atlas, story, and narratives contracts remain under `workspace.agent_root/schemas/`
- do not manually reconstruct or shorten the output directory
- do not create sibling run directories with guessed suffixes
- generated artifacts belong in the canonical output directory for this request

## Produce `atlas.json`, `stories/`, and `narratives.yaml`, then validate and repair them until clean, using the prepared semantic inputs in the canonical output directory for this run.

1. Read startup inputs first.
   - `blast.json`
   - `startup.json`
   - `index.json`
   - the small startup files listed in `startup.json`
   - treat `startup.json` as the startup authority for startup order
   - treat `index.json` as the canonical manifest and retrieval guide for deterministic and derived artifacts in this run

2. Follow the mode-specific instructions already provided by the runtime.
   - the semantic mode is determined before this skill runs
   - the runtime appends the matching guide from `modes/full.md` or `modes/incremental.md`
   - do not choose your own mode
   - if you are invoked despite `skip`, stop

3. Use facts as guidance, then move into repo code.
   - treat deterministic artifacts as guidance, not final truth
   - use `index.json` as the source of truth for what each deterministic or derived artifact means, when to read it, how to use it, and what not to infer from it
   - use deterministic evidence in three tiers: startup orientation first, early architectural guidance next, targeted disambiguation only when needed
   - after startup orientation, move into repo code before doing more fact reduction
   - prefer entrypoints, runtime wiring, registrations, and cross-component communication over helpers, validators, docs, or support files when promoting major components
   - widen from fact-selected files into adjacent code until the ownership and dependency story is clear

4. Resolve concepts, frameworks, and other deterministic candidates evidence-first.
   - use the relevant deterministic artifacts as candidate guidance, not as final semantic truth
   - prefer `observations/concepts.json` as the normalized concept-assessment layer
   - prefer `observations/health.json` and `observations/failure-scenarios.json` as the normalized health and failure assessment layer
   - prefer `observations/components.json`, `observations/stories.json`, and `observations/narratives.json` as the decomposition and teaching-path assessment layer
   - for any materially relevant concept or framework, inspect the supporting repo code and resolve it as accepted, tentative, or rejected before it materially changes the atlas
   - answer attached review questions before accepting a materially relevant candidate
   - if ambiguity remains, use the provided concept/framework catalog entrypoints and read only the specific catalog files you actually need
   - prefer omitting or downgrading a concept over carrying a broad unresolved detector label
   - treat `atlas.json.concepts` as a compact layer of resolved cross-cutting interpretations, not a generic pattern dump

5. Reconcile the architecture before you write artifacts.
   - verify `components[].depends_on` reflects runtime reliance rather than presentation, hosting, or navigation
   - verify state entries stay truthful when backend class or persistence changes by configuration
   - verify the atlas graph, stories, and narratives tell the same ownership and dependency story
   - verify each claim uses concrete mechanism names from code when those names are available
   - when `facts/symbols-seed.json` or `facts/state-seeds.json` expose exact hooks, parsers, commands, registries, options, structs, enums, or selectors for cited files, prefer those exact names in grounded claims
   - if a mechanism name is emphasized, make sure it resolves either to a real atlas entity or to grounded evidence
   - when writing atlas health, prefer the layered model defined in the atlas schema:
     - `health.local` for failures inside one unit
     - `health.integration` for failures at seams with dependencies, stores, or callers
     - `health.propagation` for downstream degraded modes, stale results, blocked work, or wider blast radius
   - use health and failure observations as ranking and contradiction pressure, not as final truth without code grounding

6. Produce `atlas.json` in the canonical output directory.
   - consult the atlas schema before first write and again during repair if atlas validation fails
   - include `metadata` as part of the normal atlas contract
   - keep metadata grounded and compact; include materially relevant deterministic context, but do not mirror every detected fact into the atlas
   - keep component and flow `description` fields compact, but add `summary` when a click-through reader needs more than a one-line label
   - write component `summary` as the ownership/dependency explanation, not a prose copy of the title
   - write flow `summary` as the operating-path explanation, not a repeat of the trigger

7. Plan narratives first, then derive the story set from that teaching plan.
   - treat `system-overview` as the canonical repo overview narrative used downstream
   - allowed narrative ids are exactly: `system-overview`, `runtime-paths`, `state-and-data`, `integrations`, `operations-and-failure`, `extensibility`, `security-and-access`
   - do not invent freeform narrative ids
   - choose the narrative set before writing stories
   - use narrative observations to rank which optional canonical narratives are actually justified for this repo
   - choose optional narratives from `recommended_narratives`; if two narratives reuse most of the same stories, merge them or replace the weaker one
   - for each chosen narrative, decide which root and child stories are needed to teach it
   - draft candidate root stories and 2-3 concern-focused child stories per root, then merge weak or duplicative children back into the parent
   - child stories should usually come from major flows, state boundaries, dependency boundaries, failure paths, or important design decisions, not from arbitrary file splits
   - let the narrative plan prune unnecessary stories; do not generate stories that no narrative or story tree actually needs

8. Produce `stories/*.yaml` and `narratives.yaml` together from the refined atlas and narrative plan.
   - consult the story schema and narratives schema before first write and again during repair if those artifacts fail validation
   - keep every story grounded in inspected evidence
   - make each story teach one primary thing with one dominant explainer
   - keep supporting material secondary to the main teaching path
   - write `system-overview.description` as a compact architecture synopsis, usually 3-4 sentences, naming the main top-level slices and the primary execution or control path rather than a generic one-liner
   - prefer `Overview` or `Repo Overview` as the human-facing title for `system-overview`
   - write each narrative as a teaching sequence, not just an ordered list: include explicit `teaches` goals and make sure each selected story clearly serves those goals
   - include `throughline` for each narrative: one short paragraph explaining why these stories belong together in this order
   - usually emit 2-4 total narratives for one repo; every extra narrative should earn its place through a distinct audience or cross-cutting teaching purpose
   - keep narrative ids inside the canonical palette defined in the narratives schema; only `system-overview` is always required, and optional narratives should be chosen from the palette only when repo evidence justifies them
   - make the bridge text between adjacent stories explain why the next story follows from the previous one, not just that it comes next

9. Run the local validation loop before you stop.
   - once `atlas.json`, `stories/`, and `narratives.yaml` are written, stop broad repo exploration and move into validation
   - run the validator from `resources.validator_script` against the canonical output directory for this run
   - if validation reports errors or warnings, repair the artifacts in place and rerun the validator
   - continue until the validator reports a clean result
   - use validation naturally as a working tool while you repair; do not wait for the daemon to drive individual repair rounds
   - keep validation scoped to the canonical output directory and do not create sibling run directories

10. Completion means the artifacts are clean.
   - stop only after the validator reports a clean result for the canonical output directory
   - do not stop immediately after first-pass generation if validation is still failing
