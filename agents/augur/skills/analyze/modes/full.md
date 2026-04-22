# Full Mode

Use this guide when the prepared semantic mode is `full`.

Full mode means the semantic pass should rebuild understanding for the whole project from the prepared deterministic evidence, then widen into code where evidence is insufficient.

## Sequence

1. Read `blast.json` in the canonical output directory to confirm `mode=full` and capture any invalidation reasons.
2. Read `startup.json` and `index.json` in the canonical output directory first. Treat `startup.json` as the startup authority and `index.json` as the canonical manifest plus retrieval guide for this run.
3. Read only the small startup-priority fact files first. Do not preload large targeted domains during startup.
4. Transition into repo code once you have an initial architectural picture from startup artifacts.
5. Read `index.json` in the canonical output directory only when you need to discover additional optional domains. Use larger or noisier supporting domains only when they help resolve materially relevant concept candidates, answer review questions, or resolve ambiguity.
6. Perform a mandatory breadth pass in repo code after the first provisional architecture draft.
7. For each provisional top-level component, inspect at least one composition or entry file, one primary behavior or flow file, and one state, dependency, or operations file.
8. Read repo files broadly enough to understand the whole architecture, starting from files surfaced by the prepared facts and then widening across adjacent implementation, not only when blocked.
9. Draft the narrative plan and story tree before writing:
   - choose the required `system-overview` narrative and any justified optional canonical narratives first
   - identify the root and child stories those narratives actually need
   - identify root stories from the top-level components
   - draft 2-3 concern-focused child stories per root where the component really owns multiple concerns
   - prefer child stories grounded in major flow, state, dependency, failure, or design-decision boundaries
   - prune weak or redundant stories before writing files; do not generate stories that no narrative or child decomposition needs
10. Reconcile the model before writing:
   - dependency direction must match runtime reliance
   - state semantics must stay truthful to configurable backends and persistence modes
   - stories and atlas must agree on ownership, flow direction, and system boundaries
   - reject provisional roots anchored mainly in tests, docs, examples, or client-only paths
   - if strong engine, storage, runtime, or coordination slices exist, do not let bootstrap absorb a full top-level root unless it is genuinely the dominant system concern
   - on large repos, make sure at least one top-level root is anchored in deeper runtime or storage internals when deterministic seeds provide one
11. Just before writing or rewriting `atlas.json`, follow the active atlas contract exactly.
   - Emit `metadata` as part of the atlas, not as an optional afterthought.
   - Use deterministic stack evidence to summarize `stack_summary`, `languages`, compact resolved `frameworks`, and `technologies`.
   - Keep component and flow `description` fields terse enough for atlas cards, but add `summary` where readers need a fuller architectural explanation in drilldown views.
12. Just before writing `stories/*.yaml` and `narratives.yaml`, follow the active story and narratives contracts exactly.
    - Give every story one dominant `primary_mode` and one clear teaching thesis in `teaches`.
    - For story flows, make both `trigger` and `outcome` explicit; do not rely on the UI to infer completion from the last step.
    - For story structures, give each visible graph its own concise `summary` and `focus`; do not rely on the story summary alone to explain the graph.
    - Keep one explainer primary and demote evidence, rationale, and extra supporting material to secondary roles.
    - For flow-first stories, make the primary flow explain trigger, major boundaries, outcome, and why it matters to the story.
    - Do not make mixed structure+flow stories the default. For `structure`-first and `flow`-first stories, omit the non-primary explainer unless the concern truly needs both.
    - Prefer `state` or `failure` stories when the story legitimately needs both a structural boundary view and an operating sequence.
    - Treat `system-overview` as the repo overview path.
    - Allowed narrative ids are exactly: `system-overview`, `runtime-paths`, `state-and-data`, `integrations`, `operations-and-failure`, `extensibility`, `security-and-access`.
    - Do not invent freeform narrative ids.
    - Write `system-overview.description` as a compact "how it works" synopsis, not a label: usually 3-4 sentences naming the main slices, dominant flow, and why the sequence teaches the architecture.
    - Prefer `Overview` or `Repo Overview` as the title unless a more specific repo-wide overview title is clearly better.
    - Treat each narrative as a coherent lesson plan with explicit `teaches` goals; the selected stories should collectively deliver those goals rather than act as a loose component inventory.
    - Add `throughline` to explain why the chosen stories form one coherent lesson in that order.
    - Prefer 2-4 total narratives unless the repo has clearly distinct audiences or cross-cutting review paths.
    - Make each adjacent story transition defensible: the per-story bridge text should explain the architectural reason for moving to that next story.
    - Choose optional narratives from `derived/narrative-seeds.json.recommended_narratives` when present. If two narratives reuse most of the same stories, merge them or replace the weaker one.
