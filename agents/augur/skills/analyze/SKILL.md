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
   - `$RUN/facts/index.json`
   - the small high-signal fact files named by the runtime
   - treat `$RUN/facts/index.json` as the manifest for deterministic evidence

2. Follow the mode-specific instructions already provided by the runtime.
   - the semantic mode is determined before this skill runs
   - the runtime appends the matching guide from `modes/full.md` or `modes/incremental.md`
   - do not choose your own mode
   - if you are invoked despite `skip`, stop

3. Use facts as guidance, then explore code semantically.
   - use `facts/index.json` to identify likely high-signal domains and files
   - prefer selective reads for large fact domains
   - inspect the actual repo code to understand boundaries, responsibilities, flows, and ambiguities
   - do not treat deterministic facts as final truth

4. Write `$RUN/atlas.json`.
   - read `../../schemas/atlas-schema.md` before writing
   - `components[].depends_on` may reference only component ids
   - outside systems belong in `external_dependencies` or `state`
   - flow node references must resolve to real atlas ids

5. Write `$RUN/stories/*.yaml`.
   - read `../../schemas/story-schema.md` before writing
   - keep every story grounded in inspected evidence

6. Write `$RUN/narratives.yaml`.
   - read `../../schemas/narratives-schema.md` before writing
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
