# Bundle Mode: Selective

Use this guidance when the prepared bundle mode is `selective`.

Selective mode means only summaries and indexes are resident at startup. Full concept definitions should be read on demand.

## Expectations

- Start from prepared facts, startup artifacts, and targeted repo reads before loading extra concept details.
- Read full concept definitions only when the current architectural question, ambiguity, or nearby-pattern decision justifies the extra context.
- Use `facts/concept-evidence.json` and any attached review questions early when they materially improve architectural interpretation.
- Keep concept reads proportional to the architectural stakes of the ambiguity you are resolving.
- Do not let detector-suggested concepts replace direct grounding from entrypoints, registrations, state boundaries, and cross-component interactions.
- Do not let on-demand concept reads override direct evidence about dependency direction or configurable state semantics.

## Goal

Preserve architecture-first synthesis while spending semantic context only where it changes the analysis.
