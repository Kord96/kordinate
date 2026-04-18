Use a plain cold analysis on this repo with no Augur facts and no Augur semantic bundle.

Repo:
- `/kord/shared/repos/restsend--rustpbx`

Task:
- analyze the current codebase from scratch
- generate:
  - `atlas.json`
  - `stories/*.yaml`
  - `narratives.yaml`

Output directory:
- `/tmp/augur-ablation/rustpbx-v1/bare-model`

Rules:
- do not read any existing Augur run outputs for this repo
- do not read Augur deterministic fact files
- do not use Augur memory bundle or Augur-local-analyze skill
- you may read only the canonical output schemas to know the required format:
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/atlas-schema.md`
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/story-schema.md`
  - `/kord/workstation/home/project/kordinate/agents/augur/schemas/narratives-schema.md`
- produce the outputs from repo inspection only

Validation:
- run:
  - `python3 /kord/workstation/home/project/kordinate/agents/augur/skills/analyze/scripts/validate_output.py /tmp/augur-ablation/rustpbx-v1/bare-model`
- if validation returns `INVALID` or `NEEDS_REFINEMENT`, repair and rerun until the latest repair-log status is `valid`

At the end, report:
- validator result
- whether any Augur run artifacts were consulted
- a brief quality self-assessment
