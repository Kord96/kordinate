---
description: Subscription and recurring billing pattern for SaaS monetization
type: pattern
category: domain-model
abstraction: [data, financial]
---
# Subscription

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

## Impact

Subscription billing directly affects revenue. Failed payment handling, webhook reliability, and plan migration logic must be thoroughly tested. Monitoring must track payment failure rates, involuntary churn, and billing webhook processing lag to prevent silent revenue loss.
