# Testing

- Test that the singleton can be reset or replaced in tests — no global state leaking between test cases
- Verify thread-safe initialization by accessing the singleton from multiple threads concurrently
- Test lifecycle management: creation on first access, optional teardown for cleanup
- Assert that subclassing is either properly supported or explicitly prevented
- Use dependency injection in tests to swap the singleton with a test double
- Verify that the singleton does not accumulate mutable state that makes tests order-dependent
- Test that singleton initialization handles failure gracefully (no partially initialized instance cached)

