# Shared Protocols

Team-wide protocols loaded by every agent on `/boot`. These define universal rules that all agents follow.

| Protocol | Purpose |
|----------|---------|
| [auth-protocol.md](auth-protocol.md) | Authenticate before guarded operations (kubectl, Grafana, git push) |
| [credentials-protocol.md](credentials-protocol.md) | All credentials go through the `pass` store — never hardcoded |
| [memory-protocol.md](memory-protocol.md) | Save insights to memory before finishing a task |
| [delegation-protocol.md](delegation-protocol.md) | Delegate work to pod agents through the job-router |
