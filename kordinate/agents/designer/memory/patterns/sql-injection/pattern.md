---
description: SQL Injection anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# SQL Injection

## Recognition

How to identify this anti-pattern in code.

### Signatures

- String concatenation in SQL queries (`f"SELECT * FROM users WHERE id = {id}"`)
- `cursor.execute("... %s" % var)` using Python string formatting instead of parameterized queries
- No parameterized queries (`?` or `$1` placeholders absent from SQL strings)
- `raw()` or `extra()` with user input in Django ORM
- `String.format()` or `+` concatenation building SQL in Java
- `execute("SELECT ... WHERE name = '" + name + "'")`
- `$"SELECT ... WHERE id = {Request.Query["id"]}"` in C#
- Stored procedures built with `EXEC('SELECT ... ' + @param)`

### Confidence

- **high** -- f-string or string concatenation directly inside `cursor.execute()`, `db.query()`, or equivalent with user-controlled input
- **medium** -- SQL strings built with variable interpolation but input source is unclear
- **low** -- raw SQL used anywhere without visible parameterization, even if input may be trusted

## Impact

Database compromise through attacker-controlled query manipulation, enabling data exfiltration, modification, or deletion.

### Symptoms

- Unexpected query results or data leaks reported by users
- Database audit logs show malformed or suspicious queries
- Application crashes on inputs containing single quotes or SQL keywords
- Web application firewall (WAF) alerts on SQL keywords in request parameters
- Data integrity violations with no corresponding application-level writes

### Remediation

- Use parameterized queries exclusively (`cursor.execute("SELECT * FROM users WHERE id = %s", (id,))`)
- Use ORM query builders instead of raw SQL wherever possible
- Validate and sanitize all user input at the boundary (allowlist, not denylist)
- Run static analysis tools (Bandit, Semgrep) with SQL injection rules enabled
- Apply principle of least privilege to database accounts used by the application
