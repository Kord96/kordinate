# Narratives Schema

Defines the top-level `narratives.yaml` contract.

`narratives.yaml` is a thin cross-cutting index over the story tree. It pulls stories from anywhere in the tree into specific reading orders for specific audiences.

Narratives are secondary navigation. The story tree is primary.

## Prose Rules

Apply these rules to narrative titles, descriptions, and per-story bridge text:

- keep each narrative description as a short overview paragraph, usually 2-4 sentences
- keep each per-story bridge description short and directional
- explain why this story is next, not what the document contains
- name the system concern or transition explicitly
- avoid generic filler such as "this narrative explains"
- use the narrative description as a compact architectural synopsis, not just a label

## Narratives YAML Contract

```yaml
version: "1"
narratives:
  - id: "<kebab-case>"
    title: "<Human Readable Title>"
    description: "<2-4 short sentences — the architecture this journey walks through>"
    teaches:
      - "<one concrete thing the reader should understand by the end>"
      - "<another concrete learning outcome>"
    throughline: "<one short paragraph — why these stories belong together in this order>"
    audience: ["<role>"]
    stories:
      - id: "<story-id>"
        description: "<one sentence — why this story is next in the sequence>"
      - id: "<story-id>"
        description: "<one sentence>"
```

## Narrative Design Rules

- usually emit 2-4 total narratives for one repo
- 3-8 stories per narrative
- 2-4 teaching goals in `teaches`
- include `throughline` for every narrative
- stories can come from any level of the tree
- order stories in teaching order, foundational to dependent
- make each narrative teach one dominant concern or audience path; if the goals pull in unrelated directions, split the narrative
- create narratives for cross-cutting concerns and audience-specific reading paths
- do not create a narrative when tree navigation alone is enough
- when child stories carry the real explanatory detail, prefer them over repeating only root stories
- for cross-cutting narratives, mix root and child stories when that yields a clearer teaching sequence than repeating roots only
- prefer the smallest story that teaches the next architectural step clearly; avoid repeating a root story when a child story is the real explanation
- each per-story bridge description should justify the transition from the previous story into the next concern; do not use filler such as "next" or "then" without naming the reason
- use `derived/narrative-seeds.json` when present as a ranking aid for which roots, child stories, and flow-bearing stories deserve inclusion, especially in `system-overview`
- for optional narratives, prefer the highest-ranked canonical narratives from `recommended_narratives`; do not keep a weaker optional narrative while omitting a clearly stronger one unless repo evidence in the final atlas justifies that tradeoff
- narratives should be meaningfully distinct from each other; do not emit two narratives that differ by only one swapped story or a light rewording of the same teaching path
- if two narratives reuse most of the same stories, they should also have clearly different teaching goals and throughlines; otherwise merge them or replace the weaker one

## Canonical Narrative Palette

Narratives should come from this constrained palette unless the repo has an unusually strong reason to justify a different reading path:

- `system-overview`
  - required
  - teaches what the system does and how it does it
- `runtime-paths`
  - deeper execution, control, scheduling, or event paths
- `state-and-data`
  - stores, persistence, caches, data movement, and state boundaries
- `integrations`
  - external systems, protocols, dependency boundaries, and handoff seams
- `operations-and-failure`
  - health, degraded modes, blast radius, and observability
- `extensibility`
  - plugins, hooks, customization seams, registries, or framework extension surfaces
- `security-and-access`
  - trust boundaries, authn, authz, identity, token/session handling, and privileged control surfaces

Prefer the palette name that best matches the real teaching purpose. Do not invent custom ids when one of the canonical narratives already fits.

## Required Narrative

Include a narrative with exact id `system-overview` that serves as the default repository overview.

`system-overview` should usually be titled `Overview` or `Repo Overview` unless a more specific repo-wide overview title is clearly better.

`system-overview` should normally move from one orienting root into the most explanatory child stories and defining cross-component flows before returning to later roots. Do not keep it root-only when child stories carry the real architecture.

`system-overview.description` is the canonical "how it works" overview used by downstream readers. It should be a compact synopsis of the repo's architectural shape, usually 3-4 sentences, and should name the dominant top-level components, major execution path, or cross-cutting subsystem boundaries explicitly.

`system-overview.teaches` should name the core architectural lessons that the included stories collectively deliver about the repository. The stories chosen for the narrative should clearly serve those goals rather than acting as a loose inventory.

`throughline` should explain why the chosen stories form one coherent overview in this order. It is not another summary; it is the teaching arc.

`system-overview` should explicitly answer:
- what the repository or system does
- how its main architecture achieves that outcome

Use component hierarchy, defining flows, important state boundaries, and major tensions as selection signals for `system-overview`, not as content to dump. Prefer the few stories that best establish repo shape and operating model over broader component coverage.

Do not write `system-overview` in a procedural "how to begin using the repo" tone. It should describe how the repo is organized and how its main architecture operates.

Do not rename this required narrative to variants such as `narrative-system-overview`.

## When To Create A Narrative

- do create one when a concern spans multiple top-level components
- do create one for a specific audience such as onboarding or resilience review
- do not create one for a single-root drilldown already covered by the story tree
- do use a canonical palette id when the repo strongly supports it through deterministic evidence or a clear cross-component teaching need
- do not emit optional palette narratives just to fill slots; each extra narrative should have a distinct concern and evidence-backed reason to exist

## File Layout

```text
$RUN/
  atlas.json
  stories/
    <id>.yaml
  narratives.yaml
```

Story filenames use the story `id`. Parent/child relationships live inside the story files, not the directory structure. `narratives.yaml` is the only narrative index file.
