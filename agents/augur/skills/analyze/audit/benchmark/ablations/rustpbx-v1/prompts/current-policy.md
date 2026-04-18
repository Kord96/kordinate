Use the full current Augur policy on the prepared RustPBX pack.

Pack:
- `/kord/agents/augur-local-codex/memory/projects/restsend--rustpbx/analysis/9e8f9100da2828ac6f627329655d55cac524dffb/2026-04-18T01-47-14Z/local-codex-pack/PACK.json`

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
  - `python3 /kord/workstation/home/project/kordinate/agents/augur/skills/analyze/scripts/validate_output.py /kord/agents/augur-local-codex/memory/projects/restsend--rustpbx/analysis/9e8f9100da2828ac6f627329655d55cac524dffb/2026-04-18T01-47-14Z`
- after each validation attempt, read `repair-log.json`
- continue until the latest repair-log iteration status is `valid`

At the end, report:
- whether all deterministic seed artifacts existed
- whether repair-log.json existed
- validator result
- whether any previous semantic outputs were consulted
- a brief quality self-assessment
