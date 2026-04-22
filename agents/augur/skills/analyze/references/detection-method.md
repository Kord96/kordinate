# Detection Method

Use this reference when interpreting deterministic concept evidence.

## Priority

1. start from `blast.json`, `startup.json`, and `index.json`
2. form a provisional architectural read from startup facts, high-signal domains, and targeted repo files
3. use `facts/concepts.json` to test or refine architectural interpretations that remain ambiguous
4. use the evidence-driven concept guidance appropriately
5. widen repo reads only when ambiguity remains after targeted fact and concept review

## Rules

- detector hits are grounded evidence, not final truth
- concept candidates are interpretation aids, not the primary map of the system
- when a concept candidate remains materially ambiguous, load only that concept's canonical reference and detector policy or rules; do not broaden into generic concept preload
- naming and folder structure alone are weak signals
- prefer `candidate` over `confirmed` when the structure is ambiguous
- counter evidence must lower confidence or block confirmation, and evidence gaps should prevent overconfident confirmation
- do not let concept labels override observed runtime directionality
- treat `depends_on` as runtime reliance, not as "is adjacent to", "serves", or "contains"
- when storage technology or persistence changes by configuration, keep the state model truthful to that variability instead of forcing one narrow store type

## Evidence Sources

- deterministic fact domains
- concepts records
- framework facts
- targeted repo reads

When a framework remains materially ambiguous, load only that framework's catalog files:
- `references/frameworks/<framework>.md`

## Goal

Use deterministic concept evidence plus review questions to improve semantic judgment without replacing direct architectural grounding.
