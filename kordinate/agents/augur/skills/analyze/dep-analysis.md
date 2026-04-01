# Dependency Analysis

Level 3 resource for the analyze skill. Referenced from step 2 (dependencies concern). Carries the full dependency mapping procedure.

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

Scan for client library usage and ORM schema files. For each service found, record: type (use concept vocabulary below), technology, target (from connection strings, env vars, or config if visible), which files use it, and config source.

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
| LLM/AI APIs | `openai`, `anthropic`, `google-genai`, `google.generativeai`, `groq`, `together`, `replicate`, `huggingface_hub`, `cohere`, `mistralai` | `openai`, `@anthropic-ai/sdk`, `@google/generative-ai`, `groq-sdk`, `together-ai`, `replicate`, `cohere-ai` | `github.com/sashabaranov/go-openai`, `github.com/liushuangls/go-anthropic` |
| Vector stores | `chromadb`, `pinecone`, `qdrant-client`, `weaviate-client`, `milvus`, `lancedb`, `turbopuffer`, `pgvector` | `@pinecone-database/pinecone`, `chromadb`, `@qdrant/js-client-rest`, `weaviate-ts-client` | `github.com/qdrant/go-client`, `github.com/pinecone-io/go-pinecone` |
| Observability | `langfuse`, `datadog`, `newrelic`, `opentelemetry`, `honeycomb`, `lightstep` | `langfuse`, `dd-trace`, `newrelic`, `@opentelemetry/*`, `@honeycombio/opentelemetry-node` | `gopkg.in/DataDog/dd-trace-go.v1`, `go.opentelemetry.io/otel` |
| Error tracking | `sentry-sdk`, `bugsnag`, `rollbar`, `airbrake` | `@sentry/node`, `@bugsnag/js`, `rollbar` | `github.com/getsentry/sentry-go`, `github.com/bugsnag/bugsnag-go` |
| Metrics | `prometheus_client`, `statsd`, `datadog` | `prom-client`, `hot-shots` (StatsD) | `github.com/prometheus/client_golang` |

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

Build a directed graph: `A -> B` means A depends on B. Respect `--depth N` if set — stop traversal at depth N. Collapse leaf modules into their parent where a parent has only leaf children. Then flag:

- **Circular dependencies**: report the full cycle path. Cap detection at cycles of length 5 or fewer — if longer cycles exist, note their presence and move on.
- **Hub modules**: imported by >50% of other modules. These are coupling hotspots.

## Concept Vocabulary

Use these exact values in the architecture.yaml output:

**For external_dependencies concept field:** `http-api`, `message-broker`, `database`, `cache`, `object-store`, `dns`, `smtp`, `nfs`, `grpc`, `auth-provider`, `cdn`

**For state concept field:** `relational-db`, `document-store`, `embedded-olap`, `cache`, `object-store`, `message-broker`, `filesystem`, `in-memory`

## Edge Cases

- **Monorepo with shared packages**: If the project root contains workspace config (`pnpm-workspace.yaml`, `package.json` with `workspaces`, `go.work`), resolve the workspace member globs to directories and treat each member as a module. For JS/TS also check `tsconfig.json` `references` as an authoritative dependency declaration between packages. Shared packages (e.g., `packages/shared/`, `libs/common/`) are internal dependencies — graph them like any other module but tag them as `shared` in the role field.
- **Vendored dependencies**: Skip `vendor/`, `third_party/`, `_vendor/` directories entirely for module discovery and import tracing. They are not project code. If a vendored package is imported, record the import target (e.g., `github.com/foo/bar`) as an external dependency, not an internal module.
- **Git submodules**: Check for `.gitmodules`. Submodule directories contain external code — do not traverse them for internal module discovery. If project source imports from a submodule path, record it as an external dependency with a note "(git submodule)".
- **Build-generated code**: Skip directories matching `gen/`, `generated/`, `proto/gen/`, `__generated__/`. If imports reference generated code, note the import but do not trace into the generated files.
- **Unsupported languages**: If no recognizable language markers are found, note what was found. The dependency analysis supports Python, JS/TS, and Go; other languages get best-effort import tracing.
