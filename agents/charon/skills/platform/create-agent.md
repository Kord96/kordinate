# Create Agent

Use this flow when adding a new daemon-backed agent to the platform.

## Goal

Add a new entry to `agent-spec.yaml`, regenerate base manifests, and make the new agent deployable through the normal `/platform deploy` path. The pod should run the shared `klaude-daemon` package, not a repo-local CLI clone.

Status: legacy. Kordinate no longer owns canonical generated platform
manifests. Use this document as historical design context unless the platform
runtime is revived or re-homed.

## Command Shape

`/platform create-agent <name> [--profile generic|generic-opus|generic-gemini-31-pro|generic-deepseek-reasoner|generic-glm5|generic-gpt54|augur-opus|augur-gemini-31-pro|augur-deepseek-reasoner|augur-glm5|augur-gpt54|charon-gpt53-codex|alfred-deepseek-chat|sauron-gpt53-codex] [profile-specific flags]`

## Steps

1. Validate the requested agent name:
   - kebab-case
   - not already present in `agent-spec.yaml`
   - request topic will be `<name>`

2. Resolve the creation profile from `agent-creation-profiles.yaml`.
   - `generic` creates a plain daemon-backed agent
   - specialist profiles may require extra choices
   - example: every Augur model profile requires both `--memory-bundle` and `--runtime-bundle`
   - profile defaults also determine the pod secret wiring unless explicitly overridden
  - for `codex-sdk` pod agents, prefer `workspace-write` sandbox mode; `approvalPolicy: never` already handles non-interactive execution
  - exception: `charon-gpt53-codex` is the cluster-ops profile and intentionally uses `danger-full-access` plus pod bootstrap for `kubectl` and `bubblewrap`
   - runtime selection is inferred from the chosen model unless `--runtime-kind` is explicitly set:
     - GPT family -> `codex-sdk`
     - Claude family -> `claude-agent-sdk`
     - everything else -> `openclaude-harness`

3. Append the new spec entry using:

```bash
python3 $KORDINATE_HOME/lib/scripts/create-agent-spec-entry.py <name> \
  --spec $KORDINATE_HOME/agents/charon/skills/platform/agent-spec.yaml \
  --profiles $KORDINATE_HOME/agents/charon/skills/platform/agent-creation-profiles.yaml \
  --profile <profile> \
  [--memory-bundle <bundle>] \
  [--runtime-bundle <bundle>] \
  [--provider <provider>] \
  [--model <model>] \
  [--backend <backend>] \
  [--secret-env <env-var>] \
  [--secret-name <secret-name>] \
  [--secret-key <secret-key>] \
  [--default-working-dir </path>]
```

4. Regenerate manifests from the updated spec:

```bash
python3 $KORDINATE_HOME/lib/scripts/generate-agent-manifests.py \
  $KORDINATE_HOME/agents/charon/skills/platform/agent-spec.yaml \
  --agents-out $KORDINATE_HOME/agents/charon/skills/platform/manifests/base/agents.yaml \
  --keda-out $KORDINATE_HOME/agents/charon/skills/platform/manifests/base/keda.yaml \
  --kafka-out $KORDINATE_HOME/agents/charon/skills/platform/manifests/base/kafka.yaml
```

5. Verify the generated manifests now contain:
   - `Deployment/agent-<name>`
   - `ScaledObject/agent-<name>`
   - `KafkaTopic/<name>`
   - `exec klaude-daemon` as the runtime command
   - provider API key env wired from the expected Secret

6. Report what was added and the next step:
   - `/platform deploy <env>` to apply
   - or `bash $KORDINATE_HOME/lib/scripts/apply-platform-manifests.sh <env> $KORDINATE_HOME/shared/runtime/profile/overlays/platform/<env>`
   - if this is a specialist flavor, ensure the required seed/runtime inputs exist

## Notes

- This flow creates a daemon-backed platform entry only.
- It does not scaffold a new agent directory under `agents/<name>/`.
- For a generic consultation agent, keep `flavor: generic`.
- For a deployed copy of a specialist flavor under a different name, use `--profile <specialist>` and keep the deployed `name` distinct.
- For any `augur-*` model profile, choose both:
  - `--memory-bundle analyze-holistic-v1|analyze-selective-v1`
  - `--runtime-bundle analyze-holistic-v1|analyze-selective-v1`
