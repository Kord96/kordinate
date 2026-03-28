# Testing

- Run static analysis (Bandit, Semgrep) with SQL injection rules to flag string concatenation in queries
- Test all user-facing inputs with SQL injection payloads (`' OR 1=1 --`, `'; DROP TABLE users;--`)
- Verify that all SQL execution paths use parameterized queries by inspecting generated SQL in tests
- Test ORM `raw()` and `extra()` calls to confirm user input is never interpolated into the SQL string
- Fuzz test query parameters with special characters (quotes, semicolons, comment markers)
- Assert that database accounts used by the application have least-privilege permissions
- Run integration tests with a real database to verify parameterized queries execute correctly
- Verify that error messages do not leak database schema information to the caller

