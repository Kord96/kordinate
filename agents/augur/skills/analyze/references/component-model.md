# Component Model

Use this reference when refining `atlas.json`.

## Include As Components

- runtime entrypoints
- business-domain services and workflows
- internal libraries with clear architectural responsibility
- client code you own that encapsulates an external dependency

## Do Not Model As Components

- generic utilities
- config-only modules
- logging wrappers
- third-party systems like Kafka, Redis, Postgres, MinIO, SMTP providers

Represent outside systems in `external_dependencies` or `state`, not as components.

## Component Fields

Each component should have:

- `id`
- `name`
- `type`
- `description`
- `modules`
- `depends_on`

Keep `depends_on` for real internal component relationships only.

## Grouping

- assign every component to exactly one top-level group
- prefer 3-5 groups
- group by runtime boundary or architectural concern, not by folder naming
- merge tiny groups before inventing more categories
