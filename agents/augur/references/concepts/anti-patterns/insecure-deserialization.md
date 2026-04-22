---
kind: concept
name: insecure-deserialization
signatures: {}
source:
  memory_concept: memory/catalog/concepts/insecure-deserialization.md
type: anti-pattern
abstraction: []
scope: backend
status: supporting
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `pickle.loads()` on untrusted or network-received input
- `eval()` or `exec()` used to parse data or configuration
- `yaml.load()` without `Loader=SafeLoader` (defaults to unsafe loader in older PyYAML)
- `unserialize()` in PHP on user-supplied data
- `JSON.parse()` on user input without schema validation
- `marshal.load()` or `shelve.open()` on untrusted files
- Java `ObjectInputStream.readObject()` on network streams
- `jsonpickle.decode()` on external input
- `__reduce__` or `__setstate__` methods in classes used with pickle

### Confidence

- **high** -- `pickle.loads()`, `eval()`, or `exec()` called directly on request body, file upload, or message queue payload
- **medium** -- `yaml.load()` without explicit SafeLoader, or `unserialize()` on data from a database column populated by users
- **low** -- `JSON.parse()` on external input without validation, or deserialization libraries used but input provenance is unclear

## Impact

Remote code execution through crafted payloads that exploit deserialization to run arbitrary commands on the server.

### Symptoms

- Unexpected process spawning or outbound network connections from the application
- Crash or exception traces referencing deserialization methods with malformed input
- Security scanner alerts for unsafe deserialization functions
- Unexplained file system modifications in the application directory
- Audit logs showing operations the application should not perform

### Remediation

- Replace `pickle` with JSON or MessagePack for data interchange
- Replace `yaml.load()` with `yaml.safe_load()` or `yaml.load(data, Loader=SafeLoader)`
- Never use `eval()` or `exec()` on external input; use `ast.literal_eval()` for Python literals
- Validate deserialized data against a schema (Pydantic, JSON Schema, dataclasses)
- Apply allowlist-based type checking before deserialization in Java (`ObjectInputFilter`)

### Relationship To Other Concepts

- Related to [input-validation](/concepts/input-validation) because schema checks and allowlists are one defense layer against unsafe payload interpretation.
- Related to [sql-injection](/concepts/sql-injection) as another data-boundary security failure where untrusted input controls dangerous behavior.
- Related to [route-guard](/concepts/route-guard) because deserialization safety often sits near other boundary-enforcement mechanisms, though it addresses payload interpretation rather than access control.

### Boundary

Use `insecure-deserialization` when untrusted serialized input can trigger unsafe object construction, code execution, or dangerous side effects.

Do not use it for ordinary parsing bugs or validation gaps that do not involve unsafe deserialization semantics.
