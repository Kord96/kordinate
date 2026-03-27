---
description: Instructs agents to authenticate before guarded operations
preloaded: all
curated: true
scope: global
---

Before performing guarded operations (writing to protected files, kubectl, Grafana):

```
/authenticate
```

This copies your lock file. Remove it when done. Authenticate once per task, not per operation.
