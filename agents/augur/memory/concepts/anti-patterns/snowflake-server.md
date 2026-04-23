---
kind: concept
name: snowflake-server
signatures: {}
type: anti-pattern
abstraction: []
scope: backend
status: supporting
family: anti-patterns
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Hand-configured servers with no Infrastructure as Code (IaC) backing them
- `ssh` commands in deploy scripts: `ssh prod-server 'sudo systemctl restart app'`
- Undocumented manual steps required to set up or update a server
- Works-on-my-machine issues that cannot be reproduced elsewhere
- Config files edited directly on the server via `vim`, `nano`, or `sed` in ad-hoc scripts
- Server setup instructions that include "ask Dave, he knows how this one is configured"
- No Terraform, Ansible, Puppet, Chef, or equivalent in the repository

### Confidence

- **high** -- deploy process involves SSH into a server and running manual commands, with no IaC in the repo
- **medium** -- partial IaC exists but some servers have manual tweaks applied outside of it
- **low** -- IaC exists but the actual server state has drifted and no one has reconciled it

## Impact

Unreproducible environments that cannot be rebuilt, audited, or scaled, turning every server into a unique artifact that the team is afraid to touch.

### Symptoms

- Disaster recovery is impossible or takes days because nobody knows the exact server configuration
- Scaling requires manually setting up each new server by hand
- Security patches are applied inconsistently across servers
- Configuration drift: nominally identical servers behave differently
- Knowledge of how to configure the server lives in one person's head

### Remediation

- Adopt Infrastructure as Code: define all server configuration in Terraform, Ansible, or equivalent
- Treat servers as cattle, not pets: any server should be replaceable by re-running the IaC
- Use immutable infrastructure: build machine images (AMI, Docker) and deploy new instances rather than mutating existing ones
- Store all configuration in version control and apply it through CI/CD pipelines
- Implement configuration drift detection that alerts when a server diverges from its declared state

See also: infrastructure-as-code, immutable-infra patterns

### Relationship To Other Concepts

- Related to [infrastructure-as-code](/concepts/infrastructure-as-code) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `snowflake-server` when the important observation is this specific recurring architectural failure mode within a backend service, storage, or server-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
