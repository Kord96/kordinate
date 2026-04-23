Use repo inspection plus canonical schemas, but no validator or repair loop.

Repo:
- `/kord/shared/repos/mondoohq--cnspec`

Task:
- inspect the repo from scratch
- generate:
  - `atlas.json`
  - `stories/*.yaml`
  - `narratives.yaml`

Output directory:
- `/tmp/augur-ablation/cnspec-v2/schemas-only`

Allowed reads:
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/atlas-schema.md`
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/story-schema.md`
- `/kord/workstation/home/project/kordinate/agents/augur/schemas/narratives-schema.md`

Rules:
- do not read any Augur run artifacts
- do not read deterministic fact files
- do not use Augur validator or repair loop
- do not use Augur skills or semantic memory

At the end, report:
- what you generated
- a brief quality self-assessment
- whether any Augur artifacts beyond the three schemas were consulted
