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
   - `$RUN/facts/index.json`
   - the small high-signal fact files listed in `$RUN/facts/startup.json`
   - treat `$RUN/facts/startup.json` and `$RUN/facts/index.json` as the authoritative manifest for which deterministic fact domains exist in this run
   - treat `$RUN/facts/concept-evidence.json` as the canonical source for candidate concepts and run-specific semantic questions
   - inspect `concept-evidence.json` selectively by candidate concept, supporting file, or component; do not read the whole file at startup

2. Follow the mode-specific instructions already provided by the runtime.
   - the semantic mode is determined before this skill runs
   - the runtime appends the matching guide from `modes/full.md` or `modes/incremental.md`
   - do not choose your own mode
   - if you are invoked despite `skip`, stop

3. Use facts as guidance, then explore code semantically.
   - use `facts/index.json` to identify likely high-signal domains and files
   - use `facts/startup.json` and `facts/index.json` to confirm which domains exist before reading any domain-specific fact file
   - start with `hot-files.json` and with repo files named by the prepared fact domains, especially routes, handlers, boundaries, dispatch bindings, and framework source files
   - use `facts/concept-evidence.json` to identify candidate concepts that still need semantic confirmation
   - answer any attached semantic questions before finalizing `atlas.json.concepts`
   - prefer selective reads for large fact domains, and extract only the entries you need before opening repo files
   - for larger domains such as `external-clients.json`, `config.json`, and `import-graph.json`, filter by `component_ids`, `source_files`, or hotspot paths with `python`, `jq`, or `rg` instead of reading the whole file
   - use the available tools you actually have: `Read`, `Edit`, and `Bash`; use `Bash` for `find`, `rg`, `jq`, and `python` queries instead of assuming `Glob` or `Grep` tools exist
   - treat deterministic evidence as ranked hints, not equal signals
   - prefer runtime wiring, service entrypoints, registration code, and cross-component communication over validators, support scripts, bootstrap helpers, or identity docs
   - for agent or plugin systems, identify the host or chassis first, then attach skills, plugins, or capabilities beneath it
   - do not promote a top-level component from one isolated utility file; require corroboration from multiple strong signals
   - inspect the actual repo code to understand boundaries, responsibilities, flows, and ambiguities
   - widen from fact-selected files to adjacent code only when the deterministic evidence leaves a real ambiguity
   - do not treat deterministic facts as final truth

4. Write `$RUN/atlas.json`.
   - read `/app/agents/augur/schemas/atlas-schema.md` before writing
   - `components[].depends_on` may reference only component ids
   - outside systems belong in `external_dependencies` or `state`
   - flow node references must resolve to real atlas ids

5. Write `$RUN/stories/*.yaml`.
   - read `/app/agents/augur/schemas/story-schema.md` before writing
   - keep every story grounded in inspected evidence
   - every structure node and flow node must reference a real atlas id
   - do not invent helper nodes that are not present in `atlas.json`

6. Write `$RUN/narratives.yaml`.
   - read `/app/agents/augur/schemas/narratives-schema.md` before writing
   - include a narrative with exact id `getting-started`
   - narrative story entries must reference real story ids

7. Validate in a loop.
   - run:

```bash
python3 $KORDINATE_HOME/agents/augur/skills/analyze/scripts/validate_output.py $RUN
```

   - if validation fails:
     - read only the schema for the failing artifact
     - fix files in place
     - run the validator again
   - continue until validation passes or the request times out
