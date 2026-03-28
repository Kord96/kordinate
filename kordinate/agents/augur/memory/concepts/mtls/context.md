## Testing

Verify bidirectional certificate verification, rejection of invalid certs, and correct identity extraction.

### Unit Tests

- Present a valid client certificate and assert the server accepts the connection and extracts the correct identity (CN/SAN)
- Present no client certificate and assert the server rejects the connection
- Present a certificate signed by an untrusted CA and assert the handshake fails

### Integration Tests

- Establish an mTLS connection between two services and verify end-to-end request/response works
- Rotate the client certificate and verify the new certificate is accepted without service restart
- Verify that the server's CA bundle is scoped narrowly (rejects certificates from unexpected CAs)

### Expiry and Revocation Tests

- Present an expired certificate and assert the handshake is rejected
- If CRL/OCSP is configured, revoke a certificate and verify the server rejects it
- Test certificate renewal automation end-to-end: trigger renewal and verify the new cert is used

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

## Deployment

Coordinate certificate provisioning with service rollouts to avoid handshake failures during deployment.

### Rollout Implications

- New service versions must have valid client certificates provisioned before they attempt connections
- CA bundle updates must be deployed to servers before clients present certificates signed by the new CA
- Rolling updates should maintain at least one pod with a valid certificate at all times during transition
- Certificate rotation and service deployment should not overlap to isolate failure causes

### Pre-deploy Checklist

- Verify client and server certificates are provisioned and not expired in the target environment
- Confirm the CA bundle on the server includes the CA that signed the new client certificates
- Test mTLS handshake between the new service version and its dependencies in a staging environment
- Ensure plaintext fallback is disabled -- TLS enforcement is not optional

