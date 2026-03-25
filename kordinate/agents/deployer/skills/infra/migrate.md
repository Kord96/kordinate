Prepare workstation migration manifests and handover file.

Does NOT perform the migration — generates the artifacts for external execution.

**Input**: $ARGUMENTS (optional: target cluster, e.g. `home` or `vandc`)

## Procedure

1. Read current workstation config from profile/config.yaml
2. Read current workstation manifest from agents/deployer/manifests/gateway/base/workstation.yaml
3. Generate the migration handover file at agents/deployer/memory/dynamic/workstation-handover.md with:
   - Current workstation state (cluster, namespace, Tailscale hostname)
   - Step-by-step external migration instructions:
     1. Apply the new workstation manifest: `kubectl apply -n gateway -f workstation.yaml`
     2. Wait for pod ready: `kubectl wait -n gateway --for=condition=Ready pod -l component=workstation --timeout=300s`
     3. Verify Tailscale is up: `kubectl logs -n gateway -l component=workstation | grep "Tailscale up"`
     4. SSH to new workstation and verify: `ssh workstation`
     5. On new workstation: `cd ~/kordinate && ./installer/setup-shell.sh` then run `/onboard sync` to link the framework
     6. Run `/boot` to pick up handover context
     7. Delete old workstation: `kubectl delete -n <old-namespace> deploy workstation`
   - Post-migration checklist:
     - [ ] SSH works to new workstation
     - [ ] tmux auto-attaches to 0-general
     - [ ] kordinate framework linked
     - [ ] All agents responsive
     - [ ] Old workstation deleted
4. Commit and push the handover file
5. Report: "Handover file ready at agents/deployer/memory/dynamic/workstation-handover.md — follow the external steps to complete migration."

## Notes

- The handover file is deployer's dynamic memory so the new workstation's deployer instance can read it via /boot
- The human applies manifests externally because migrating from inside the pod being replaced is unsafe
- Tailscale hostname conflicts are avoided because the new pod starts fresh — the old one should be deleted after verification
