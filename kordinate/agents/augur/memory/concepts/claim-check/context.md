## Testing

Verify the store-reference-retrieve lifecycle and that large payloads never travel through the message channel.

### Unit Tests

- Store a payload, assert a claim reference is returned, and retrieve the payload using the reference
- Verify the message sent through the channel contains only the claim reference, not the payload
- Test expiration: attempt to retrieve an expired claim and verify a clear error is returned

### Integration Tests

- Send a message with a large payload end-to-end: verify the producer stores, the message carries the reference, and the consumer retrieves
- Test with the actual blob/object store to verify serialization and access control

### Failure Injection

- Simulate store unavailability at retrieval time and verify the consumer surfaces the error rather than processing an incomplete message

## Deployment

Ensure the external store is available before deploying services that read or write claim references.

### Rollout Implications

- The blob/object store must be accessible from both old and new service versions during rollout
- Claim reference format changes require coordination between producer and consumer deployments
- Rolling restart may leave unretrieved claims in the store — ensure retention policy covers rollout duration

### Pre-deploy Checklist

- Verify external store connectivity and permissions from the target deployment environment
- Confirm claim TTL and cleanup policies will not expire payloads during extended rollouts

