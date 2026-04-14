# Incremental Mode

Use this guide when the prepared semantic mode is `incremental`.

Incremental mode means the semantic pass should start from the accepted prior semantic output, then update only the changed slice and the architecture it affects. Preserve unchanged conclusions unless current evidence forces revision.

## Sequence

1. Read `$RUN/blast.json` and capture `changed_files`, `base_analysis_dir`, and the affected blast slice.
2. Read the relevant files in `$RUN/facts/`, especially `frameworks.json`, `concept-evidence.json`, and the domain files named by the blast slice.
3. When needed, read the accepted base analysis referenced by `base_analysis_dir`.
4. Read only the repo files needed to verify the changed slice and its architectural impact.
5. Just before writing or rewriting `$RUN/atlas.json`, read `../../schemas/atlas-schema.md` and follow it exactly.
6. Just before writing `stories/*.yaml`, read `../../schemas/story-schema.md` and follow it exactly.
7. Just before writing `narratives.yaml`, read `../../schemas/narratives-schema.md` and follow it exactly.
8. Update outputs under `$RUN`, preserving unaffected structure where possible.

## Incremental-Mode Expectations

- Start narrow: changed files and affected components/flows/state/dependencies/concepts first.
- Reuse unchanged semantic conclusions when the deterministic evidence and code inspection still support them.
- Escalate to broader rereads only when the changed slice proves the boundary is larger than the blast estimate.
- Avoid broad whole-repo exploration unless incremental evidence is clearly insufficient.
