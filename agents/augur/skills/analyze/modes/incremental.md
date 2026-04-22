# Incremental Mode

Use this guide when the prepared semantic mode is `incremental`.

Incremental mode means the semantic pass should start from the accepted prior semantic output, then update only the changed slice and the architecture it affects. Preserve unchanged conclusions unless current evidence forces revision.

## Sequence

1. Read `blast.json` in the canonical output directory and capture `changed_files`, `base_analysis_dir`, and the affected blast slice.
2. Read `facts/startup.json` and `facts/index.json` in the canonical output directory, then only the small startup-priority files listed in `startup.json`. Treat `index.json` as the canonical manifest plus retrieval guide for this run.
3. Form a provisional view of how the changed slice affects the existing architecture.
4. If `concept-evidence.json` is present and carries review questions for affected concept candidates, use them to resolve those candidates as accepted, tentative, or rejected before finalizing `atlas.json.concepts`.
5. If `frameworks.json` is present and framework interpretation is relevant to the changed slice, resolve those framework candidates before letting framework semantics change the updated atlas or stories.
6. When needed, read the accepted base analysis referenced by `base_analysis_dir`.
7. Read only the repo files needed to verify the changed slice and its architectural impact.
8. Just before writing or rewriting `atlas.json`, follow the active atlas contract exactly.
9. Re-plan the affected narratives and stories together before writing.
   - start from the changed slice and decide which existing narratives or stories actually need edits
   - if the changed slice introduces a new teaching path, choose the canonical narrative id before writing new stories
   - avoid generating new stories unless the changed architecture really needs them
10. Just before writing `stories/*.yaml` and `narratives.yaml`, follow the active story and narratives contracts exactly.
   - Preserve or sharpen the story's dominant `primary_mode`; avoid turning one story into several equal-weight explainers.
   - Keep `teaches` as the story thesis and treat evidence/rationale as supporting inspection material.
   - When editing or adding story flows, keep `trigger` and `outcome` explicit instead of relying on final-step inference.
   - When editing or adding story structures, give each visible graph its own concise `summary` and `focus` instead of relying on the story summary alone.
   - When updating a flow-first story, keep `flow` terminology consistent instead of mixing `path` and `flow`.
   - Avoid casually introducing both `structures` and `flows` into the same story; if the story is `structure`-first or `flow`-first, the non-primary explainer should usually stay absent.
   - Keep narrative ids inside the canonical palette only: `system-overview`, `runtime-paths`, `state-and-data`, `integrations`, `operations-and-failure`, `extensibility`, `security-and-access`.
   - Use `facts/narrative-seeds.json` when present to choose optional canonical narratives and to prune overlapping teaching paths.
11. Update stories and `narratives.yaml` in the canonical output directory, preserving unaffected structure where possible.
12. Run `resources.validator_script` against the canonical output directory for this run.
13. If validation reports errors or warnings, repair the changed artifacts in place and rerun the validator until it is clean.

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
- If `narrative-seeds.json` is present, use it only when the changed slice may alter onboarding or another teaching path; prefer swapping or pruning stories over expanding the narrative.
- If `control-hotspots.json` or `state-access-summary.json` are present and touched by the changed slice, use them only when operating-model or boundary-story selection remains unclear.
- If a changed-slice framework candidate remains ambiguous, read only the specific framework catalog files for that framework instead of widening framework context broadly.
- If a changed-slice concept candidate remains ambiguous, read only the specific concept file and detector `meta.yaml` for that concept instead of widening concept context broadly.
- Follow the runtime's advertised tool schema instead of assuming specific tool names from other runtimes.
