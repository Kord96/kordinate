Execute workstation migration — build image, create PVC, migrate data, deploy.

Requires charon authentication. The charon executes all phases via SSH to the control plane.
The only human action is verifying from the new pod and running `/migrate cleanup`.

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
3. Run `/migrate cleanup` to verify and clean up

## Notes

- Rolling update (maxSurge:1, maxUnavailable:0) ensures zero-downtime
- Both pods connect to the same Cloudflare tunnel during overlap
- Tailscale briefly conflicts (new pod deletes old workstation node) — Cloudflare SSH is unaffected
- Home cluster has no container registry — images imported directly into k3s containerd
- Longhorn RWX allows multiple pods to mount the kord PVC (workstation, docs, future services)
- Old PVCs are NOT deleted by this procedure — that's `/migrate cleanup`
- Longhorn requires `open-iscsi` on all nodes — install as part of `setup-storage`
- To upgrade an existing PVC from local-path/RWO to Longhorn/RWX, use `/bootstrap upgrade-storage` instead

---

Post-migration verification and cleanup. Run from the NEW workstation pod after migration.

**Input**: $ARGUMENTS (none required)

## Pre-condition

Must be running on the new workstation (check: `/kord/` mount exists, cloudflared and caddy sidecars running).

## Procedure

### Step 1: Verify this is the new pod

```bash
[ -d /kord ] && echo "OK: /kord mount exists" || echo "FAIL: not on new pod"
[ -L ~/.gnupg ] && echo "OK: ~/.gnupg is symlink" || echo "FAIL: ~/.gnupg not symlinked"
[ -L ~/.password-store ] && echo "OK: ~/.password-store is symlink" || echo "FAIL: not symlinked"
```

If any check fails, STOP — you're on the old pod.

### Step 2: Run verification checklist

| Check | Command | Expected |
|-------|---------|----------|
| Pass store | `pass ls kordinate` | Lists entries |
| GPG functional | `pass show kordinate/ssh/password` | Returns password |
| SSH keys | `ls ~/.ssh/id_ed25519` | File exists |
| Kordinate linked | `ls ~/.kord/KORD.json` | File exists |
| Beorn running | `curl -sf localhost:3100/health` | 200 OK |
| Caddy running | `curl -sf -H "Host: test.khaledkord.com" localhost:80 -o /dev/null -w "%{http_code}"` | 404 |
| Grafana reachable | `curl -sf localhost:80/api/health -H "Host: grafana.khaledkord.com"` | JSON response |
| Tailscale up | `tailscale status` | Connected |
| Cloudflare SSH | User confirms SSH via `ssh workstation` from external device | Connected |

Report results. If any critical check fails (pass, GPG, SSH, Cloudflare), STOP and report.

### Step 3: Cleanup (only if all checks pass)

SSH to control plane and execute:

```bash
# Delete old ingress deployment (already scaled to 0)
kubectl delete deploy ingress -n master 2>/dev/null || true
kubectl delete configmap ingress-caddyfile -n master 2>/dev/null || true

# Delete stale secrets
kubectl delete secret cloudflared-credentials -n prod 2>/dev/null || true

# Delete old PVCs
kubectl delete pvc workstation-home -n master

# Clean up migration artifacts on control plane
rm -rf /tmp/workstation-build /tmp/kord-migration.tar.gz /tmp/master-workstation.yaml /tmp/master-kord-storage.yaml
```

### Step 4: Final verification

```bash
kubectl get pvc -n master  # should show only 'kord' for workstation
kubectl get deploy -n master | grep -E 'ingress|workstation'  # should show only workstation
```

### Step 5: Report

Summary of what was verified, what was cleaned up, and current state.
