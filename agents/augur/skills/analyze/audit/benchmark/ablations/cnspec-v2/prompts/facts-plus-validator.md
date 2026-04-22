Use repo inspection plus deterministic facts plus schemas and validator/repair, but no semantic memory or Augur-local skill.

Repo:
- `/kord/shared/repos/mondoohq--cnspec`

Prepared run artifacts:
- `/kord/agents/augur-local-codex/memory/projects/mondoohq--cnspec/analysis/eb0390792c16b23ecfe9e2ea46faa24712c7747b/2026-04-18T02-50-38Z`

Output directory:
- `/tmp/augur-ablation/cnspec-v2/facts-plus-validator`

Read first:
- `/kord/agents/augur-local-codex/memory/projects/mondoohq--cnspec/analysis/eb0390792c16b23ecfe9e2ea46faa24712c7747b/2026-04-18T02-50-38Z/blast.json`
- `/kord/agents/augur-local-codex/memory/projects/mondoohq--cnspec/analysis/eb0390792c16b23ecfe9e2ea46faa24712c7747b/2026-04-18T02-50-38Z/facts/startup.json`
- `/kord/agents/augur-local-codex/memory/projects/mondoohq--cnspec/analysis/eb0390792c16b23ecfe9e2ea46faa24712c7747b/2026-04-18T02-50-38Z/facts/facts-guide.json`
- `/kord/agents/augur-local-codex/memory/projects/mondoohq--cnspec/analysis/eb0390792c16b23ecfe9e2ea46faa24712c7747b/2026-04-18T02-50-38Z/facts/index.json`

Allowed reads:
- the deterministic fact files in that run
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/atlas-schema.md`
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/story-schema.md`
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/narratives-schema.md`
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/log-schema.md`

Task:
- use repo code plus deterministic artifacts to generate:
  - `atlas.json`
  - `stories/*.yaml`
  - `narratives.yaml`

Validation:
- run:
  - `python3 /kord/workstation/home/project/kordinate/agents/augur/skills/analyze/validator/validate.py /tmp/augur-ablation/cnspec-v2/facts-plus-validator`
- after each validation attempt, read `/tmp/augur-ablation/cnspec-v2/facts-plus-validator/log.json`
- continue until the latest log status is `valid`

Rules:
- do not use Augur semantic memory bundle
- do not use Augur-local-analyze skill
- do not read previous semantic outputs

At the end, report:
- validator result
- a brief quality self-assessment
- whether semantic memory or prior semantic outputs were consulted
