#!/bin/bash
# Readiness probe — pod is NOT ready until externally accessible through Cloudflare.
# Kubernetes will not terminate the old pod during a rolling update until this passes.
#
# Checks:
# 1. sshd is listening on port 2222 (local prerequisite)
# 2. Cloudflare tunnel routes internet traffic to this pod (end-to-end proof)
#
# The curl returns HTTP 302 (Cloudflare Access redirect) if the tunnel works.
# Any HTTP response proves reachability. A connection error means the tunnel
# is not routing to us yet.

# sshd must be listening (port 2222 — Cloudflare tunnel target)
ss -tlnp | grep -q ':2222 ' || exit 1

# End-to-end: reach ourselves through Cloudflare from the public internet
curl -sf --max-time 10 -o /dev/null https://ssh.khaledkord.com 2>/dev/null || exit 1
