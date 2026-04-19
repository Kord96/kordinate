---
name: analyze
description: >
  Semantic phase for Augur /analyze. Consumes a prepared run directory, follows
  the runtime-selected mode guidance, writes atlas/stories/narratives, and
  validates until completion or timeout.
---

# Analyze

Semantic phase for Augur `/analyze`.

The deterministic phase is already done. Work from the prepared run directory and produce semantic outputs that validate.

Operational path rules for this runtime:
- the runtime provides one canonical repo root and one canonical output directory for this request
- if `AGENT_ROOT` is present, treat it as the stable base for agent-owned resources
- if `VALIDATOR_SCRIPT` is present, use it directly instead of rediscovering validator paths
- if `CONCEPT_CATALOG_INDEX` or `FRAMEWORK_CATALOG_INDEX` are present, start there for on-demand semantic reads instead of browsing the catalogs
- do not manually reconstruct or shorten the output directory
- do not create sibling run directories with guessed suffixes
- generated artifacts belong in the canonical output directory for this request

## Produce `atlas.json`, `stories/`, and `narratives.yaml` using the prepared semantic inputs in the canonical output directory for this run.

1. Read startup inputs first.
   - `blast.json`
   - `facts/startup.json`
   - `facts/facts-guide.json` when present
   - `facts/index.json`
   - the small high-signal fact files listed in `facts/startup.json`
   - treat `facts/startup.json` and `facts/index.json` as the authoritative manifest for which deterministic fact domains exist in this run

2. Follow the mode-specific instructions already provided by the runtime.
   - the semantic mode is determined before this skill runs
   - the runtime appends the matching guide from `modes/full.md` or `modes/incremental.md`
   - do not choose your own mode
   - if you are invoked despite `skip`, stop

