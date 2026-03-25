#!/bin/bash
# Generate master manifests from profile/config.yaml + gateway-ips.yaml.
# Wrapper around generate-config.py for convenience.
#
# Usage:
#   ./generate.sh              # write to base/
#   ./generate.sh --dry-run    # print to stdout
set -euo pipefail
cd "$(dirname "$0")"
exec python3 generate-config.py "$@"
