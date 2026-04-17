---
description: Claim Check architectural pattern
type: pattern
testable: true
distributed: true
graphable: true
abstraction:
- integration
- messaging
status: primary
scope: cross-cutting
relationships:
  related_to:
  - message-queue
  - webhook
  - dead-letter
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Claim Check

## Recognition

How to identify this pattern in code.

### Signatures

- Large payload stored in blob or object storage before sending a message
- Message body contains a reference/URL instead of the full payload
- `s3://` or `gs://` or `az://` references embedded in message fields
- Download-on-consume pattern where the consumer fetches data by reference
- Payload size threshold triggering offload to external storage
- Separate upload and notify steps in producer code
- Claim token or reference ID passed through the message bus

### Confidence

- **high** -- explicit size-check logic that offloads to object storage and replaces payload with a reference
- **medium** -- messages contain storage URLs but no explicit size threshold or offload logic visible
- **low** -- large blob references in messages but could be a normal file-sharing workflow rather than intentional claim check

## Architecture

Look for payload offloading to external storage with reference-based message passing.

### Review Checklist

- Size threshold for offloading is configurable and documented
- References include enough metadata to retrieve the payload (bucket, key, version)
- Consumers handle both inline payloads and claim-check references transparently
- Stored payloads have a retention/expiration policy to avoid orphaned blobs
- Access control on the storage matches the message consumer's permissions

### Anti-patterns

- No cleanup -- offloaded payloads accumulate indefinitely in storage
- Consumer assumes all messages are inline and crashes on references
- Reference points to storage the consumer cannot access (permission mismatch)
- No fallback for storage unavailability -- producer fails entirely instead of degrading

### Relationship To Other Concepts

- Related to [message-queue](/concepts/message-queue) because claim-check is often used to keep queue payloads small by storing large bodies externally.
- Related to [webhook](/concepts/webhook) when callbacks or events carry references to externally retrievable payloads instead of inlining them.
- Related to [dead-letter](/concepts/dead-letter) when failed reference resolution or payload retrieval requires quarantine and retry handling.

### Boundary

Use `claim-check` when messages carry a pointer to externally stored payload data instead of embedding the full payload inline.

Do not use it for any ID field or storage reference. The key signal is intentionally offloading large payloads from the message body.
