Use repo inspection plus canonical schemas plus validator/repair, but no deterministic facts or semantic memory.

Repo:
- `/kord/shared/repos/matrixorigin--matrixone`

Output directory:
- `/tmp/augur-ablation/matrixone-v2/schemas-plus-validator`

Allowed reads:
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/atlas-schema.md`
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/story-schema.md`
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/narratives-schema.md`
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/log-schema.md`

Task:
- inspect the repo from scratch
- generate:
  - `atlas.json`
  - `stories/*.yaml`
  - `narratives.yaml`

Validation:
- run:
  - `python3 /kord/workstation/home/project/kordinate/agents/augur/skills/analyze/validator/validate.py /tmp/augur-ablation/matrixone-v2/schemas-plus-validator`
- after each validation attempt, read `/tmp/augur-ablation/matrixone-v2/schemas-plus-validator/log.json`
- continue until the latest log status is `valid`

Rules:
- do not read Augur deterministic fact files
- do not use Augur skills or semantic memory
- do not read prior semantic outputs

At the end, report:
- validator result
- a brief quality self-assessment
- whether any forbidden Augur artifacts were consulted
