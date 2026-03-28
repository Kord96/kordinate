## Testing

Verify handler ordering, correct delegation through the chain, and that unhandled requests reach a terminal handler.

### Unit Tests

- Send a request matching the first handler and assert it is processed without reaching subsequent handlers
- Send a request matching a middle handler and verify it passes through earlier handlers untouched
- Send a request matching no handler and verify it reaches the default/terminal handler

### Integration Tests

- Assemble the full chain via configuration and verify end-to-end request routing for each handler type
- Test dynamic chain modification: add or remove a handler at runtime and verify updated routing

### Failure Injection

- Inject an exception in a mid-chain handler and verify the chain either short-circuits with an error or skips to the next handler per policy

