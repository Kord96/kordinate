# Repo Sourcing Pass 3 Prompt

Use this after pass 2 to improve evaluation practicality.

## Prompt

```text
Suggest 6 public GitHub repositories that would be strong candidates for a benchmark dataset for evaluating an AI agent's ability to analyze software architecture and codebases.

This is pass 3. Focus on remaining gaps:
- stable, labelable mid-sized repos rather than only giant systems
- desktop, native, or mobile applications
- messy but maintained non-framework applications
- smaller repos that are architecturally discriminative
- adversarial-but-fair repos where naming or layout could mislead shallow analysis

Avoid repeating obvious famous picks unless they are unusually strong additions.

Return JSON only as an array. For each repo object include exactly these fields:
- repo
- reason_for_inclusion
- what_it_tests
- risks_or_caveats
```

## Notes

- Prefer candidates that are practical to pin, clone, and label.
- This pass should improve benchmark quality, not just benchmark size.
