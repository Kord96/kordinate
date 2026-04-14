# Narratives Schema

Defines the top-level `narratives.yaml` contract.

`narratives.yaml` is a thin cross-cutting index over the story tree. It pulls stories from anywhere in the tree into specific reading orders for specific audiences.

Narratives are secondary navigation. The story tree is primary.

## Prose Rules

Apply these rules to narrative titles, descriptions, and per-story bridge text:

- keep each description short and directional
- explain why this story is next, not what the document contains
- name the system concern or transition explicitly
- avoid generic filler such as "this narrative explains"

## Narratives YAML Contract

```yaml
version: "1"
narratives:
  - id: "<kebab-case>"
    title: "<Human Readable Title>"
    description: "<one sentence — what the reader achieves>"
    audience: ["<role>"]
    stories:
      - id: "<story-id>"
        description: "<one sentence — why this story is next in the sequence>"
      - id: "<story-id>"
        description: "<one sentence>"
```

## Narrative Design Rules

- 3-8 stories per narrative
- stories can come from any level of the tree
- order stories in teaching order, foundational to dependent
- create narratives for cross-cutting concerns and audience-specific reading paths
- do not create a narrative when tree navigation alone is enough

## Required Narrative

Include a narrative with exact id `getting-started` that provides a teaching-order path covering the main top-level components.

Do not rename this required narrative to variants such as `narrative-getting-started`.

## When To Create A Narrative

- do create one when a concern spans multiple top-level components
- do create one for a specific audience such as onboarding or resilience review
- do not create one for a single-root drilldown already covered by the story tree

## File Layout

```text
$RUN/
  atlas.json
  stories/
    <id>.yaml
  narratives.yaml
```

Story filenames use the story `id`. Parent/child relationships live inside the story files, not the directory structure. `narratives.yaml` is the only narrative index file.
