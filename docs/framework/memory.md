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

- **Structured** files can only be written by scribe. See [Guards](guards.md) for enforcement details.
- **On-demand** files are discovered by scanning directories and reading frontmatter. No index files needed.

## Framework Memories

`MAP.md` lives at `~/.kord/MAP.md` — the single entry point. It lists all agents, team memory, and kords with descriptions.

=== "Agent"

    | File | Path | Purpose | Structured | On-demand | Expiry |
    |------|------|---------|:----------:|:---------:|:------:|
    | identity | `<agent>/identity.md` | Role, tools, auth, workflow, rules | yes | no | — |
    | skills | `<agent>/skills/<name>/SKILL.md` | Skill definitions | yes | yes | — |
    | memory | `<agent>/memory/*.md` | Domain knowledge, notes, findings | varies | yes | varies |

=== "Team"

    | File | Path | Purpose | Structured | On-demand | Expiry |
    |------|------|---------|:----------:|:---------:|:------:|
    | shared knowledge | `team/memory/*.md` | Team-wide conventions, standards | varies | varies | varies |
    | contract | `team/kords/<name>/contract.md` | Consultation protocol | yes | yes | — |
    | data | `team/kords/<name>/data.md` | Cached result | yes | yes | `team/kords/<name>/expiry.sh` |

### Project Level

Any file can have `scope: project` in frontmatter. Project-scoped files follow the same structure but live under `<project>/.kord/` instead of `~/.kord/`.

??? note "Templates"

    === "identity.md"

        ```markdown
        ---
        name: deployer
        description: Infrastructure operations — sole kubectl write authority
        model: inherit
        tools: [Read, Edit, Write, Bash, Glob]
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
