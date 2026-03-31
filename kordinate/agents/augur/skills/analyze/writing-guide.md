# Writing Guide

Level 3 resource for the analyze skill. Referenced whenever augur writes prose — story summaries, journey descriptions, observation findings, rationale explanations, report text. One voice across all output.

## Core Rule

**State facts about code, not facts about the document.** Every sentence should tell the reader something about the system, not about what they're reading.

Bad: "This section describes the authentication flow."
Good: "**auth-service** validates JWT tokens before forwarding requests to downstream services."

Bad: "The following components are involved in data persistence."
Good: "**order-service** writes to PostgreSQL; **cache-layer** reads from Redis with a 5-minute TTL."

## Voice

**Name things.** Use component names (bold), file paths, function names, library names. Vague references ("the service", "the database") waste the reader's time.

**State relationships.** Don't just list components — say what connects them. "A calls B" is better than "A and B exist."

**Explain decisions in one clause.** Don't write a paragraph about why something exists. Append it: "Uses Redis for sessions — the database was a bottleneck under load."

**Lead with action.** Start sentences with what happens, not with context.

Bad: "When a user submits a login request, the system first checks..."
Good: "**api-gateway** forwards login requests to **auth-service**, which validates credentials against **user-db**."

## Length

All prose should be as short as possible while still stating facts.

| Context | Target | Max |
|---------|--------|-----|
| Story summary | 50-80 words | 100 words |
| Journey description | 1 sentence | 2 sentences |
| Observation finding | 1 sentence | 1 sentence |
| Rationale decision | 1 sentence | 2 sentences |
| Rationale trade_offs | 1 sentence | 2 sentences |
| Rationale alternatives | 1 sentence each | 1 sentence each |
| Report purpose | 1 sentence | 1 sentence |

If you're over the target, you're probably describing the document instead of stating facts. Cut the meta-text.

## Formatting

- **Bold** component names: `**auth-service**` — must resolve to an atlas node ID
- Em dashes (—) not double hyphens
- Periods to end sentences, not semicolons
- Every sentence starts with a capital letter
- No headings inside summaries — they're single paragraphs
- No bullet lists inside summaries — use sentences

## Text Quality

These rules apply to ALL text augur produces — summaries, observations, rationale, descriptions, journey overviews.

**Capitalization:** Every sentence starts with a capital letter. Component names in **bold** keep their kebab-case inside the bold markers but the sentence itself starts capitalized. YES: "**message-producer** scans NFS..." NO: "message-producer scans NFS..."

**Spacing:** One space after periods. Two newlines between paragraphs (in multi-paragraph summaries). No trailing whitespace. No double spaces.

**Punctuation:** End every sentence with a period. Observations end with a period. Rationale fields end with a period. Anchor descriptions end with a period.

**Clarity over cleverness:** Short sentences (15-25 words). One idea per sentence. If a sentence has more than one comma, split it. Technical terms are fine — jargon is not. Name the specific technology, don't say "the framework" or "the tool."

**Descriptions in atlas:** Component descriptions are one sentence, max 30 words. Group descriptions are one sentence, max 20 words. The purpose field is one sentence, max 15 words. External dependency descriptions are one sentence.

## Examples by Context

### Story summary (structure)

Good:
> **api-gateway** routes external traffic to **auth-service**, **user-service**, and **order-service**. All three share a PostgreSQL instance through separate schemas — no cross-service queries. **auth-service** owns JWT validation and issues tokens consumed by the other two via a shared middleware library.

Bad:
> This story covers the API layer of the application. It includes three services that handle authentication, user management, and order processing. They connect to a shared database and use JWT tokens for security.

### Story summary (flow)

Good:
> A checkout request hits **api-gateway**, which validates the JWT and forwards to **order-service**. **order-service** reserves inventory via **inventory-service**, charges the card through **payment-adapter** (Stripe), and writes the order to PostgreSQL. Failure at any step triggers a compensating transaction via the saga coordinator.

Bad:
> This flow describes how the checkout process works from start to finish. The request goes through several services before completing the order.

