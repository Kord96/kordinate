# Troubleshooting

- **ErrImagePull**: Manifests must use full registry path (`<registry>/<image>:<tag>`), not bare image names
- **CrashLoopBackOff**: Check `kubectl logs <pod> -n <ns>` — missing PVC data, config errors, dependency not ready
- **Pending pods**: Check `kubectl describe pod <pod> -n <ns>` — node scheduling or PVC binding issues
