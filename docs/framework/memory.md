# Recall System

## Memory Properties

Every piece of knowledge in kordinate is described by five properties:

| Property | Question | Values | Default |
|----------|----------|--------|---------|
| **Structured** | Does it follow a template? | `true` / `false` | `false` |
| **On-demand** | Preloaded or read when needed? | `true` / `false` | `true` |
| **Owner** | Who owns it? | `team` / `agent` | `agent` |
| **Scope** | Where does it apply? | `global` / `project` | `global` |
| **Expiry** | Does it expire? | `none` / `<script>` / `<.md>` | `none` |

Files with no frontmatter use the defaults. Override any property in YAML frontmatter.

### Constraints

- **On-demand files must be indexed** in the owner's `index.md`. Orphaned on-demand files are dead knowledge. Dead-end detection: scan on-demand files, compare to index, flag anything missing.
- **Structured files** are owned by scribe. A guard hook validates writes against the template — only scribe can create or modify structured files. Unstructured files are writable by any agent.
- **`index.md`** is auto-generated per owner (team and each agent). Lists all on-demand files. Preloaded so the agent knows what to look for.

## Templates

Scribe maintains a registry of structured patterns and on-demand indexes. The guard hook reads this to decide what to protect. Users extend via scribe.

| Pattern | Template | Required Sections |
|---------|----------|-------------------|
| `*/identity.md` | identity | frontmatter (name, model, tools, triggers), Auth, Workflow, Rules, Consultation |
| `*/commands/*/SKILL.md` | command | frontmatter (name, description), free-form procedure |
| `*/index.md` | index | File + Description table |
| `team/index.md` | team-index | Agents table, Shared Rules, Kords table |
| `team/kords/*/contract.md` | kord-contract | frontmatter (description, requester, provider), Provider Guidelines, Response Format, Provider State Invalidation |
| `team/kords/*/data.md` | kord-data | follows contract's Response Format |

**On-demand patterns** — files matching these must appear in an `index.md`:

- `*/memory/*.md`
- `team/memory/*.md`
- `team/kords/*/contract.md`

Any file with `structured: true` in frontmatter that doesn't match a registered pattern is drift — blocked by the guard.

??? note "Template examples"

    ??? example "team/index.md"

        ```markdown
        ## Agents

        | Agent | Role |
        |-------|------|
        | deployer | Infrastructure operations |

        ## Shared Rules

        - All .md files protected — only scribe may edit

        ## Kords

        | Kord | Provider |
        |------|----------|
        | deployer-default | deployer |
        ```

    ??? example "identity.md"

        ```markdown
        ---
        name: deployer
        model: inherit
        tools: [Read, Edit, Write, Bash, Glob]
        triggers: ["roll", "migrate"]
        ---

        # Deployer

        Infrastructure operations.

        ## Auth

        Copy profile/locks/deployer to /tmp/.deployer-auth before writes.

        ## Workflow

        1. Verify source health
        2. Apply manifests
        3. Verify target health

        ## Rules

        - Never patch a project's Dockerfile
        - Use cluster registry

        ## Consultation

        Cluster state, versions, configuration, networking.
        ```

    ??? example "commands/*/SKILL.md"

        ```markdown
        ---
        name: roll
        description: Roll deployments between environments
        argument-hint: [source] [target]
        allowed-tools: Read, Edit, Bash, Glob
        ---

        Roll $ARGUMENTS between environments:

        1. Verify source environment health
        2. Apply manifests to target
        3. Verify target health
        ```

    ??? example "contract.md"

        ```markdown
        ---
        description: General deployment and cluster questions
        requester: any
        provider: deployer
        ---

        ## Provider Guidelines

        Answer with specific names, endpoints, and configuration paths.
        Keep under 50 lines.

        ### Response Format

        | Field | Required |
        |-------|----------|
        | Infrastructure topology | yes |
        | Monitoring pipeline | yes |
        | Configuration sources | if applicable |

        ## Provider State Invalidation

        Invalidate when:
        - Cluster manifests are modified
        - Services are redeployed
        ```

    ??? example "index.md"

        ```markdown
        | File | Description |
        |------|-------------|
        | memory/infra.md | Infrastructure reference |
        | memory/migration.md | Migration procedures |
        ```

## Framework Memories

Memories that ship with kordinate and their properties:

### Team

| File | Path | Purpose | Structured | On-demand | Expiry |
|------|------|---------|:----------:|:---------:|:------:|
| team index | `team/index.md` | Team roster — agents, shared rules, available kords | yes | no | — |
| shared knowledge | `team/memory/*.md` | Team-wide reference — conventions, standards | varies | varies | varies |
| kord contract | `team/kords/<name>/contract.md` | Consultation protocol between agents | yes | yes | — |
| kord data | `team/kords/<name>/data.md` | Cached result of a consultation | yes | yes | `expiry.sh` |
| kord registry | `team/kords/index.md` | Lists all available kords | yes | no | — |

### Agent

| File | Path | Purpose | Structured | On-demand | Expiry |
|------|------|---------|:----------:|:---------:|:------:|
| identity | `<agent>/identity.md` | Who the agent is — role, tools, auth, workflow, rules | yes | no | — |
| index | `<agent>/index.md` | Lists available on-demand files | yes | no | — |
| commands | `<agent>/commands/*/SKILL.md` | Skill definitions — invoked by name | yes | yes | — |
| memory | `<agent>/memory/*.md` | Domain knowledge, notes, findings | varies | varies | varies |

### Project Level

Any file can have `scope: project` in frontmatter. Project-scoped files follow the same structure but live under `<project>/.kord/` instead of `~/.kord/`.
