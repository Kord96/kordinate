# Full Mode

Use this guide when the prepared semantic mode is `full`.

Full mode means the semantic pass should rebuild understanding for the whole project from the prepared deterministic evidence, then widen into code where evidence is insufficient.

## Sequence

1. Read `$RUN/blast.json` to confirm `mode=full` and capture any invalidation reasons.
2. Read `$RUN/facts/index.json` and use it as the canonical manifest for available domains, counts, detector coverage, and failed domains.
3. Read `hot-files.json` and use it to rank likely code hotspots before widening into repo code.
4. Inspect `concept-evidence.json` early, but only through filtered queries for the candidate entries and semantic questions that matter for the current architectural picture.
5. Read only the small, high-signal fact files first, especially `frameworks.json`, `boundaries.json`, `routes.json`, and `dispatch-bindings.json`.
6. Read repo files only as needed to resolve ambiguity or verify architecture boundaries, starting from files named by the prepared fact domains and `hot-files.json`.
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
- Use `concept-evidence.json` to drive concept confirmation work. Query only the entries tied to the components, flows, or hotspot files you are actively resolving. If a candidate carries semantic questions, answer them before finalizing `atlas.json.concepts`.
- Use `hot-files.json` and the `source_files` fields inside facts as the default bridge from deterministic evidence into semantic code reading.
- Keep schema families distinct:
  - `atlas.json` uses atlas-style fields such as `name` and `description`
  - `stories/*.yaml` use story-schema fields such as `id`, `title`, and `summary`
  - `narratives.yaml` uses narrative-schema fields such as `id`, `title`, and `description`
- Do not emit legacy atlas sections such as `groups`, `stack`, `debt`, `api_surface`, `security`, or `developer_experience`.
- The required onboarding narrative must use the exact id `getting-started`.
- In `atlas.json`, `components[].depends_on` may reference only other component ids.
- Put Kafka, external APIs, databases, filesystems, and other outside systems in `external_dependencies` or `state`, not in `components[].depends_on`.
- In flow steps, `component` and `to` must reference real atlas node ids. Do not use placeholders such as `filesystem`; represent persistence through `state` entries instead.
- If a component interacts with Kafka, keep that relationship in `external_dependencies`, `events`, and flow steps. Do not put `kafka` in `components[].depends_on`.
- If you create multiple narratives, one of them must still be exactly `id: getting-started`, and every narrative must list 3-8 real story ids.
- Treat `facts/index.json` as the control surface. Do not read every fact domain wholesale before you know which domains matter.
- For larger domains such as `concept-evidence.json`, `import-graph.json`, `config.json`, or `external-clients.json`, inspect them selectively with `jq`, `python`, `rg`, or targeted reads instead of full-file slurps.
- Do not read `concept-evidence.json`, `external-clients.json`, `config.json`, or `import-graph.json` in full during early orientation. Filter them by relevant `component_ids`, `source_files`, hotspot paths, or concept ids first.
- Until you have written an initial `atlas.json`, never full-read `concept-evidence.json`, `external-clients.json`, `config.json`, or `import-graph.json`. Query only the entries tied to the components, flows, hotspot files, or concept candidates you are actively resolving.
- Avoid spending early turns rediscovering runtime setup or filesystem layout.
- Do not start by listing the repo root or browsing top-level directories to “see what is there”. Start from prepared facts and only follow concrete paths they surface.
- Prefer architecture entrypoints and hotspots surfaced by facts, such as route handlers, dispatch targets, boundary files, framework bootstrap code, and hot files.
- Do not read repo metadata files such as `README.md`, `CLAUDE.md`, `KORD.md`, `KORD.json`, or `agents/*/IDENTITY.md` during semantic startup. The runtime context and prepared deterministic artifacts already provide the operating contract.
- Do not inspect agent-definition files to understand your own role. Treat the runtime context as authoritative.
