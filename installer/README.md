# Installer

Bootstrap scripts for installing kordinate and setting up the environment.

| File | Purpose |
|------|---------|
| [kordinate-cli](kordinate-cli) | Bootstrap CLI — `init` (k3s + workstation), `join` (cluster node), `hydrate` (.mcp.json), `export`/`import` (credentials) |
| [setup-shell.sh](setup-shell.sh) | Idempotent shell setup — KORDINATE_HOME, PATH, tmux.conf, git-crypt worktree wrappers |
| [lib.sh](lib.sh) | Shared utilities — colored logging, kubectl resolver (local/in-cluster/SSH) |
| [auth-check.sh](auth-check.sh) | Credential initialization — GPG, pass store, GitHub auth, Tailscale, Claude credentials |
| [test/](test/) | Installation test suite |
