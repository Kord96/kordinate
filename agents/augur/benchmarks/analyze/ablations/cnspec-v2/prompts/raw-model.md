Use a true raw-model cold analysis on this repo.

Repo:
- `/kord/shared/repos/mondoohq--cnspec`

Task:
- inspect the repo from scratch
- generate:
  - `atlas.json`
  - `stories/*.yaml`
  - `narratives.yaml`

Output directory:
- `/tmp/augur-ablation/cnspec-v2/raw-model`

Rules:
- do not read any Augur run artifacts
- do not read any deterministic fact files
- do not read Augur schemas
- do not use Augur validator or repair loop
- do not use Augur skills or semantic memory
- rely only on repo inspection and your own judgment

At the end, report:
- what you generated
- a brief quality self-assessment
- whether any Augur artifacts were consulted
