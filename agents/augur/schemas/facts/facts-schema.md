# Facts Schema

Consumer-facing entrypoint for the Augur facts contract.

The canonical normalized facts schema now lives with detector source assets:

- [../../detectors/schema.md](../../detectors/schema.md)

Why:
- detectors own deterministic fact production
- the normalized fact shape is part of the detector contract
- semantic consumers should read the detector-owned schema, not redefine it

Use this file as the consumer-facing pointer from `schemas/`.

## What Counts As A Fact

Facts are:
- deterministic
- normalized
- emitted by detector infrastructure
- stored under run-local `facts/`

Facts are not:
- semantic observations
- architectural conclusions
- planning hints
- model-authored judgments

Detector metadata may carry `review_questions`, but those live at the
detector level, not repeated on each fact record.

If an artifact needs confidence, semantic uncertainty, or recommendations, it
belongs in `observations/`, not `facts/`.

## Related Contracts

- [../../detectors/schema.md](../../detectors/schema.md)
  - canonical normalized facts schema
- [../observations/observations-schema.md](../observations/observations-schema.md)
  - normalized semantic observation contract
- [concepts-schema.md](concepts-schema.md)
  - raw deterministic precursor contract for `facts/concepts.json`