13. Generate `stories/*.yaml` and `narratives.yaml` together from the refined atlas and the narrative plan.
14. Run `resources.validator_script` against the canonical output directory for this run.
15. If validation reports errors or warnings, fix the artifacts in place and rerun the validator until it is clean.
16. Re-read repo files or supporting fact domains only when needed to resolve ambiguity, verify architecture boundaries, or address concrete validation findings.

## Full-Mode Expectations

- Build a project-wide architectural model.
- Recompose the component hierarchy, components, flows, and narratives across the whole repository.
- Do not leave the atlas fully flat unless the codebase is genuinely flat. Use parent-child component relationships when subsystems contain real nested responsibilities.
- Use deterministic facts first for orientation, then let code inspection drive the main architectural synthesis.
- Do not stay in a long fact-mining loop after startup. Once you have initial hypotheses, confirm or reject them in repo code.
- If `facts/concepts.json` is present, use it as the primary concept trigger only when concept work is actually in play: review candidate concepts, supporting evidence, counter evidence, evidence gaps, and review questions before keeping a concept in `atlas.json`.
- If `frameworks.json` is present, use it as the primary framework trigger: review framework evidence first, then confirm only the frameworks that materially affect component boundaries, flows, or concept activation.
- Resolve concept candidates as accepted, tentative, or rejected from deterministic evidence plus repo code; do not let broad concept vocabulary leak into the atlas before that resolution.
- Resolve framework candidates as accepted, tentative, or rejected from deterministic evidence plus repo code; do not let framework labels steer the atlas just because detection fired.
- Treat unresolved or weakly backed concepts as candidates to drop or downgrade, not as decorative pattern labels.
- If a framework candidate still matters after that first pass, read only the specific framework catalog files instead of broad framework preload.
- If a concept candidate still matters after that first pass, read only the specific concept reference and detector policy or rules for that concept instead of broad concept preload.
- Keep `atlas.json.concepts` compact and grounded: prefer a few high-signal concepts with repo-specific summaries over a long generic pattern list.
- If `derived/story-seeds.json` is present, use it only when story decomposition or root choice is still unclear, not as a startup preload.
- If `derived/narrative-seeds.json` is present, use it only when system-overview or other teaching-path selection is still unclear.
- If `derived/narrative-seeds.json` is present, use its `recommended_narratives` section to decide which optional canonical narrative ids are truly justified for this repo. Prefer higher-ranked optional narratives over weaker ones when you only keep one secondary teaching path. Do not invent freeform narrative ids when the canonical palette already fits.
- If `facts/control-hotspots.json` or `facts/state-access-summary.json` are present, use them only when overview selection, flow choice, or state or dependency boundaries remain unclear.
- If `facts/health-candidates.json` is present, use it only when health, monitoring, gaps, or failure-scenario modeling is underdetermined.
- If `facts/symbols-seed.json` is present, use it when naming or grounding issues remain, not as a default startup read.
- If `facts/state-seeds.json` is present, use it when state naming or state truthfulness is unclear, not as a default startup read.
- Use strong architectural evidence when naming components, responsibilities, and flows.
- Prefer real runtime boundaries, registration paths, cross-component communication, and entrypoints over helper or support files when promoting major components.
- For agent, plugin, hook, or skill-oriented repos, identify the host runtime or chassis first, then model capabilities beneath it.
- Distinguish top-level components from supporting libraries, tests, docs, plugins, and utilities.
- Keep dependency direction faithful to runtime reliance. Serving, embedding, or hosting another artifact does not automatically reverse the dependency edge.
- Keep state entries truthful when backend class or persistence changes by deployment; avoid over-narrow labels when the implementation is configurable.
- A full-mode run should usually read beyond fact-surfaced files. Facts pick the first files; they should not cap the breadth pass.
- Let the schemas and validator enforce field-level contract details; do not improvise alternate formats.
