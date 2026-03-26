---
description: Insecure Deserialization anti-pattern
curated: true
scope: global
preloaded: none
---
# Insecure Deserialization

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
