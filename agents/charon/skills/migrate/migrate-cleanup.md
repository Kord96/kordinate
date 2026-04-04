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
| Kordinate linked | `ls ~/.kord` | Directory exists |
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
