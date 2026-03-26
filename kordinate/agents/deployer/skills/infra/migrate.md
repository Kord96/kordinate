Prepare workstation migration manifests and handover file.

Does NOT perform the migration — generates the artifacts for external execution.

**Input**: $ARGUMENTS (optional: target cluster, e.g. `home` or `vandc`)

## Procedure

1. Read current workstation config from profile/config.yaml
2. Read current workstation manifest from agents/deployer/skills/infra/manifests/master-workstation.yaml
3. Detect migration type:
   - **PVC migration**: manifest references a PVC that doesn't exist on the cluster yet
   - **Image update**: Dockerfile has changes or image tag changed
   - **Config update**: manifest changed but image is same
   - **Cluster migration**: target cluster differs from current
4. Generate the migration handover file at agents/deployer/memory/dynamic/workstation-handover.md

## Handover File Template

The handover file contains step-by-step instructions for external execution.
All kubectl commands run from the cluster control plane via SSH.

### Phase 0: Pre-checks

```bash
# Verify Cloudflare SSH works as backup path (from a remote device)
ssh -o ProxyCommand="cloudflared access ssh --hostname %h" claude@ssh.khaledkord.com

# Verify pass store entries required by entrypoint
pass show kordinate/ssh/password
pass show kordinate/tailscale/auth_key_workstation
pass show kordinate/cloudflare/tunnel_token
```

### Phase 1: Extract data from running pod

The old `workstation-home` PVC is RWO and currently mounted by the running pod.
It cannot be mounted by a second pod. Extract data from inside the running pod.

```bash
# From INSIDE the running workstation (via SSH):
tar czf /tmp/kord-migration.tar.gz \
  -C /home/claude \
  .password-store .ssh .gnupg .kord \
  kordinate

# Copy to control plane
scp /tmp/kord-migration.tar.gz kkord@<CONTROL_PLANE_IP>:/tmp/
```

### Phase 2: Build and import workstation image

```bash
# Copy build context to control plane
scp -r kordinate/agents/deployer/skills/infra/images/workstation/ kkord@<CONTROL_PLANE_IP>:/tmp/workstation-build/

# SSH to control plane
ssh kkord@<CONTROL_PLANE_IP>

# Tag old image as backup
sudo k3s ctr images tag docker.io/library/workstation:latest docker.io/library/workstation:pre-migration

# Build new image
cd /tmp/workstation-build && docker build -t workstation:latest .

# Import into k3s
docker save workstation:latest | sudo k3s ctr images import -
```

### Phase 3: Create kord PVC and migrate data

```bash
# Substitute STORAGE_CLASS and apply (on control plane)
sed 's/STORAGE_CLASS/longhorn/' master-kord-storage.yaml | sudo kubectl apply -n master -f -

# Wait for init job
sudo kubectl wait -n master --for=condition=Complete job/kord-init --timeout=120s

# Extract migration data into kord PVC via a temporary pod
sudo kubectl run kord-migrate --rm -it --restart=Never -n master \
  --overrides='{
    "spec": {
      "containers": [{
        "name": "migrate",
        "image": "alpine",
        "command": ["/bin/sh", "-c",
          "echo Extracting...; tar xzf /tmp/data.tar.gz -C /tmp/extract; echo Copying pass store...; cp -a /tmp/extract/.password-store/* /kord/pass/ 2>/dev/null; cp -a /tmp/extract/.password-store/.gpg-id /kord/pass/; echo Copying GPG keys...; cp -a /tmp/extract/.gnupg/* /kord/gnupg/ 2>/dev/null; cp -a /tmp/extract/.gnupg/.* /kord/gnupg/ 2>/dev/null; echo Copying SSH keys...; cp -a /tmp/extract/.ssh/* /kord/ssh/ 2>/dev/null; echo Copying kordinate runtime...; cp -a /tmp/extract/.kord/* /kord/kordinate/ 2>/dev/null; cp -a /tmp/extract/.kord/.* /kord/kordinate/ 2>/dev/null; echo Copying projects...; cp -a /tmp/extract/kordinate /kord/projects/ 2>/dev/null; chmod 700 /kord/pass /kord/ssh /kord/gnupg; chown -R 1000:1000 /kord/; echo Done; ls -la /kord/"
        ],
        "volumeMounts": [
          {"name": "kord", "mountPath": "/kord"},
          {"name": "data", "mountPath": "/tmp/data.tar.gz", "subPath": "kord-migration.tar.gz"}
        ]
      }],
      "volumes": [
        {"name": "kord", "persistentVolumeClaim": {"claimName": "kord"}},
        {"name": "data", "hostPath": {"path": "/tmp", "type": "Directory"}}
      ]
    }
  }' -- /bin/sh

# Verify data
sudo kubectl run kord-verify --rm -it --restart=Never -n master \
  --overrides='{
    "spec": {
      "containers": [{
        "name": "verify",
        "image": "alpine",
        "command": ["/bin/sh", "-c", "ls -la /kord/ /kord/pass/ /kord/ssh/ /kord/gnupg/ /kord/kordinate/ /kord/projects/"],
        "volumeMounts": [{"name": "kord", "mountPath": "/kord"}]
      }],
      "volumes": [{"name": "kord", "persistentVolumeClaim": {"claimName": "kord"}}]
    }
  }' -- /bin/sh
```