3. Use facts as guidance, then explore code semantically.
   - use `facts/index.json` to identify likely high-signal domains and files
   - use `facts/facts-guide.json` when present as the run-specific interpretation guide for deterministic artifacts in this run
   - treat each domain file in `facts/` as a JSON object with metadata and a top-level `facts` array
   - do not force every file under `facts/` into the domain-file shape; manifest, guide, planning-aid, and derived-structure artifacts may use specialized JSON layouts
   - if you encounter an unfamiliar deterministic artifact shape and `AGENT_ROOT` is present, read `AGENT_ROOT/schemas/facts-schema.md` and `AGENT_ROOT/schemas/facts-catalog.json` before interpreting it
   - use the bundle-mode guidance as concept-resolution methodology, not as a cue to preload a broad semantic concept bundle
   - use the deterministic phase in three tiers:
     - startup orientation: `blast.json`, `facts/startup.json`, `facts/index.json`, and the small high-signal startup fact files
     - early architectural guidance: `hot-files.json` plus the most relevant routing, boundary, handler, dispatch, or framework domains
     - targeted disambiguation only when needed: optional or noisier domains listed in `facts/index.json`, such as `concept-evidence.json`, `import-graph.json`, `config.json`, or similar supporting artifacts
   - after startup orientation, move into repo code before doing more fact reduction
   - if `facts/concept-evidence.json` is present in this run, use it as the primary trigger for concept work: inspect candidate concepts, detector backing, contradictions, and attached semantic questions before letting concepts affect the atlas
   - if `facts/frameworks.json` is present in this run, use it as candidate guidance for framework interpretation: resolve materially relevant frameworks from repo code before letting them change component naming, flow interpretation, or concept activation
   - when a framework remains materially relevant and ambiguous after reviewing `facts/frameworks.json`, start from `FRAMEWORK_CATALOG_INDEX` or `AGENT_ROOT/memory/catalog/frameworks/README.md`, then read only the corresponding framework files you actually need
   - when a concept candidate is materially relevant and remains ambiguous after reviewing `facts/concept-evidence.json`, start from `CONCEPT_CATALOG_INDEX` or `AGENT_ROOT/memory/catalog/concepts/README.md`, then read only the corresponding concept file you actually need
   - when you need the detector's intended threshold, semantic questions, or monitoring expectations for a materially relevant concept candidate and `AGENT_ROOT` is present, read `AGENT_ROOT/detectors/facts/concept-evidence/<concept>/meta.yaml`
   - if `facts/story-seeds.json` is present in this run, use it as an advisory planning aid before writing stories or narratives
   - if `facts/narrative-seeds.json` is present in this run, use it as an advisory ranking aid for system-overview and other teaching paths before finalizing `narratives.yaml`
   - when optional narratives are recommended, prefer the strongest-ranked canonical narrative types instead of keeping a weaker optional path just because it is also allowed
   - if `facts/symbols-seed.json` is present in this run, use it as an advisory exact-name dictionary for high-signal files before writing observations, summaries, or flow steps
   - if `facts/state-seeds.json` is present in this run, use it as an advisory exact-name dictionary for state entries grounded in state or operations files
   - if `facts/health-candidates.json` is present in this run, use it as advisory coverage and contradiction pressure for atlas health: distinguish local failures, boundary failures, and downstream propagation instead of collapsing them into one flat list
   - if `facts/concept-evidence.json` is present, explicitly resolve each materially relevant concept candidate as accepted, tentative, or rejected from repo code and attached semantic questions before finalizing `atlas.json.concepts`
   - if `facts/frameworks.json` is present, explicitly resolve each materially relevant framework as accepted, tentative, or rejected from repo code before using framework-specific semantics to interpret the atlas
   - if present, answer any attached semantic questions before accepting a concept that changes component boundaries, flow interpretation, monitoring expectations, or gaps
   - treat `atlas.json.concepts` as a cross-cutting interpretation layer of resolved concepts: each kept concept should explain how it manifests in this repo and why it matters architecturally, not just name a pattern
   - prefer omitting or downgrading a concept over carrying a broad detector-led label that remains unresolved after code inspection
   - treat deterministic evidence as guidance, not final truth
   - prefer strong architectural evidence when naming components, boundaries, and flows
   - prefer entrypoints, runtime wiring, registration points, and cross-component communication over helper, validator, identity, or support files when promoting major components
   - inspect the actual repo code to understand boundaries, responsibilities, flows, and ambiguities
   - widen from fact-selected files to adjacent code when you need broader context
   - before writing outputs, reconcile the architecture:
     - verify `components[].depends_on` reflects runtime reliance rather than presentation, hosting, or navigational relationships
     - verify state entries stay truthful when backend class or persistence changes by configuration
     - verify the atlas graph, story edges, and narratives tell the same ownership and dependency story
     - verify each claim uses concrete mechanism names from code such as hook names, parser/controller names, stage names, registry names, or option names when those names are available
   - if stories and atlas disagree, fix the model before emitting final artifacts
   - before writing stories, draft candidate root stories and 2-3 concern-focused child stories per root, then merge weak or duplicative children back into the parent
   - child stories should usually come from major flows, state boundaries, dependency boundaries, failure paths, or important design decisions, not from arbitrary file splits
   - prefer one mechanism per claim instead of compressing several stages into one abstract sentence unless the code presents them together
  - when `facts/symbols-seed.json` exposes exact hooks, parsers, commands, registries, options, classes, or stage names for the cited files, prefer those exact names in grounded claims
  - if you emphasize a mechanism name with `**bold**`, make sure it resolves either to a real atlas entity or to a grounded symbol from `facts/symbols-seed.json`
   - when `facts/state-seeds.json` exposes exact structs, enums, maps, config variants, or storage selectors for the cited state files, prefer those exact names in state descriptions and keep one concrete mechanism per claim
   - when writing atlas health, prefer the layered model from `atlas-schema.md`:
     - `health.local` for failures inside one unit
     - `health.integration` for failures at seams with dependencies, stores, or callers
     - `health.propagation` for downstream degraded modes, stale results, blocked work, or wider blast radius
   - use `facts/health-candidates.json` as a ranking and contradiction aid for health coverage, but do not treat it as final truth without code grounding

