# Dependency Analysis

Level 3 resource for the architect skill. Referenced from step 3 (map dependencies). Carries the full dependency mapping procedure.

## Module Discovery

| Language | Package markers | Notes |
|----------|----------------|-------|
| **Python** | `__init__.py`, top-level module dirs | `pyproject.toml`, `setup.py`, `requirements.txt` confirm Python |
| **JS/TS** | `package.json` workspaces, dirs with `index.ts`/`index.js` | Resolve workspace globs from `pnpm-workspace.yaml` or `package.json` `workspaces`. Respect `tsconfig.json` path aliases and `package.json` `exports` |
| **Go** | Dirs containing `.go` files | `go.mod` module path is the root; `internal/` dirs are private |

## Import Patterns

### Python
- `import X` and `from X import Y` where X is an internal module
- Relative imports: `from . import Y`, `from ..sub import Z`

### JS/TS
- `import ... from './...'` and `import ... from '../...'`
- `import ... from '@/...'` (path alias)
- `require('./...')`
- Resolve path aliases from `tsconfig.json` `paths` and `baseUrl` if present
- `tsconfig.json` `references` — each `{ "path": "../pkg" }` is a compile-time dependency between packages
- Monorepo workspace imports: `import ... from '@scope/package'`

### Go
- `import "module/path/internal/..."` where module path matches `go.mod`
- Multi-module repos: check for nested `go.mod` files

## External Service Detection

Scan for client library usage and ORM schema files. These are common starting points; adapt to what the project uses.

**ORM schema files**: `prisma/schema.prisma` (`provider`, `url`), `drizzle.config.ts`, `ormconfig.ts`, SQLAlchemy `metadata`, GORM `Open()`. These declare database providers and connections authoritatively.

| Category | Python | JS/TS | Go |
|----------|--------|-------|----|
| HTTP | `requests`, `httpx`, `aiohttp`, `urllib3` | `fetch`, `axios`, `got`, `node-fetch`, `ky` | `net/http`, `go-resty/resty` |
| gRPC | `grpc` channel/stub patterns | `@grpc/grpc-js` | `google.golang.org/grpc` |
| Message queues | `confluent_kafka`, `kafka`, `celery`, `pika` | `kafkajs`, `amqplib`, `bullmq` | `sarama`, `confluent-kafka-go` |
| SQL databases | `psycopg2`, `asyncpg`, `sqlalchemy` | `prisma`, `drizzle-orm`, `typeorm`, `knex`, `sequelize` | `database/sql`, `pgx`, `gorm.io/gorm` |
| NoSQL databases | `pymongo`, `motor`, `redis` | `mongoose`, `mongodb`, `ioredis`, `redis` | `go.mongodb.org/mongo-driver`, `go-redis/redis` |
| Cloud SDKs | `boto3`, `google.cloud`, `azure` | `@aws-sdk/*`, `@google-cloud/*` | `github.com/aws/aws-sdk-go-v2`, `cloud.google.com/go` |
| Object storage | `boto3` (S3), `minio` | `@aws-sdk/client-s3`, `minio` | `github.com/minio/minio-go` |
| NATS | `nats` | `nats` | `github.com/nats-io/nats.go` |
| Search | `elasticsearch`, `opensearchpy`, `meilisearch` | `@elastic/elasticsearch`, `meilisearch`, `typesense` | `olivere/elastic`, `meilisearch-go` |
| Auth/Identity | `authlib`, `jose`, `jwt` | `next-auth`, `passport`, `jsonwebtoken`, `@auth0/nextjs-auth0` | `golang-jwt/jwt`, `coreos/go-oidc` |
| Email/SMTP | `smtplib`, `sendgrid`, `mailgun` | `nodemailer`, `@sendgrid/mail` | `gomail`, `jordan-wright/email` |

## Infrastructure Scanning

Check k8s manifests at `manifests/`, `deploy/`, `k8s/`, `helm/`, `charts/`:
- PVCs, StatefulSets, ConfigMaps, Secrets, Service endpoints, init containers, sidecars
- Helm `values.yaml` for service references, resource names, and env injections
- Terraform/Pulumi files (`.tf`, `Pulumi.yaml`) at `infra/`, `terraform/`, `iac/` for provisioned resources (RDS, ElastiCache, S3 buckets, SQS queues)

If none found, note "No k8s/IaC manifests found" in module_graph.infrastructure.

## Inter-service Config Patterns

Scan config files for service references:

| Source file | Pattern | Indicates |
|-------------|---------|-----------|
| `.env`, `.env.example` | `*_URL`, `*_HOST`, `*_ENDPOINT`, `*_DSN` | Service dependency |
| `docker-compose.yml` | `depends_on`, `links`, service names in env | Container-level deps |
| `config.yaml`, `settings.py` | Connection strings, broker URLs, bucket names | Infrastructure deps |
| k8s manifests | `Service` references, `ExternalName`, `ConfigMap` data | Cluster-level deps |
| Helm `values.yaml` | Service URLs, hostnames, ports in values | Parameterized infra deps |
| Terraform `.tf` | `resource`, `data` blocks; `aws_db_instance`, `aws_sqs_queue`, etc. | Provisioned infra deps |
| `Pulumi.yaml`, `index.ts` | Pulumi resource constructors | Provisioned infra deps |

## Reverse Dependency Scanning (--reverse only)

Scan sibling directories (`~/`, `~/repos/`, `~/test-repos/`) for imports or references to this project:
- Language imports matching the project's module/package name
- Config references (env vars, URLs containing the project name)
- K8s manifest references (Service names, ExternalName entries)

Performance: scans all siblings. For repos with 10+ sibling projects, warn about context consumption.

## Module Graph Analysis

Build a directed graph: `A -> B` means A depends on B. Then flag:

- **Circular dependencies**: report the full cycle path. Cap detection at cycles of length 5 or fewer.
- **Hub modules**: imported by >50% of other modules. These are coupling hotspots.

## Concept Vocabulary

Use these exact values in the architecture.yaml output:

**For external_dependencies concept field:** `http-api`, `message-broker`, `database`, `cache`, `object-store`, `dns`, `smtp`, `nfs`, `grpc`, `auth-provider`, `cdn`

**For state concept field:** `relational-db`, `document-store`, `embedded-olap`, `cache`, `object-store`, `message-broker`, `filesystem`, `in-memory`

## Edge Cases

| Marker | Handling |
|--------|----------|
| `pnpm-workspace.yaml`, `package.json` `workspaces`, `go.work` | Monorepo — treat workspace members as modules |
| `vendor/`, `third_party/`, `_vendor/` | Vendored deps — skip for module discovery, record imports as external |
| `.gitmodules` | Git submodules — treat submodule dirs as external |
| `gen/`, `generated/`, `proto/gen/`, `__generated__/` | Build-generated code — note but do not trace |
