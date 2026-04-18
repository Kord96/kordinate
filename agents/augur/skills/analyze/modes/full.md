# Full Mode

Use this guide when the prepared semantic mode is `full`.

Full mode means the semantic pass should rebuild understanding for the whole project from the prepared deterministic evidence, then widen into code where evidence is insufficient.

## Sequence

1. Read `$RUN/blast.json` to confirm `mode=full` and capture any invalidation reasons.
2. Read `$RUN/facts/startup.json` and `$RUN/facts/index.json` and use them as the authoritative manifest for available domains, counts, detector coverage, and failed domains.
3. Read `hot-files.json` and the most relevant startup fact files as the early guidance layer after the prepared startup facts.
4. Transition into repo code once you have an initial architectural picture from startup artifacts.
5. Use larger or noisier supporting domains only when they are present in `facts/index.json` and help resolve materially relevant concept candidates, answer semantic questions, or resolve ambiguity.
6. Perform a mandatory breadth pass in repo code after the first provisional architecture draft.
7. For each provisional top-level component, inspect at least one composition or entry file, one primary behavior or flow file, and one state, dependency, or operations file.
8. Read repo files broadly enough to understand the whole architecture, starting from files surfaced by the prepared facts and then widening across adjacent implementation, not only when blocked.
9. Draft the story tree before writing:
   - identify root stories from the top-level components
   - draft 2-3 concern-focused child stories per root where the component really owns multiple concerns
   - prefer child stories grounded in major flow, state, dependency, failure, or design-decision boundaries
10. Reconcile the model before writing:
   - dependency direction must match runtime reliance
   - state semantics must stay truthful to configurable backends and persistence modes
   - stories and atlas must agree on ownership, flow direction, and system boundaries
   - reject provisional roots anchored mainly in tests, docs, examples, or client-only paths
   - if strong engine, storage, runtime, or coordination slices exist, do not let bootstrap absorb a full top-level root unless it is genuinely the dominant system concern
   - on large repos, make sure at least one top-level root is anchored in deeper runtime or storage internals when deterministic seeds provide one
11. Just before writing or rewriting `$RUN/atlas.json`, read `$KORDINATE_HOME/agents/augur/schemas/atlas-schema.md` and follow it exactly.
   - Emit `metadata` as part of the atlas, not as an optional afterthought.
   - Use deterministic stack evidence to summarize `stack_summary`, `languages`, compact resolved `frameworks`, and `technologies`.
12. Just before writing `stories/*.yaml`, read `$KORDINATE_HOME/agents/augur/schemas/story-schema.md` and follow it exactly.
13. Just before writing `narratives.yaml`, read `$KORDINATE_HOME/agents/augur/schemas/narratives-schema.md` and follow it exactly.
    - Write `getting-started.description` as a compact "how it works" synopsis, not a label: usually 3-4 sentences naming the main slices, dominant flow, and why the sequence teaches the architecture.
    - Treat each narrative as a coherent lesson plan with explicit `teaches` goals; the selected stories should collectively deliver those goals rather than act as a loose component inventory.
    - Add `throughline` to explain why the chosen stories form one coherent lesson in that order.
    - Prefer 2-4 total narratives unless the repo has clearly distinct audiences or cross-cutting review paths.
    - Make each adjacent story transition defensible: the per-story bridge text should explain the architectural reason for moving to that next story.
14. Generate `stories/*.yaml` and `narratives.yaml` from the refined atlas.
15. Re-read repo files or supporting fact domains only when needed to resolve ambiguity, verify architecture boundaries, or address concrete validation findings.

## Full-Mode Expectations

- Build a project-wide architectural model.
- Recompose the component hierarchy, components, flows, and narratives across the whole repository.
- Do not leave the atlas fully flat unless the codebase is genuinely flat. Use parent-child component relationships when subsystems contain real nested responsibilities.
- Use deterministic facts first for orientation, then let code inspection drive the main architectural synthesis.
- Do not stay in a long fact-mining loop after startup. Once you have initial hypotheses, confirm or reject them in repo code.
- If `concept-evidence.json` is present, use it as the primary concept trigger: review candidate concepts, detector backing, contradictions, and semantic questions before keeping a concept in `atlas.json`.
- If `frameworks.json` is present, use it as the primary framework trigger: review framework evidence first, then confirm only the frameworks that materially affect component boundaries, flows, or concept activation.
- Resolve concept candidates as accepted, tentative, or rejected from deterministic evidence plus repo code; do not let broad concept vocabulary leak into the atlas before that resolution.
- Resolve framework candidates as accepted, tentative, or rejected from deterministic evidence plus repo code; do not let framework labels steer the atlas just because detection fired.
- Treat unresolved or weakly backed concepts as candidates to drop or downgrade, not as decorative pattern labels.
- If a framework candidate still matters after that first pass, read only the specific framework catalog files instead of broad framework preload.
- If a concept candidate still matters after that first pass, read only the specific concept file and detector `meta.yaml` for that concept instead of broad concept preload.
- Keep `atlas.json.concepts` compact and grounded: prefer a few high-signal concepts with repo-specific summaries over a long generic pattern list.
- If `story-seeds.json` is present, use it as an advisory checklist for child-story decomposition, not as a replacement for actual architectural judgment.
- If `narrative-seeds.json` is present, use it as an advisory ranking layer for `getting-started` and other teaching paths: prefer the smallest set of stories that teaches system shape plus the operating model.
- If `control-hotspots.json` or `state-access-summary.json` are present, use them as evidence for which flows or state/dependency boundaries deserve to appear in onboarding narratives, not as content to dump literally.
- If `symbols-seed.json` is present, use it as an advisory exact-name inventory for high-signal files before finalizing observations, summaries, and flow steps.
- If `state-seeds.json` is present, use it as an advisory exact-name inventory for state entries grounded in state or operations files.
- Use strong architectural evidence when naming components, responsibilities, and flows.
- Prefer real runtime boundaries, registration paths, cross-component communication, and entrypoints over helper or support files when promoting major components.
- For agent, plugin, hook, or skill-oriented repos, identify the host runtime or chassis first, then model capabilities beneath it.
- Distinguish top-level components from supporting libraries, tests, docs, plugins, and utilities.
- Keep dependency direction faithful to runtime reliance. Serving, embedding, or hosting another artifact does not automatically reverse the dependency edge.
- Keep state entries truthful when backend class or persistence changes by deployment; avoid over-narrow labels when the implementation is configurable.
- A full-mode run should usually read beyond fact-surfaced files. Facts pick the first files; they should not cap the breadth pass.
- Let the schemas and validator enforce field-level contract details; do not improvise alternate formats.
