# CNSpec Ablation Set v2

This set is the cleaner second-round ablation for CNSpec. It separates:

- raw model ability
- schema value
- validator/repair value
- deterministic facts value
- full current Augur policy

Repo:
- `mondoohq--cnspec`
- commit: `eb0390792c16b23ecfe9e2ea46faa24712c7747b`
- repo root: `/kord/shared/repos/mondoohq--cnspec`

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

## Automation

Run all conditions in parallel:

```bash
python3 /kord/workstation/home/project/kordinate/agents/augur/benchmarks/scripts/run_ablation_codex.py \
  /kord/workstation/home/project/kordinate/agents/augur/benchmarks/analyze/ablations/cnspec-v2/manifest.json \
  --model gpt-5.4 \
  --jobs 5
```
