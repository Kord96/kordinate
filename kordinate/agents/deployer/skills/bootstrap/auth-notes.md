# Bootstrap Authentication

Level 3 resource for the bootstrap skill.

## Bootstrap Auth

For writes to master namespace (excluding workstation resources):

1. `cp profile/locks/deployer /tmp/.deployer-auth`
2. `cp profile/locks/deployer /tmp/.bootstrap-auth`
3. Run SSH + kubectl commands targeting master namespace
4. `rm /tmp/.bootstrap-auth /tmp/.deployer-auth`

## Always Blocked

Even with bootstrap auth:
- `kubectl apply -k master/`
- `kubectl apply -f workstation.yaml`
- Any write command containing "workstation"
- `kubectl drain/cordon`

## Cluster RBAC

On clusters, default `KUBECONFIG` is readonly. Use admin kubeconfig:

```
ssh <cluster> "KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl apply ..."
```

Both layers enforce deployer-only write access: local hook (primary) + cluster RBAC (defense in depth).
