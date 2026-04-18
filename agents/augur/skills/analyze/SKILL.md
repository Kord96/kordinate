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

## Produce `atlas.json`, `stories/`, and `narratives.yaml` using the prepared semantic inputs for this run.

1. Read startup inputs first.
   - `$RUN/blast.json`
   - `$RUN/facts/startup.json`
   - `$RUN/facts/facts-guide.json` when present
   - `$RUN/facts/index.json`
   - the small high-signal fact files listed in `$RUN/facts/startup.json`
   - treat `$RUN/facts/startup.json` and `$RUN/facts/index.json` as the authoritative manifest for which deterministic fact domains exist in this run

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
   - if you encounter an unfamiliar deterministic artifact shape, read `$KORDINATE_HOME/agents/augur/schemas/facts-schema.md` and `$KORDINATE_HOME/agents/augur/schemas/facts-catalog.json` before interpreting it
   - use the bundle-mode guidance as concept-resolution methodology, not as a cue to preload a broad semantic concept bundle
   - use the deterministic phase in three tiers:
     - startup orientation: `blast.json`, `facts/startup.json`, `facts/index.json`, and the small high-signal startup fact files
     - early architectural guidance: `hot-files.json` plus the most relevant routing, boundary, handler, dispatch, or framework domains
     - targeted disambiguation only when needed: optional or noisier domains listed in `facts/index.json`, such as `concept-evidence.json`, `import-graph.json`, `config.json`, or similar supporting artifacts
   - after startup orientation, move into repo code before doing more fact reduction
   - if `facts/concept-evidence.json` is present in this run, use it as the primary trigger for concept work: inspect candidate concepts, detector backing, contradictions, and attached semantic questions before letting concepts affect the atlas
   - if `facts/frameworks.json` is present in this run, use it as candidate guidance for framework interpretation: resolve materially relevant frameworks from repo code before letting them change component naming, flow interpretation, or concept activation
   - when a framework remains materially relevant and ambiguous after reviewing `facts/frameworks.json`, read only the corresponding framework files at `$KORDINATE_HOME/agents/augur/memory/catalog/frameworks/<framework>/framework.md` and `$KORDINATE_HOME/agents/augur/memory/catalog/frameworks/<framework>/semantics.yaml`
   - when a concept candidate is materially relevant and remains ambiguous after reviewing `facts/concept-evidence.json`, read only the corresponding concept file at `$KORDINATE_HOME/agents/augur/memory/catalog/concepts/<concept>.md`
   - when you need the detector's intended threshold, semantic questions, or monitoring expectations for a materially relevant concept candidate, read `$KORDINATE_HOME/agents/augur/detectors/facts/concept-evidence/<concept>/meta.yaml`
   - if `facts/story-seeds.json` is present in this run, use it as an advisory planning aid before writing stories or narratives
   - if `facts/narrative-seeds.json` is present in this run, use it as an advisory ranking aid for getting-started and other teaching paths before finalizing `narratives.yaml`
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
   - when `facts/state-seeds.json` exposes exact structs, enums, maps, config variants, or storage selectors for the cited state files, prefer those exact names in state descriptions and keep one concrete mechanism per claim
   - when writing atlas health, prefer the layered model from `atlas-schema.md`:
     - `health.local` for failures inside one unit
     - `health.integration` for failures at seams with dependencies, stores, or callers
     - `health.propagation` for downstream degraded modes, stale results, blocked work, or wider blast radius
   - use `facts/health-candidates.json` as a ranking and contradiction aid for health coverage, but do not treat it as final truth without code grounding

4. Produce `$RUN/atlas.json`.
   - read `$KORDINATE_HOME/agents/augur/schemas/atlas-schema.md` before writing
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

5. Produce `$RUN/stories/*.yaml`.
   - read `$KORDINATE_HOME/agents/augur/schemas/story-schema.md` before writing
   - keep every story grounded in inspected evidence

6. Produce `$RUN/narratives.yaml`.
   - read `$KORDINATE_HOME/agents/augur/schemas/narratives-schema.md` before writing
   - treat `getting-started` as the canonical repo overview narrative used downstream; the id is historical, but the content should explain the repo's architecture rather than read like a startup guide
   - write `getting-started.description` as a compact architecture synopsis, usually 3-4 sentences, naming the main top-level slices and the primary execution or control path rather than a generic one-liner
   - prefer `Overview` or `Repo Overview` as the human-facing title for `getting-started`
   - write each narrative as a teaching sequence, not just an ordered list: include explicit `teaches` goals and make sure each selected story clearly serves those goals
   - include `throughline` for each narrative: one short paragraph explaining why these stories belong together in this order
   - usually emit 2-4 total narratives for one repo; every extra narrative should earn its place through a distinct audience or cross-cutting teaching purpose
   - make the bridge text between adjacent stories explain why the next story follows from the previous one, not just that it comes next
   - use `facts/narrative-seeds.json` when present to rank which roots, child stories, and flow-bearing stories deserve inclusion, especially for `getting-started`

7. Validate in a loop.
   - run:

```bash
python3 $KORDINATE_HOME/agents/augur/skills/analyze/scripts/validate_output.py $RUN
```

   - the validator writes `$RUN/repair-log.json`
   - after each validation attempt, read the latest iteration in `repair-log.json` and use it as the authoritative structured repair record
   - use `repair_targets` in the latest iteration to prioritize grouped fixes before chasing individual line-level grounding warnings
   - if validation returns `INVALID` or `NEEDS_REFINEMENT`:
     - read only the schema for the failing artifact
     - read `$KORDINATE_HOME/agents/augur/schemas/repair-log-schema.md` if you need the repair-log contract
     - use the latest `repair-log.json` iteration to prioritize open or regressed issues before making edits
     - fix files in place
     - run the validator again
   - only stop when the latest `repair-log.json` iteration status is `valid`
   - continue until validation passes cleanly or the request times out

8. Finalize the accepted run.
   - once the latest `repair-log.json` iteration status is `valid`, write the canonical accepted-run metadata by running:

```bash
python3 $KORDINATE_HOME/agents/augur/scripts/finalize_analysis.py $RUN
```

   - this must produce `$RUN/meta.json` and update the project-level latest pointers for accepted analyses
   - after finalizing, rerun:

```bash
python3 $KORDINATE_HOME/agents/augur/skills/analyze/scripts/validate_output.py $RUN
```

   - only finish when:
     - the latest `repair-log.json` iteration status is still `valid`
     - and `$RUN/meta.json` exists and validates cleanly
