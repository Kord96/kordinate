---
description: OAuth2/OpenID Connect — deployment guidance
type: supplementary
---
## Deployment

Coordinate with IdP configuration and ensure secrets are rotated safely during rollouts.

### Rollout Implications

- Client secrets must be available in the new deployment before the old one is terminated (use Kubernetes Secrets, not env vars baked into images)
- JWKS key rotation at the IdP can invalidate cached keys -- ensure the service refetches JWKS on signature validation failure
- Redirect URI changes must be registered with the IdP before deploying the code that uses them
- Rolling deployments with mixed old/new pods must agree on the same token validation rules (audience, issuer, scopes)

### Pre-deploy Checklist

- Confirm client_id and client_secret are present in the secret store for the target environment
- Verify redirect_uri registered at the IdP matches the new deployment's callback URL
- Test OIDC discovery endpoint reachability from the deployment network
- Ensure JWKS cache TTL is short enough to pick up key rotations within the expected window
