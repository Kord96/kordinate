# Bundle Mode: Evidence Driven

Use this guidance for Augur analyze runs.

Evidence-driven mode means:

- keep only high-level semantic methodology resident by default
- let deterministic evidence surface candidate concepts
- resolve those candidates through repo inspection and semantic questions before they materially affect outputs

## Expectations

- Start from prepared facts, startup artifacts, and repo code, not from a broad resident concept bundle.
- Treat `facts/concept-evidence.json` as the main trigger for concept work.
- For each concept candidate that could materially affect the atlas, stories, monitoring, or gaps:
  - inspect detector backing and contradictions
  - answer any attached semantic questions
  - confirm or reject it from grounded repo evidence
- Only accepted concepts should strongly influence `atlas.json.concepts`, concept-driven monitoring, or concept-driven gaps.
- Tentative concepts should be weakly expressed or omitted.
- Do not let concept labels override direct evidence about dependency direction, runtime ownership, or configurable state semantics.

## Goal

Use deterministic evidence plus targeted semantic judgment to produce grounded concept output without broad semantic preload.