### Phase 4: Apply workstation manifest

```bash
# Update the cloudflared-tunnel secret with actual token (not MUST_BE_SET)
TUNNEL_TOKEN="<from pass show kordinate/cloudflare/tunnel_token>"
sudo kubectl create secret generic cloudflared-tunnel -n master \
  --from-literal=TUNNEL_TOKEN="$TUNNEL_TOKEN" \
  --dry-run=client -o yaml | sudo kubectl apply -f -

# Apply Caddyfile ConfigMap + Deployment (substitute REGISTRY and STORAGE_CLASS)
sed 's/REGISTRY\///' master-workstation.yaml | sed 's/STORAGE_CLASS/longhorn/' \
  | sudo kubectl apply -n master -f -

# Watch the rolling update — new pod starts before old terminates
sudo kubectl rollout status deploy/workstation -n master --timeout=300s

# Check all 3 containers are running
sudo kubectl get pods -n master -l app=workstation
```

### Phase 5: Verify new pod is accessible

During rolling update, both pods connect to the Cloudflare tunnel.
Verify the new pod works before the old one terminates.

```bash
# From a remote device — SSH should work through either pod
ssh -o ProxyCommand="cloudflared access ssh --hostname %h" claude@ssh.khaledkord.com

# Inside the workstation, verify:
ls /kord/                         # should show pass/ gnupg/ ssh/ kordinate/ projects/
ls -la ~/.password-store          # should be symlink to /kord/pass
ls -la ~/.gnupg                   # should be symlink to /kord/gnupg
pass show kordinate/ssh/password  # should work (GPG + pass functional)
which kord-hydrate                # should be in PATH
```

If verification fails:
```bash
sudo kubectl rollout undo deploy/workstation -n master
```

### Phase 6: Cleanup (after verification)

```bash
# Delete old ingress deployment (already scaled to 0, superseded by sidecars)
sudo kubectl delete deploy ingress -n master
sudo kubectl delete configmap ingress-caddyfile -n master

# Delete stale K8s secret
sudo kubectl delete secret cloudflared-credentials -n prod

# Keep old PVCs for 24-48 hours as safety net, then:
sudo kubectl delete pvc workstation-home -n master
# Note: kord-shared may still be referenced — check before deleting

# Clean up build artifacts
rm -rf /tmp/workstation-build /tmp/kord-migration.tar.gz
```

### Post-migration checklist

- [ ] SSH works via Cloudflare (`ssh workstation` from remote device)
- [ ] SSH works via Tailscale
- [ ] Grafana accessible at grafana.khaledkord.com
- [ ] pass store works (`pass ls kordinate`)
- [ ] tmux auto-attaches to 0-general window 0 on SSH login
- [ ] kordinate framework linked (`ls ~/.kord/`)
- [ ] Beorn MCP server running (`curl localhost:3100/health`)
- [ ] All agents responsive (`/boot`)
- [ ] Run `auth-check.sh` to verify all credentials
- [ ] Run `claude login` if needed
- [ ] Old ingress deployment deleted
- [ ] Old PVCs deleted (after 24-48 hour safety window)

## Notes

- The handover file is deployer's dynamic memory so the new workstation's deployer instance can read it via /boot
- The human applies manifests externally because migrating from inside the pod being replaced is unsafe
- Rolling update ensures zero-downtime: new pod starts before old pod terminates
- Both pods connect to the same Cloudflare tunnel during overlap — SSH works through either
- Tailscale will briefly conflict during overlap (new pod deletes old workstation node) — Cloudflare SSH is unaffected
- The home cluster has no container registry — images must be imported directly into k3s containerd
- workstation-home PVC is RWO — data must be extracted from inside the running pod, not mounted by a migration pod
