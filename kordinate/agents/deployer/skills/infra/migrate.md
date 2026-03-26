Execute workstation migration — build image, create PVC, migrate data, deploy.

Requires deployer authentication. The deployer executes all phases via SSH to the control plane.
The only human action is verifying from the new pod and running `/infra migrate-cleanup`.

**Input**: $ARGUMENTS (optional: target cluster, e.g. `home` or `vandc`)

## Procedure

### Phase 1: Extract data from running pod

The current workstation-home PVC is RWO and mounted. Extract data from inside.

```bash
tar czf /tmp/kord-migration.tar.gz --exclude='S.gpg-agent*' \
  -C /home/claude .password-store .ssh .gnupg .kord kordinate
scp /tmp/kord-migration.tar.gz kkord@<CONTROL_PLANE_IP>:/tmp/
```

Resolve CONTROL_PLANE_IP from `profile/config.yaml` — use the cluster's `tailscale_ip`.

### Phase 2: Build and import workstation image

```bash
scp -r $KORDINATE_HOME/agents/deployer/skills/infra/images/workstation/ kkord@<CONTROL_PLANE_IP>:/tmp/workstation-build/
ssh kkord@<CONTROL_PLANE_IP> "
  sudo k3s ctr images tag docker.io/library/workstation:latest docker.io/library/workstation:pre-migration 2>/dev/null || true
  cd /tmp/workstation-build && docker build -t workstation:latest .
  docker save workstation:latest | sudo k3s ctr images import -
"
```

### Phase 3: Create kord PVC and migrate data

Read `STORAGE_CLASS` from cluster overlay or default to `longhorn`.

```bash
# Apply PVC + init job (substitute STORAGE_CLASS)
sed 's/STORAGE_CLASS/<sc>/' master-kord-storage.yaml | ssh kkord@<IP> "sudo kubectl apply -n master -f -"

# Wait for init
ssh kkord@<IP> "sudo kubectl wait -n master --for=condition=Complete job/kord-init --timeout=120s"

# Run migration pod: extract tarball into kord PVC
# Mount /tmp from host to access the tarball, mount kord PVC for output
# Copy: .password-store -> pass/, .gnupg -> gnupg/, .ssh -> ssh/, .kord -> kordinate/, kordinate -> projects/
# chown to claude user (UID 1001)
```

### Phase 4: Update secrets

Read tunnel token from pass store, apply secret via kubectl.

```bash
TUNNEL_TOKEN=$(pass show kordinate/cloudflare/tunnel_token)
ssh kkord@<IP> "sudo kubectl create secret generic cloudflared-tunnel -n master \
  --from-literal=TUNNEL_TOKEN='$TUNNEL_TOKEN' --dry-run=client -o yaml | sudo kubectl apply -f -"
```

### Phase 5: Apply workstation manifest

Substitute `REGISTRY/` placeholder (home cluster has no registry — remove prefix).
Substitute `STORAGE_CLASS` if present.

```bash
sed 's|REGISTRY/||' master-workstation.yaml | ssh kkord@<IP> "sudo kubectl apply -n master -f -"
```

### Phase 6: Monitor rolling update

```bash
ssh kkord@<IP> "sudo kubectl rollout status deploy/workstation -n master --timeout=300s"
ssh kkord@<IP> "sudo kubectl get pods -n master -l app=workstation"
```

Both old and new pods run during rollout. Cloudflare SSH works through either.

### Phase 7: Report and hand off to human

Report:
- New pod status (all 3 containers running)
- Old pod status (terminating or terminated)
- Cloudflare tunnel connections active

Instruct the human:
1. SSH into the new pod from an external device: `ssh workstation`
2. Verify you're on the new pod: `ls /kord/`
3. Run `/infra migrate-cleanup` to verify and clean up

## Notes

- Rolling update (maxSurge:1, maxUnavailable:0) ensures zero-downtime
- Both pods connect to the same Cloudflare tunnel during overlap
- Tailscale briefly conflicts (new pod deletes old workstation node) — Cloudflare SSH is unaffected
- Home cluster has no container registry — images imported directly into k3s containerd
- workstation-home PVC is RWO — data extracted via tarball, not dual-mount
- Old PVCs are NOT deleted by this procedure — that's `/infra migrate-cleanup`
