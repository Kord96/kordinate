# Full Mode

Use this guide when the prepared semantic mode is `full`.

Full mode means the semantic pass should rebuild understanding for the whole project from the prepared deterministic evidence, then widen into code where evidence is insufficient.

## Sequence

1. Read `$RUN/blast.json` to confirm `mode=full` and capture any invalidation reasons.
2. Read `$RUN/facts/index.json` and use it as the canonical manifest for available domains, counts, detector coverage, and failed domains.
3. Read only the small, high-signal fact files first, especially `frameworks.json`, `boundaries.json`, `routes.json`, and `dispatch-bindings.json`.
4. Read repo files only as needed to resolve ambiguity or verify architecture boundaries.
5. Just before writing or rewriting `$RUN/atlas.json`, read `../../schemas/atlas-schema.md` and follow it exactly.
6. Just before writing `stories/*.yaml`, read `../../schemas/story-schema.md` and follow it exactly.
7. Just before writing `narratives.yaml`, read `../../schemas/narratives-schema.md` and follow it exactly.
8. Generate `stories/*.yaml` and `narratives.yaml` from the refined atlas.
9. Re-read repo files only when needed to resolve ambiguity, verify architecture boundaries, or address concrete validation findings.

## Full-Mode Expectations

- Build a project-wide architectural model.
- Recompose groups, components, flows, and narratives across the whole repository when the evidence suggests it.
- Use deterministic facts first, then code inspection.
- Keep schema families distinct:
  - `atlas.json` uses atlas-style fields such as `name` and `description`
  - `stories/*.yaml` use story-schema fields such as `id`, `title`, and `summary`
  - `narratives.yaml` uses narrative-schema fields such as `id`, `title`, and `description`
- The required onboarding narrative must use the exact id `getting-started`.
- In `atlas.json`, `components[].depends_on` may reference only other component ids.
- Put Kafka, external APIs, databases, filesystems, and other outside systems in `external_dependencies` or `state`, not in `components[].depends_on`.
- In flow steps, `component` and `to` must reference real atlas node ids. Do not use placeholders such as `filesystem`; represent persistence through `state` entries instead.
- If a component interacts with Kafka, keep that relationship in `external_dependencies`, `events`, and flow steps. Do not put `kafka` in `components[].depends_on`.
- If you create multiple narratives, one of them must still be exactly `id: getting-started`, and every narrative must list 3-8 real story ids.
- Treat `facts/index.json` as the control surface. Do not read every fact domain wholesale before you know which domains matter.
- For larger domains such as `concept-evidence.json`, `import-graph.json`, `config.json`, or `external-clients.json`, inspect them selectively with `jq`, `python`, `rg`, or targeted reads instead of full-file slurps.
- Avoid spending early turns rediscovering runtime setup or filesystem layout.
- Do not read repo metadata files such as `README.md`, `CLAUDE.md`, `KORD.md`, `KORD.json`, or `agents/*/IDENTITY.md` during semantic startup. The runtime context and prepared deterministic artifacts already provide the operating contract.
- Do not inspect agent-definition files to understand your own role. Treat the runtime context as authoritative.
