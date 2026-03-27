# Language & Service Patterns

Reference material for `/map-dependencies`. Adapt based on what the project actually uses.

## Module Discovery

| Language | Package markers | Notes |
|----------|----------------|-------|
| **Python** | `__init__.py`, top-level module dirs | `pyproject.toml`, `setup.py`, `requirements.txt` confirm Python |
| **JS/TS** | `package.json` workspaces, dirs with `index.ts`/`index.js` | Resolve workspace globs (`packages/*`, etc.) from `pnpm-workspace.yaml` or `package.json` `workspaces` to get member list. Respect `tsconfig.json` path aliases and `package.json` `exports` |
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
- `tsconfig.json` `references` -- each `{ "path": "../pkg" }` is a compile-time dependency between packages
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

## Inter-service Config Patterns

When scanning config files (step 7), look for these patterns:

| Source file | Pattern | Indicates |
|-------------|---------|-----------|
| `.env`, `.env.example` | `*_URL`, `*_HOST`, `*_ENDPOINT`, `*_DSN` | Service dependency |
| `docker-compose.yml` | `depends_on`, `links`, service names in env | Container-level deps |
| `config.yaml`, `settings.py` | Connection strings, broker URLs, bucket names | Infrastructure deps |
| k8s manifests | `Service` references, `ExternalName`, `ConfigMap` data | Cluster-level deps |
| Helm `values.yaml` | Service URLs, hostnames, ports in values | Parameterized infra deps |
| Terraform `.tf` | `resource`, `data` blocks; `aws_db_instance`, `aws_sqs_queue`, `aws_s3_bucket`, etc. | Provisioned infra deps |
| `Pulumi.yaml`, `index.ts` | Pulumi resource constructors | Provisioned infra deps |

## Edge Case Markers

When scanning, check for these and adjust behavior per SKILL.md Edge Cases:

| Marker | Indicates |
|--------|-----------|
| `pnpm-workspace.yaml`, `package.json` `workspaces`, `go.work` | Monorepo -- treat workspace members as modules |
| `vendor/`, `third_party/`, `_vendor/` | Vendored deps -- skip for module discovery |
| `.gitmodules` | Git submodules -- treat submodule dirs as external |
| `gen/`, `generated/`, `proto/gen/`, `__generated__/` | Build-generated code -- note but do not trace |
