# Authentication

Kubectl write operations and image builds are protected by `guard-kubectl.sh`. Only the deployer can bypass it.

## Standard auth

For writes to any namespace except master:

1. `cp <lock> /tmp/.deployer-auth` (lock path from paths.json)
2. Run SSH + kubectl/docker commands or Redis MCP tools
3. `rm /tmp/.deployer-auth`

## Bootstrap auth

For writes to master namespace (excluding workstation resources):

1. `cp <lock> /tmp/.deployer-auth`
2. `cp <lock> /tmp/.bootstrap-auth`
3. Run SSH + kubectl commands targeting master namespace
4. `rm /tmp/.bootstrap-auth /tmp/.deployer-auth`

Bootstrap auth is only used by `/deployer:bootstrap deploy-master`.

## Always blocked

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