4. Produce `atlas.json` in the canonical output directory.
   - include `metadata` as part of the normal atlas contract
   - when deterministic facts are present, populate at least:
     - `analysis_mode`
     - `story_ids`
     - `affected_components`
     - `stack_summary`
     - `languages`
     - compact resolved `frameworks`
     - `technologies`
   - keep `metadata.frameworks` limited to materially relevant accepted or tentative frameworks; do not mirror every detected framework fact
   - keep component and flow `description` fields compact, but add `summary` when a click-through reader needs more than a one-line label
   - write component `summary` as the ownership/dependency explanation, not a prose copy of the title
   - write flow `summary` as the operating-path explanation, not a repeat of the trigger

5. Produce `stories/*.yaml` in the canonical output directory.
   - keep every story grounded in inspected evidence
   - make each story teach one primary thing; choose a `primary_mode` and let one explainer dominate
   - write `teaches` as the visible thesis sentence for the story
   - for story flows, make `trigger` and `outcome` explicit instead of leaving completion to be inferred from the final step
   - for story structures, give each visible graph its own concise `summary` and `focus` so the graph can explain itself without borrowing all of the story summary
   - keep low-signal transport or tool metadata secondary; the main flow presentation should foreground what starts the flow, what it does, and what it produces
   - treat observations, anchor evidence, and rationale as supporting inspection material, not as equal-weight primary sections
   - when a story is flow-first, use `flow` consistently in titles and summaries instead of mixing `path` and `flow`
   - do not default to emitting both `structures` and `flows` in the same story
   - for `structure`-first and `flow`-first stories, prefer one primary explainer and omit the other unless it is materially necessary
   - mixed `structure` + `flow` stories should usually be reserved for `state` or `failure` stories where both views are needed together

6. Produce `narratives.yaml` in the canonical output directory.
   - treat `system-overview` as the canonical repo overview narrative used downstream
   - write `system-overview.description` as a compact architecture synopsis, usually 3-4 sentences, naming the main top-level slices and the primary execution or control path rather than a generic one-liner
   - prefer `Overview` or `Repo Overview` as the human-facing title for `system-overview`
   - write each narrative as a teaching sequence, not just an ordered list: include explicit `teaches` goals and make sure each selected story clearly serves those goals
   - include `throughline` for each narrative: one short paragraph explaining why these stories belong together in this order
   - usually emit 2-4 total narratives for one repo; every extra narrative should earn its place through a distinct audience or cross-cutting teaching purpose
   - keep narrative ids inside the canonical palette defined in `narratives-schema.md`; only `system-overview` is always required, and optional narratives should be chosen from the palette only when repo evidence justifies them
   - make the bridge text between adjacent stories explain why the next story follows from the previous one, not just that it comes next
   - use `facts/narrative-seeds.json` when present both to rank which roots, child stories, and flow-bearing stories deserve inclusion and to decide which optional canonical narratives are actually justified for this repo

7. Validate in a loop.
   - run:

```bash
python3 "$VALIDATOR_SCRIPT" "<output_dir>"
```

   - the validator writes `repair-log.json` under the output directory
   - after each validation attempt, read the latest iteration in `repair-log.json` and use it as the authoritative structured repair record
   - use `repair_targets` in the latest iteration to prioritize grouped fixes before chasing individual line-level grounding warnings
   - if validation returns `INVALID` or `NEEDS_REFINEMENT`:
     - use the latest `repair-log.json` iteration to prioritize open or regressed issues before making edits
     - fix files in place
     - run the validator again
   - only stop when the latest `repair-log.json` iteration status is `valid`
   - continue until validation passes cleanly or the request times out

8. Finalization is orchestrator-owned.
   - once the latest `repair-log.json` iteration status is `valid`, stop returning to repo exploration
   - the daemon/workflow will finalize the accepted run and write `meta.json`
