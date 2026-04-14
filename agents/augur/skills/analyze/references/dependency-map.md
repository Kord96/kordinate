# Dependency Mapping

Use this reference when refining component relationships, `external_dependencies`, and `state`.

## Internal Relationships

Use `depends_on` only for internal component-to-component relationships:

- imports
- direct calls
- event consumption
- state access across component boundaries

Do not use `depends_on` for incidental shared utilities.

## External Dependencies

Capture outside systems separately:

- HTTP APIs
- databases
- caches
- brokers
- object stores
- auth providers
- SMTP or messaging providers

If you did not write the system, it is usually external.

## Signals

Use:

- client libraries
- connection config
- manifests and deployment files
- ORM schemas
- broker, queue, and topic references

to identify external boundaries.
