---
description: Request-Reply architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [messaging, integration]
---
# Request-Reply

## Recognition

How to identify this pattern in code.

### Signatures

- Correlation ID linking request messages to their responses
- Reply-to queue or topic specified in message headers
- Temporary or exclusive response queues created per requester
- RPC-over-messaging: `call()`, `rpc()`, or `request()` methods that block or return futures
- NATS request-reply: `nc.request(subject, payload, timeout)`
- RabbitMQ RPC: `reply_to` and `correlation_id` properties on AMQP messages
- Timeout configuration for waiting on the reply
- WebSocket/protocol request-reply: unique `messageId` sent with request, callbacks stored in a map (`requests.set(messageId, [resolve, reject])`), matched to incoming response by same ID
- OCPP/custom protocol: message array with `[messageType, messageId, action, payload]` where the ID correlates request to response
- Java: `CompletableFuture`-based request with pending map keyed by request ID, completed when matching response arrives
- Java: Undertow/Netty request-response exchange objects (`HttpServerExchange`, `ChannelHandlerContext.writeAndFlush`)
- OPC UA: `RequestHeader`/`ResponseHeader` with matching request handles across transport

**Not this pattern:** Standard HTTP request-response (browser sends GET, server returns HTML) is not request-reply. This pattern specifically addresses synchronous request-response semantics layered over an asynchronous transport (WebSocket, message broker, custom protocol) using correlation IDs.

### Confidence

- **high** -- correlation ID plus reply-to destination with timeout handling
- **medium** -- message exchange where producer blocks waiting for a response on a known topic
- **low** -- fire-and-forget publish followed by a separate poll for results

## Architecture

Look for synchronous request-response semantics implemented over an asynchronous messaging layer using correlation IDs and reply destinations.

### Review Checklist

- Every request includes a unique correlation ID and a reply-to destination
- Timeout is enforced on the requester side with clear error handling on expiry
- Temporary reply queues are cleaned up after the response is received or timeout fires
- Correlation ID is propagated through any intermediate services for traceability
- Responder handles duplicate requests idempotently

### Anti-patterns

- Missing timeout on the request side (blocking forever on a lost reply)
- Reply queues not cleaned up, leaking resources on the broker
- Using request-reply where fire-and-forget or pub-sub would be simpler
- Correlation ID collisions from non-unique ID generation
