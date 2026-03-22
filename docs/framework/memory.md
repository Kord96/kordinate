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

- **On-demand files must be indexed** in the owner's `index.md`. Orphaned on-demand files are dead knowledge.
- **Structured files** are owned by scribe. A guard hook validates writes against the template — only scribe can create or modify structured files. Unstructured files are writable by any agent.
- **`index.md`** is auto-generated per owner (team and each agent). Preloaded so the agent knows what on-demand files are available.

## Framework Memories

=== "Agent"

    | File | Path | Purpose | Structured | On-demand | Expiry |
    |------|------|---------|:----------:|:---------:|:------:|
    | identity | `<agent>/identity.md` | Role, tools, auth, workflow, rules | yes | no | — |
    | index | `<agent>/memory/index.md` | On-demand file listing | yes | no | — |
    | commands | `<agent>/commands/*/SKILL.md` | Skill definitions | yes | yes | — |
    | memory | `<agent>/memory/*.md` | Domain knowledge, notes, findings | varies | varies | varies |

=== "Team"

    | File | Path | Purpose | Structured | On-demand | Expiry |
    |------|------|---------|:----------:|:---------:|:------:|
    | manifest | `team/manifest.md` | Team roster — agents, rules, kords | yes | no | — |
    | shared knowledge | `team/memory/*.md` | Team-wide conventions, standards | varies | varies | varies |

=== "Kord"

    | File | Path | Purpose | Structured | On-demand | Expiry |
    |------|------|---------|:----------:|:---------:|:------:|
    | contract | `team/kords/<name>/contract.md` | Consultation protocol | yes | yes | — |
    | data | `team/kords/<name>/data.md` | Cached result | yes | yes | `expiry.sh` |
    | expiry | `team/kords/<name>/expiry.sh` | Staleness check script | — | — | — |
    | registry | `team/kords/index.md` | Lists all available kords | yes | no | — |

Users extend the structured patterns via scribe. Any file with `structured: true` in frontmatter that doesn't match a registered pattern is drift — blocked by the guard.

### Project Level

Any file can have `scope: project` in frontmatter. Project-scoped files follow the same structure but live under `<project>/.kord/` instead of `~/.kord/`.

### Templates

??? note "Templates"

    === "manifest.md"

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

    === "identity.md"

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

    === "SKILL.md"

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

    === "contract.md"

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

    === "data.md"

        Follows the Response Format from the kord's `contract.md`:

        ```markdown
        Infrastructure topology: k3s cluster, gateway + monitor + master namespaces
        Monitoring pipeline: Alloy → Prometheus + Loki → Grafana
        Configuration sources: manifests/gateway/base/, master-alloy.yml
        ```

    === "index.md"

        ```markdown
        | File | Description |
        |------|-------------|
        | memory/infra.md | Infrastructure reference |
        | memory/migration.md | Migration procedures |
        ```
