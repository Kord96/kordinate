---
description: Conversation threading pattern for messaging and real-time communication
type: pattern
category: domain-model
abstraction: [data, communication]
---
# Conversation Thread

## Recognition

How to identify this pattern in code.

### Signatures

- `Message`, `Thread`, `Conversation` model classes with parent-child relationships
- `reply_to`, `parent_message_id`, `thread_id` foreign keys linking messages
- `Reaction`, `reaction`, `emoji` models attached to messages
- `read_receipt`, `ReadReceipt`, `last_read_at`, `seen_by` read state tracking
- `Channel`, `channel_id`, `Room` grouping constructs for message streams
- Python: `channels`, message models with `sender`, `content`, `thread` fields
- JS/TS: `socket.io` or WebSocket handlers for real-time message delivery, `stream-chat`
- Go: message structs with `ThreadID`, `ParentID`, WebSocket hub for broadcasting
- Rust: message types with `reply_to: Option<MessageId>`, async channel for delivery
- Java: `@Entity Message` with `@ManyToOne` thread relationship, STOMP/WebSocket messaging

### Confidence

- **high** -- Thread/Message hierarchy with reply_to references, real-time delivery via WebSocket, read receipts, and reactions on messages
- **medium** -- Message model with conversation grouping and reply chains but polling-based delivery
- **low** -- Simple comment list without threading, real-time delivery, or read state management

## Architecture

### When to use
- Chat and messaging features where users converse in threads or channels
- Comment systems with threaded replies and nested discussions
- Customer support systems with conversation history and agent assignment

### Anti-patterns
- Polling for new messages instead of using WebSocket or SSE for real-time delivery
- Unbounded thread depth without pagination, causing query and rendering performance issues
- Storing read state per-message-per-user in a flat table, which grows as O(messages * users)

### Complements
- [websocket](/concepts/websocket) — real-time message delivery uses WebSocket connections
- [pub-sub](/concepts/pub-sub) — message distribution across channels follows pub/sub patterns
- [pagination](/concepts/pagination) — message history requires cursor-based pagination for infinite scroll

## Impact

Conversation threading combines data modeling complexity with real-time delivery requirements. Read state tracking creates significant storage and query pressure at scale, and message ordering guarantees affect both user experience and system design for distributed deployments.
