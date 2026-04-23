# MatrixOne Ablation Set v2

This set is the cleaner second-round ablation for MatrixOne. It separates:

- raw model ability
- schema value
- validator/repair value
- deterministic facts value
- full current Augur policy

Repo:
- `matrixorigin--matrixone`
- commit: `68390b227551e2189ed6a071dab92f8983436088`
- repo root: `/kord/shared/repos/matrixorigin--matrixone`

Output contract target:
- `atlas.json`
- `stories/*.yaml`
- `narratives.yaml`

## Conditions

1. `raw-model`
- repo only
- no Augur schemas
- no validator
- no repair loop

2. `schemas-only`
- repo + canonical schemas
- no validator
- no repair loop

3. `schemas-plus-validator`
- repo + canonical schemas
- validator + repair loop
- no deterministic facts

4. `facts-plus-validator`
- repo + deterministic facts + schemas
- validator + repair loop
- no semantic memory

5. `current-policy`
- full current Augur setup

## Goal

Answer more cleanly:

- how much quality the base model has with no Augur scaffolding
- how much schemas add
- how much validator and repair add
- how much deterministic facts add
- how much the full current semantic policy adds on top

## Automation

Run all conditions in parallel:

```bash
python3 /kord/workstation/home/project/kordinate/agents/augur/benchmarks/scripts/run_ablation_codex.py \
  /kord/workstation/home/project/kordinate/agents/augur/benchmarks/analyze/ablations/matrixone-v2/manifest.json \
  --model gpt-5.4 \
  --jobs 5
```
