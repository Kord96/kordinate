# Repo Sourcing Pass 2 Prompt

Use this after reviewing the first-pass merged pool.

Goal: fill concrete coverage gaps without prescribing exact benchmark buckets.

## Prompt

```text
Suggest 10 public GitHub repositories that would be strong candidates for a benchmark dataset for evaluating an AI agent's ability to analyze software architecture and codebases.

This is pass 2. Do not suggest generic famous repos unless they are unusually valuable.

Focus on gaps in the current candidate pool:
- Java application repos, not just libraries/frameworks
- mid-sized Go application repos
- event-driven, worker-heavy, or data-pipeline systems
- messy but stable non-framework applications
- smaller repos that are still architecturally discriminative

Use your own judgment for selection criteria. Prioritize repos that add new benchmark value rather than repeating the same stack archetypes.

Return JSON only as an array. For each repo object include exactly these fields:
- repo
- reason_for_inclusion
- what_it_tests
- risks_or_caveats
```

## Notes

- This pass is targeted gap-filling, not broad ideation.
- Prefer candidates that are labelable and stable enough to pin.
- After collection, merge with pass 1 and then review overlap and remaining gaps.