### Story summary (failure cascade)

Good:
> When Stripe returns 503, **payment-adapter** retries 3 times with exponential backoff. If all retries fail, the saga coordinator rolls back the inventory reservation in **inventory-service**. No circuit breaker exists — a sustained Stripe outage blocks all checkouts indefinitely.

Bad:
> This story describes what happens when the payment system fails. The failure cascades through the system and affects the checkout process.

### Observation finding

Good: "**order-service** queries PostgreSQL directly from route handlers, bypassing the repository layer in 8 of 23 endpoints."

Bad: "There is a potential architectural concern where some endpoints access the database directly."

### Rationale

Good:
- decision: "Session tokens stored in Redis, not PostgreSQL"
- context: "Login endpoint was the bottleneck — 200ms p99 from PostgreSQL session table scans"
- trade_offs: "10x faster session validation; added Redis as a single point of failure for auth"
- alternatives: ["JWT-only (stateless) — rejected because token revocation requires a blocklist, which needs Redis anyway"]

Bad:
- decision: "We decided to use Redis for caching"
- context: "Performance was an issue"
- trade_offs: "Better performance but more complexity"
- alternatives: ["Could have used memcached"]

### Journey description

Good: "Trace a request from the API gateway through auth, order processing, and payment — then see what breaks when Stripe goes down."

Bad: "This journey covers the backend request flow and related failure modes."

## Analogies

Use analogies sparingly and only when they make a concrete concept clearer. An analogy must be **grounded** — it should map to something specific in the code, not decorate a vague description.

**Good analogies** (grounded in code behavior):
- "**order-service** orchestrates checkout like a saga — each step has a compensating rollback if the next fails." (Maps to actual saga pattern in the code)
- "The plugin system works like Unix pipes — each processor reads stdin, transforms, writes stdout." (Maps to actual ProcessorPool dispatch model)

**Bad analogies** (decorative, not grounded):
- "The architecture is like a city with roads connecting buildings." (Maps to nothing specific)
- "Redis acts as the system's short-term memory." (Sounds nice but obscures what Redis actually stores and who reads/writes it)

**Rules:**
- Only use an analogy if it maps to a real mechanism in the code
- The analogy must survive the question "which file/function implements this?"
- One analogy per story is enough. Two is too many.
- Never use an analogy as a substitute for naming components and stating facts

## Guided Narrative Voice

Stories should guide a reader through the system, not just describe it.

**Lead with what happens, not what exists:**
- YES: "When a new log slot appears on NFS, **message-producer** scans it and publishes each log line to Kafka."
- NO: "The message-producer component processes log files from NFS."

**Anchors orient the reader:**
- Each story should identify its anchor — the one file:line a new developer should open first.
- Promote the most important `grounded_in` reference to the anchor field.
- Write the anchor description as a "you are here" statement: "This is where a raw log becomes a Kafka message."

**Bridge text between journey stories:**
- Bridge asks a question the next story answers.
- Pattern: "[What you just learned]. But [question that pulls you forward]?"
- Example: "Logs are now parsed into entities. But how do 14 entity types become a queryable graph?"

**First story in getting-started orients:**
- Open with the domain model and purpose: "This is a property-graph system that maps network entities and their relationships."
- Name one concrete thing to follow: "Follow a FortiMail log line from NFS mount to queryable graph node."

## Common Mistakes

1. **Describing the document instead of the system.** "This story covers..." / "The following section..." / "We describe..." — delete these and state the fact directly.

2. **Listing without relating.** "The system has Service A, Service B, and Service C." — say how they connect.

3. **Vague severity.** "There is a potential issue with..." — name the issue, name the component, state the impact.

4. **Passive voice hiding the actor.** "Requests are processed by..." — name the component that does it: "**order-service** processes requests..."

5. **Explaining what a pattern is.** "The circuit breaker pattern prevents cascading failures by..." — the reader knows what a circuit breaker is. Say where it is and what it wraps: "**payment-adapter** wraps Stripe calls with a circuit breaker (pybreaker, 5-failure threshold)."
