# jPOS Ablation Set v1

Use this set to measure which parts of Augur materially improve quality on a harder, subsystem-heavy Java repo.

Repo:
- `jpos--jPOS`
- commit: `0f3d309ee36b610be83843cac607fdb566a4b37b`
- repo root: `/kord/shared/repos/jpos--jPOS`

Output contract for every condition:
- `atlas.json`
- `stories/*.yaml`
- `narratives.yaml`

Shared scoring references:
- [augur-evaluation-plan.md](../../augur-evaluation-plan.md)
- [augur-pilot-execution-matrix.md](../../augur-pilot-execution-matrix.md)

## Conditions

1. `bare-model`
- no deterministic facts
- no Augur memory bundle
- no Augur skill
- only repo + schemas + task

2. `skill-no-facts`
- Augur workflow and schemas
- no deterministic facts
- no semantic memory bundle

3. `facts-no-memory`
- deterministic facts from the prepared run
- no Augur semantic memory bundle
- no Augur-local skill wrapper

4. `current-policy`
- full current Augur setup
- deterministic facts + semantic bundle + log loop + quality gate

## Goal

Answer:
- whether Augur’s advantage grows again on a more difficult repo than RustPBX
- how much quality comes from the model alone
- how much the Augur workflow adds
- how much deterministic prep adds
- how much the current semantic preload adds

## Notes

- Use the same backend model for all four conditions.
- Do not reuse prior semantic outputs between conditions.
- Treat each condition as a cold run.
- Score every run using the same rubric.

## Automation

Run all conditions non-interactively with:

```bash
python3 /kord/workstation/home/project/kordinate/agents/augur/benchmarks/scripts/run_ablation_codex.py \
  /kord/workstation/home/project/kordinate/agents/augur/benchmarks/analyze/ablations/jpos-v1/manifest.json \
  --model gpt-5.4
```

Run a subset:

```bash
python3 /kord/workstation/home/project/kordinate/agents/augur/benchmarks/scripts/run_ablation_codex.py \
  /kord/workstation/home/project/kordinate/agents/augur/benchmarks/analyze/ablations/jpos-v1/manifest.json \
  --model gpt-5.4 \
  --condition bare-model \
  --condition skill-no-facts
```

Runner artifacts are written under:

- `.../ablations/jpos-v1/runs/<timestamp>/`

Each condition gets:

- `run.json`
- `stdout.jsonl`
- `stderr.log`
- `final-message.txt`
