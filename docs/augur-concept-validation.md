# Augur Concept Validation

Augur concept units are validated from Markdown frontmatter. `meta.yaml` is not supported.

The repository does not currently carry the Augur concept catalog directly. Use the validator against an installed or checked-out Augur release:

```sh
python3 shared/skills/validate-output/validators/augur_concepts.py /path/to/augur/memory/concepts
```

If the catalog has a deterministic fact generator, run it as part of the same gate:

```sh
python3 shared/skills/validate-output/validators/augur_concepts.py /path/to/augur/memory/concepts \
  --fact-generator "/path/to/fact-generator --check"
```

The validator appends the catalog path to the fact-generator command.

## Deterministic Gate

The deterministic gate is strict and blocks on structural failures:

- every concept unit must contain `concept.md`
- every Markdown file in a concept unit must have YAML frontmatter
- frontmatter must include `description`, a kebab-case `concept` or `name`, and `type`, `kind`, or `taxonomy.type`
- concept type must be one of `pattern`, `anti-pattern`, `domain-model`, `flow-shape`, `structure-shape`, or `framework`
- boolean traits must be actual booleans
- detector strength must be an integer from 1 to 5
- diagnostic question ids must be stable kebab-case ids
- referenced detector, support-rule, and fact-generator files must exist
- `*.yaml` support files must parse
- `meta.yaml` fails; move schema data into Markdown frontmatter

## Semantic Gate

The semantic gate is intentionally small and score-based. It reports per-file scores for:

- specificity
- detectability
- evidence value
- noise control
- actionability

Low scores are warnings. Severe semantic problems block:

- the concept is too generic
- the concept lacks concrete detection signals
- the total rubric score is below 50/100

This keeps early semantic validation useful without turning every subjective improvement into a blocking condition.
