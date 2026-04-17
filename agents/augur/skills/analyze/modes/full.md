# Full Mode

Use this guide when the prepared semantic mode is `full`.

Full mode means the semantic pass should rebuild understanding for the whole project from the prepared deterministic evidence, then widen into code where evidence is insufficient.

## Sequence

1. Read `$RUN/blast.json` to confirm `mode=full` and capture any invalidation reasons.
2. Read `$RUN/facts/startup.json` and `$RUN/facts/index.json` and use them as the authoritative manifest for available domains, counts, detector coverage, and failed domains.
3. Read `hot-files.json` as a secondary hint layer after the prepared startup facts.
4. Read `concept-evidence.json` early enough to understand the candidate concepts and semantic questions that matter for the current architectural picture.
5. Read the most relevant high-signal fact files first.
6. Read repo files broadly enough to understand the whole architecture, starting from files surfaced by the prepared facts and then widening as needed.
7. Just before writing or rewriting `$RUN/atlas.json`, read `/app/agents/augur/schemas/atlas-schema.md` and follow it exactly.
8. Just before writing `stories/*.yaml`, read `/app/agents/augur/schemas/story-schema.md` and follow it exactly.
9. Just before writing `narratives.yaml`, read `/app/agents/augur/schemas/narratives-schema.md` and follow it exactly.
10. Generate `stories/*.yaml` and `narratives.yaml` from the refined atlas.
11. Re-read repo files only when needed to resolve ambiguity, verify architecture boundaries, or address concrete validation findings.

## Full-Mode Expectations

- Build a project-wide architectural model.
- Recompose the component hierarchy, components, flows, and narratives across the whole repository.
- Do not leave the atlas fully flat unless the codebase is genuinely flat. Use parent-child component relationships when subsystems contain real nested responsibilities.
- Use deterministic facts first, then code inspection.
- Use `concept-evidence.json` to drive concept confirmation work. If a candidate carries semantic questions, answer them before finalizing `atlas.json.concepts`.
- Use strong architectural evidence when naming components, responsibilities, and flows.
- Prefer real runtime boundaries, registration paths, cross-component communication, and entrypoints over helper or support files when promoting major components.
- For agent, plugin, hook, or skill-oriented repos, identify the host runtime or chassis first, then model capabilities beneath it.
- Distinguish top-level components from supporting libraries, tests, docs, plugins, and utilities.
- Let the schemas and validator enforce field-level contract details; do not improvise alternate formats.
