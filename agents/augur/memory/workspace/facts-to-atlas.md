# Facts To Atlas

This workspace note captures the new facts-first wiring for Augur.

## Pipeline

```text
detectors -> facts -> concept inference -> atlas synthesis
```

## User-facing entrypoint

The synthesis CLI reads facts and, when available, concept decisions. It derives the atlas sections that can be built directly from first-order evidence and then late-loads concept monitoring guidance:

```bash
python3 scripts/synthesize_atlas_from_facts.py <facts-dir> --concepts <concepts.json> --project <name> --output <atlas.json>
```

## What it derives

- `stack`
- `domain_model` hints
- `api_surface`
- `state`
- `external_dependencies`
- `module_graph`
- attached `health` enrichment on components and dependencies when concept metadata exists
- top-level `business_metrics` when concept metadata provides them

## What it does not replace

- concept detection
- semantic questions
- anti-pattern reasoning
- debt scoring

Those remain in the concept layer and atlas composer.
