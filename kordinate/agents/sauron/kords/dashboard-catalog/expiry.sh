#!/bin/bash
exec "${KORDINATE_HOME:-$HOME/.kord}/lib/kord-expiry.sh" "$(cd "$(dirname "$0")" && pwd)"
