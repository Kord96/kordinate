# Facts To Atlas

This workspace note captures the new facts-first wiring for Augur.

## Pipeline

```text
detectors -> facts (including concept-evidence) -> atlas synthesis
```

## User-facing entrypoint

The synthesis CLI reads normalized facts only, including `concept-evidence.json` when present. It derives the atlas sections that can be built directly from first-order evidence and uses concept evidence as another fact domain rather than a special side-channel:

```bash
python3 scripts/synthesize_atlas_from_facts.py <facts-dir> --project <name> --output <atlas.json>
```

## What it derives

- `stack`
- `domain_model` hints
- `api_surface`
- `state`
- `external_dependencies`
- `module_graph`
- attached `health` enrichment on components and dependencies when concept evidence exists
- top-level `business_metrics` when concept evidence provides them

## What it does not replace

- deterministic concept evidence generation
- semantic questions
- anti-pattern reasoning
- debt scoring

Those remain in the semantic atlas composer.
