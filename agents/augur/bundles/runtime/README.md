# Augur runtime bundles

These are runtime composition manifests for Augur `/analyze`.

They are not meant to inline the full prompt prefix anymore.

## Bundles

- `analyze-holistic-v1.json` — composition manifest for large-context models using holistic semantic preload
- `analyze-selective-v1.json` — composition manifest for constrained models using selective semantic preload

## Rule

Runtime bundles should reference:

- the stable skill bundle
- the chosen memory bundle
- the detector execution plan
- repo/run context as the final appended layer

They should not duplicate the entire memory preload text inside the runtime artifact.
