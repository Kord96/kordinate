# Incremental Mode

Use this guide when the prepared semantic mode is `incremental`.

Incremental mode means the semantic pass should start from the accepted prior semantic output, then update only the changed slice and the architecture it affects. Preserve unchanged conclusions unless current evidence forces revision.

## Sequence

1. Read `$RUN/blast.json` and capture `changed_files`, `base_analysis_dir`, and the affected blast slice.
2. Read `$RUN/facts/startup.json`, then the relevant files listed in `$RUN/facts/index.json`, especially `frameworks.json` and the domain files named by the blast slice. Use `concept-evidence.json` only if it is present in this run and relevant to the changed slice.
3. Form a provisional view of how the changed slice affects the existing architecture.
4. If `concept-evidence.json` is present and carries semantic questions for affected concept candidates, use them to resolve those candidates as accepted, tentative, or rejected before finalizing `atlas.json.concepts`.
5. If `frameworks.json` is present and framework interpretation is relevant to the changed slice, resolve those framework candidates before letting framework semantics change the updated atlas or stories.
6. When needed, read the accepted base analysis referenced by `base_analysis_dir`.
7. Read only the repo files needed to verify the changed slice and its architectural impact.
8. Just before writing or rewriting `$RUN/atlas.json`, read `$KORDINATE_HOME/agents/augur/schemas/atlas-schema.md` and follow it exactly.
9. Just before writing `stories/*.yaml`, read `$KORDINATE_HOME/agents/augur/schemas/story-schema.md` and follow it exactly.
   - Preserve or sharpen the story's dominant `primary_mode`; avoid turning one story into several equal-weight explainers.
   - Keep `teaches` as the story thesis and treat evidence/rationale as supporting inspection material.
   - When updating a flow-first story, keep `flow` terminology consistent instead of mixing `path` and `flow`.
   - Avoid casually introducing both `structures` and `flows` into the same story; if the story is `structure`-first or `flow`-first, the non-primary explainer should usually stay absent.
10. Just before writing `narratives.yaml`, read `$KORDINATE_HOME/agents/augur/schemas/narratives-schema.md` and follow it exactly.
11. Update outputs under `$RUN`, preserving unaffected structure where possible.

## Incremental-Mode Expectations

- Start narrow: changed files and affected components/flows/state/dependencies/concepts first.
- Reuse unchanged semantic conclusions when the deterministic evidence and code inspection still support them.
- Escalate to broader rereads only when the changed slice proves the boundary is larger than the blast estimate.
- Avoid broad whole-repo exploration unless incremental evidence is clearly insufficient.
- Preserve existing top-level component boundaries unless new strong evidence disproves them.
- When changed files belong to a capability or plugin under an existing host, update that capability story first instead of promoting a new top-level component.
- Prefer runtime wiring, registrations, entrypoints, and inter-component communication over validators, helpers, identity docs, or support scripts when deciding whether architecture has materially changed.
- Treat concept-evidence as candidate guidance, not as a final concept list. Only accepted concepts should materially change atlas concepts, monitoring expectations, or gaps.
- Treat framework evidence as candidate guidance, not as a final framework list. Only accepted frameworks should materially change atlas naming, flow interpretation, or framework-driven concept activation.
- If `narrative-seeds.json` is present, use it to challenge whether the changed slice should alter the onboarding path or another teaching path; prefer swapping or pruning stories over expanding the narrative.
- If `control-hotspots.json` or `state-access-summary.json` are present and touched by the changed slice, use them as evidence for operating-model or boundary-story selection rather than restating them directly.
- If a changed-slice framework candidate remains ambiguous, read only the specific framework catalog files for that framework instead of widening framework context broadly.
- If a changed-slice concept candidate remains ambiguous, read only the specific concept file and detector `meta.yaml` for that concept instead of widening concept context broadly.
- The available tools in this runtime are `Read`, `Edit`, and `Bash`. Use `Bash` with `find`, `rg`, `jq`, or `python` for discovery or filtering instead of assuming `Glob` or `Grep` tools exist.
