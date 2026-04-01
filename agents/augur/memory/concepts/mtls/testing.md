---
description: Mutual TLS — testing guidance
type: supplementary
---
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
