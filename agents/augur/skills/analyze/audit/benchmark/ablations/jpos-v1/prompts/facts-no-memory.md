Use the prepared deterministic artifacts, but do not use Augur semantic memory or the Augur-local-analyze wrapper.

Repo:
- `/kord/shared/repos/jpos--jPOS`

Prepared run artifacts:
- `/kord/agents/augur-local-codex/memory/projects/jpos--jPOS/analysis/0f3d309ee36b610be83843cac607fdb566a4b37b/2026-04-18T02-20-39Z`

Output directory:
- `/tmp/augur-ablation/jpos-v1/facts-no-memory`

Read first:
- `/kord/agents/augur-local-codex/memory/projects/jpos--jPOS/analysis/0f3d309ee36b610be83843cac607fdb566a4b37b/2026-04-18T02-20-39Z/blast.json`
- `/kord/agents/augur-local-codex/memory/projects/jpos--jPOS/analysis/0f3d309ee36b610be83843cac607fdb566a4b37b/2026-04-18T02-20-39Z/facts/startup.json`
- `/kord/agents/augur-local-codex/memory/projects/jpos--jPOS/analysis/0f3d309ee36b610be83843cac607fdb566a4b37b/2026-04-18T02-20-39Z/facts/facts-guide.json`
- `/kord/agents/augur-local-codex/memory/projects/jpos--jPOS/analysis/0f3d309ee36b610be83843cac607fdb566a4b37b/2026-04-18T02-20-39Z/facts/index.json`

You may use:
- the deterministic fact files in that run
- the canonical output schemas:
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/atlas-schema.md`
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/story-schema.md`
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/narratives-schema.md`
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/log-schema.md`

You must not use:
- Augur semantic memory bundle
- Augur-local-analyze skill
- any previous semantic outputs for this repo

Task:
- use the deterministic artifacts plus repo code to generate:
  - `atlas.json`
  - `stories/*.yaml`
  - `narratives.yaml`

Validation:
- run:
  - `python3 /kord/workstation/home/project/kordinate/agents/augur/skills/analyze/validator/validate.py /tmp/augur-ablation/jpos-v1/facts-no-memory`
- after each validation attempt, read `/tmp/augur-ablation/jpos-v1/facts-no-memory/log.json`
- continue until the latest log status is `valid`

At the end, report:
- validator result
- whether semantic memory was consulted
- a brief quality self-assessment
