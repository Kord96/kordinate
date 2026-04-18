Use Augur workflow discipline, but do not use deterministic facts or semantic memory.

Repo:
- `/kord/shared/repos/jpos--jPOS`

Output directory:
- `/tmp/augur-ablation/jpos-v1/skill-no-facts`

Rules:
- do not read any existing Augur run outputs for this repo
- do not read any files under `facts/` from prior prepared runs
- do not use Augur semantic memory bundle
- do use the current Augur analyze workflow and repair-loop discipline:
  - `/kord/workstation/home/project/kordinate/agents/augur/skills/analyze/SKILL.md`
  - `/kord/workstation/home/project/kordinate/agents/augur/skills/analyze/modes/full.md`
- use the canonical output schemas:
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/atlas-schema.md`
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/story-schema.md`
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/narratives-schema.md`
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/repair-log-schema.md`

Task:
- analyze the repo from scratch
- generate:
  - `atlas.json`
  - `stories/*.yaml`
  - `narratives.yaml`

Validation:
- run:
  - `python3 /kord/workstation/home/project/kordinate/agents/augur/skills/analyze/scripts/validate_output.py /tmp/augur-ablation/jpos-v1/skill-no-facts`
- after each validation attempt, read `/tmp/augur-ablation/jpos-v1/skill-no-facts/repair-log.json`
- continue until the latest repair-log status is `valid`

At the end, report:
- validator result
- whether deterministic facts were consulted
- a brief quality self-assessment
