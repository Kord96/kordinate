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

2. Follow the mode-specific instructions already provided by the runtime.
   - the semantic mode is determined before this skill runs
   - the runtime appends the matching guide from `modes/full.md` or `modes/incremental.md`
   - do not choose your own mode
   - if you are invoked despite `skip`, stop

3. Use facts as guidance, then explore code semantically.
   - use `facts/index.json` to identify likely high-signal domains and files
   - treat each domain file in `facts/` as a JSON object with metadata and a top-level `facts` array
   - start with `hot-files.json` and with repo files named by the prepared fact domains
   - use `facts/concept-evidence.json` to identify candidate concepts that still need semantic confirmation
   - answer any attached semantic questions before finalizing `atlas.json.concepts`
   - treat deterministic evidence as guidance, not final truth
   - prefer strong architectural evidence when naming components, boundaries, and flows
   - inspect the actual repo code to understand boundaries, responsibilities, flows, and ambiguities
   - widen from fact-selected files to adjacent code when you need broader context

4. Produce `$RUN/atlas.json`.
   - read `/app/agents/augur/schemas/atlas-schema.md` before writing

5. Produce `$RUN/stories/*.yaml`.
   - read `/app/agents/augur/schemas/story-schema.md` before writing
   - keep every story grounded in inspected evidence

6. Produce `$RUN/narratives.yaml`.
   - read `/app/agents/augur/schemas/narratives-schema.md` before writing

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
