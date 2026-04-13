# Repo Sourcing Prompt

Use this for the first pass of cross-model candidate generation.

Goal: let each model apply its own benchmark criteria while still returning mergeable structured output.

## Prompt

```text
Suggest 25 public GitHub repositories that would be strong candidates for a benchmark dataset for evaluating an AI agent's ability to analyze software architecture and codebases.

Use your own judgment for selection criteria. Do not follow a pre-made rubric. Give your independent view of what makes a repository benchmark-worthy.

Prioritize diversity, discriminative value, and practical usefulness. Avoid suggesting only the most famous repos unless they are especially valuable benchmark cases. Include a mix of straightforward, messy, and difficult repos.

Return JSON only as an array. For each repo object include exactly these fields:
- repo
- reason_for_inclusion
- what_it_tests
- risks_or_caveats
```

## Notes

- Use the same prompt for Gemini, DeepSeek, Claude, and other candidate-generating models.
- Keep this pass open-ended. Do not impose benchmark buckets yet.
- Normalize outputs after collection into the shared candidate schema.
- In a later pass, ask follow-up questions only after reviewing merged duplicates and gaps.
