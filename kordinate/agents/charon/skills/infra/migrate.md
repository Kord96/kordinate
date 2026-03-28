Execute workstation migration — build image, create PVC, migrate data, deploy.

Requires charon authentication. The charon executes all phases via SSH to the control plane.
The only human action is verifying from the new pod and running `/infra migrate-cleanup`.

**Input**: $ARGUMENTS — target cluster (e.g. `home`, `vandc`)

## Procedure

### Phase 1: Extract data from running pod

The current pod's kord PVC may be RWO. Extract data from inside via tarball.

```bash
tar czf /tmp/kord-migration.tar.gz --exclude='S.gpg-agent*' \
  -C /home/claude .password-store .ssh .gnupg .kord kordinate
scp /tmp/kord-migration.tar.gz kkord@<CONTROL_PLANE_IP>:/tmp/
```

Resolve CONTROL_PLANE_IP from `profile/config.yaml` — use the cluster's `tailscale_ip`.

### Phase 2: Ensure Longhorn is installed

```bash
ssh kkord@<IP> "sudo kubectl get ns longhorn-system" || {
  # Install open-iscsi prerequisite on all nodes
  ssh kkord@<IP> "sudo apt-get install -y open-iscsi && sudo systemctl enable --now iscsid"
  # Install Longhorn
  ssh kkord@<IP> "sudo kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.7.3/deploy/longhorn.yaml"
  # Wait for rollout
  ssh kkord@<IP> "sudo kubectl -n longhorn-system rollout status deploy/longhorn-driver-deployer --timeout=120s"
  ssh kkord@<IP> "sudo kubectl -n longhorn-system rollout status daemonset/longhorn-manager --timeout=120s"
}
```

Verify the `longhorn` StorageClass uses `driver.longhorn.io` (not `rancher.io/local-path`):
```bash
ssh kkord@<IP> "sudo kubectl get sc longhorn -o jsonpath='{.provisioner}'"
```

### Phase 3: Build and import workstation image

```bash
scp -r $KORDINATE_HOME/agents/charon/skills/infra/images/workstation/ kkord@<IP>:/tmp/workstation-build/
ssh kkord@<IP> "
  sudo k3s ctr images tag docker.io/library/workstation:latest docker.io/library/workstation:pre-migration 2>/dev/null || true
  cd /tmp/workstation-build && docker build -t workstation:latest .
  docker save workstation:latest | sudo k3s ctr images import -
"
```

### Phase 4: Create kord PVC (Longhorn RWX) and migrate data

```bash
# Apply PVC + init job
sed 's/STORAGE_CLASS/longhorn/' master-kord-storage.yaml | ssh kkord@<IP> "sudo kubectl apply -n master -f -"
ssh kkord@<IP> "sudo kubectl wait -n master --for=condition=Complete job/kord-init --timeout=120s"

# Run migration pod: extract tarball into kord PVC
# Mount /tmp from host to access the tarball, mount kord PVC for output
# Copy: .password-store -> pass/, .gnupg -> gnupg/, .ssh -> ssh/, .kord -> kordinate/, kordinate -> projects/
# chown to claude user (UID 1001)
```

### Phase 5: Update secrets

Read tunnel token from pass store, apply secret via kubectl.

```bash
TUNNEL_TOKEN=$(pass show kordinate/cloudflare/tunnel_token)
ssh kkord@<IP> "sudo kubectl create secret generic cloudflared-tunnel -n master \
  --from-literal=TUNNEL_TOKEN='$TUNNEL_TOKEN' --dry-run=client -o yaml | sudo kubectl apply -f -"
```

### Phase 6: Apply workstation manifest

Substitute `REGISTRY/` placeholder (home cluster has no registry — remove prefix).

```bash
sed 's|REGISTRY/||' master-workstation.yaml | ssh kkord@<IP> "sudo kubectl apply -n master -f -"
```

### Phase 7: Apply overlay ConfigMaps

Generate overlays if needed, then apply generated ConfigMaps:

```bash
# Apply overlay-generated ConfigMaps (Caddyfile, datasources, etc.)
ssh kkord@<IP> "sudo kubectl apply -n master -f -" < profile/overlays/<cluster>/master/workstation-caddyfile.yaml
ssh kkord@<IP> "sudo kubectl apply -n master -f -" < profile/overlays/<cluster>/master/datasources.yaml
```

### Phase 8: Monitor rolling update

```bash
ssh kkord@<IP> "sudo kubectl rollout status deploy/workstation -n master --timeout=300s"
ssh kkord@<IP> "sudo kubectl get pods -n master -l app=workstation"
```

Both old and new pods run during rollout. Cloudflare SSH works through either.

### Phase 9: Report and hand off to human

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
- Longhorn RWX allows multiple pods to mount the kord PVC (workstation, docs, future services)
- Old PVCs are NOT deleted by this procedure — that's `/infra migrate-cleanup`
- Longhorn requires `open-iscsi` on all nodes — install as part of `setup-storage`
- To upgrade an existing PVC from local-path/RWO to Longhorn/RWX, use `/infra upgrade-storage` instead
