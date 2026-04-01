---
description: Mutual TLS — monitoring guidance
type: supplementary
---
## Monitoring

Track certificate health, handshake failures, and expiry to prevent authentication outages.

### Key Metrics

- `tls_handshake_failures_total` (counter) — failed mTLS handshakes by reason (expired cert, unknown CA, no client cert)
- `certificate_expiry_seconds` (gauge) — time remaining until the client or server certificate expires
- `tls_connections_active` (gauge) — current number of established mTLS connections
- `certificate_rotation_total` (counter) — successful certificate rotations

### Alerts

- Certificate expiring within the rotation safety window (e.g., 7 days before expiry)
- Handshake failure rate spike (new deployment presenting wrong cert or CA mismatch)
- Any plaintext connections on ports that should enforce mTLS
- Certificate rotation failure (automated renewal did not complete)
