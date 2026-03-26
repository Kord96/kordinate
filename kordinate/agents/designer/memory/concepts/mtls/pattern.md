---
description: Mutual TLS architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [security, infrastructure]
---
# Mutual TLS

## Recognition

How to identify this pattern in code.

### Signatures

- Client certificate configuration (`--cert`, `--key` flags, `tls.Certificate` structs)
- Server requiring client certs: `ssl_verify_client on` (nginx), `tls.Config{ClientAuth: tls.RequireAndVerifyClientCert}` (Go)
- CA bundle configuration for validating client certificates (`ClientCAs`, `ssl_client_certificate`)
- X.509 client certificate parsing and subject/SAN extraction from verified connections
- Certificate chain validation with intermediate CAs
- Service-to-service certificate provisioning (SPIFFE, cert-manager, Vault PKI)
- TLS termination configuration distinguishing between external TLS and internal mTLS
- Libraries: `crypto/tls` (Go), `ssl` (Python), `tls` (Node), OpenSSL bindings

### Confidence

- **high** -- Server configured to require and verify client certificates, CA bundle loaded, and client services present certificates with subject/SAN-based identity
- **medium** -- TLS configuration with client certificate fields present but `ClientAuth` set to optional or verification mode unclear
- **low** -- Certificate files referenced in config but no explicit mutual verification (could be standard one-way TLS)

## Architecture

Look for bidirectional certificate verification where both client and server authenticate each other via X.509 certificates.

### Review Checklist

- Server requires client certificates (not optional/request-only mode)
- CA bundle is scoped narrowly (only trusted CAs for expected clients, not the system CA store)
- Certificate identity (CN or SAN) is checked after TLS handshake for authorization decisions
- Certificates have reasonable validity periods with automated rotation before expiry
- Certificate revocation is handled (CRL or OCSP stapling)
- Plaintext fallback is impossible (TLS is enforced, not optional)

### Anti-patterns

- Using the system-wide CA store to validate client certificates (any publicly-trusted cert would pass)
- No certificate rotation -- long-lived certificates with manual renewal processes
- Skipping client identity verification after handshake (mTLS authenticates but code never checks who)
- Mixing mTLS and non-mTLS traffic on the same port without clear enforcement boundaries
