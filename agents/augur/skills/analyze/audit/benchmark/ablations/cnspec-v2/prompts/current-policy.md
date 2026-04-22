Use the full current Augur policy on the prepared CNSpec pack.

Pack:
- `/kord/agents/augur-local-codex/memory/projects/mondoohq--cnspec/analysis/eb0390792c16b23ecfe9e2ea46faa24712c7747b/2026-04-18T02-50-38Z/local-codex-pack/PACK.json`

Requirements:
- read `PACK.json`
- read `PROMPT.md`
- perform a true cold semantic pass from the prepared deterministic artifacts and repo code
- do not read or reuse `atlas.json`, `stories/*.yaml`, or `narratives.yaml` from any previous run for this repo
- generate from scratch:
  - `atlas.json`
  - `stories/*.yaml`
  - `narratives.yaml`
- validate in a loop with:
  - `python3 /kord/workstation/home/project/kordinate/agents/augur/skills/analyze/validator/validate.py /kord/agents/augur-local-codex/memory/projects/mondoohq--cnspec/analysis/eb0390792c16b23ecfe9e2ea46faa24712c7747b/2026-04-18T02-50-38Z`
- after each validation attempt, read `log.json`
- continue until the latest log iteration status is `valid`

At the end, report:
- whether all deterministic seed artifacts existed
- whether log.json existed
- validator result
- whether any previous semantic outputs were consulted
- a brief quality self-assessment
