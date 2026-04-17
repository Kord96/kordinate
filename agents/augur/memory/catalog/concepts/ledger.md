---
description: Double-entry ledger pattern for financial data integrity
type: pattern
category: domain-model
abstraction:
- data
- financial
status: primary
scope: domain
relationships:
  related_to:
  - audit-logging
  - event-sourcing
  - saga
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Ledger

## Recognition

How to identify this pattern in code.

### Signatures

- `debit` and `credit` columns or fields appearing in the same table/model
- `JournalEntry`, `LedgerEntry`, or `GeneralLedger` class definitions
- `balance` computed by summing debits and credits: `SUM(debit) - SUM(credit)`
- `double_entry` or `double_entry_bookkeeping` in module or function names
- Python: `hledger`, `beancount`, `ledger` library usage
- JS/TS: `medici` library, `journal` collection with debit/credit documents
- Go: `debit Amount` and `credit Amount` struct fields, `PostTransaction` methods
- Rust: `debit: Decimal`, `credit: Decimal` in transaction structs
- Java: `@Column(name = "debit")` and `@Column(name = "credit")` JPA annotations
- SQL: `GL` table prefix, `journal_entry` table, `account_id` foreign key on entries

### Confidence

- **high** -- JournalEntry or LedgerEntry class with paired debit/credit fields and a balance invariant check ensuring debits equal credits per transaction
- **medium** -- Separate debit and credit columns in a financial table with immutable insert-only entries
- **low** -- A single `amount` field with a `type` enum of debit/credit, without explicit balance verification

## Architecture

### Relationship To Other Concepts

- `ledger` is the financial system-of-record: immutable postings, account balances, and reconciliation invariants.
- Use `audit-logging` for operational traceability when balance invariants are not the central concern.
- Use `event-sourcing` for generic append-only business history; not every event stream is a financial ledger.
- Use `saga` when multi-step transfers or settlements need orchestration around ledger posting.

### When to use
- Financial systems requiring auditability and provable correctness
- Any domain where money moves between accounts and balances must reconcile
- Systems subject to regulatory or compliance requirements on transaction records

### Anti-patterns
- Storing only a running balance without the underlying journal entries, making reconciliation impossible
- Mutable ledger entries that can be updated in place instead of appending correcting entries
- Mixing business logic with ledger posting — the ledger should record facts, not enforce rules

### Complements
- [event-sourcing](/concepts/event-sourcing) — ledger entries are naturally append-only events
- [audit-logging](/concepts/audit-logging) — financial records require audit trails
- [saga](/concepts/saga) — multi-account transfers may need saga coordination

### Boundary

Do not use `ledger` for any append-only transaction table. Prefer it only when debit/credit balancing, account integrity, and reconciliation are architectural requirements.

## Impact

A double-entry ledger provides a self-balancing system of record. When present, testing must verify the balance invariant (total debits == total credits) on every transaction, and monitoring should alert on any imbalance as a critical data integrity failure.
