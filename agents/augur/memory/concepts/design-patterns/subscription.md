---
kind: concept
name: subscription
signatures: {}
type: pattern
abstraction:
- data
- financial
scope: domain
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `Subscription`, `Plan`, `BillingCycle` model classes with status and period fields
- `invoice`, `Invoice`, `LineItem` classes for billing record generation
- `usage_meter`, `UsageMeter`, `metered_billing` for consumption-based pricing
- Stripe SDK: `stripe.Subscription`, `stripe.Invoice`, `stripe.PaymentIntent`
- Paddle SDK: `paddle`, `paddle.subscriptions`, webhook event handlers
- `trial`, `trial_end`, `trial_days` fields for free trial management
- `churn`, `MRR`, `ARR` metric calculations or dashboard fields
- `recurring_payment`, `billing_period`, `next_billing_date` scheduling fields
- Python: `djstripe`, `stripe` library, `billing` app or module
- JS/TS: `stripe` package, `@stripe/stripe-js`, subscription webhook handlers
- Go: `stripe-go`, `Subscription` struct with `Status` and `CurrentPeriodEnd`
- Java: `com.stripe.model.Subscription`, billing service with plan management

### Confidence

- **high** -- Stripe/Paddle integration with subscription lifecycle management (create, upgrade, downgrade, cancel), invoice generation, and webhook handling for payment events
- **medium** -- Custom Subscription and Plan models with billing cycle tracking and recurring charge scheduling
- **low** -- Simple boolean `is_premium` flag without plan tiers, billing cycles, or payment integration

## Architecture

### Relationship To Other Concepts

- `subscription` is the revenue-domain model: plans, billing cycles, invoices, renewals, and churn.
- Use `webhook` when the key concern is provider event ingress rather than billing lifecycle semantics.
- Use `state-machine` for lifecycle transitions like trial, active, past_due, and canceled.
- Use `multi-tenant` when entitlements are attached to tenant scope rather than individual users.

### When to use
- SaaS products with tiered pricing plans and recurring revenue
- Usage-based or metered billing where charges depend on consumption
- Any product requiring trial periods, upgrades, downgrades, and cancellation flows

### Anti-patterns
- Building custom billing logic instead of using a payment provider's subscription management
- Not handling webhook delivery failures, causing billing state to drift from the payment provider
- Storing payment credentials locally instead of using tokenized references from the payment provider

### Complements
- [webhook](/concepts/webhook) — payment provider events arrive via webhooks
- [state-machine](/concepts/state-machine) — subscription lifecycle (trial, active, past_due, canceled) is a state machine
- [multi-tenant](/concepts/multi-tenant) — subscriptions often gate tenant-level feature access

### Relationship To Other Concepts

- Related to [multi-tenant](/concepts/multi-tenant) because subscription tiers often control tenant-level entitlements and limits.
- Related to [state-machine](/concepts/state-machine) because subscription lifecycle changes usually move through well-defined states such as trial, active, past-due, and canceled.
- Related to [webhook](/concepts/webhook) when billing providers notify the system about renewal, payment failure, or cancellation events asynchronously.

### Boundary

Do not use `subscription` for any premium flag or simple entitlement check. Prefer it only when recurring billing and lifecycle management are part of the architecture.

## Impact

Subscription billing directly affects revenue. Failed payment handling, webhook reliability, and plan migration logic must be thoroughly tested. Monitoring must track payment failure rates, involuntary churn, and billing webhook processing lag to prevent silent revenue loss.
