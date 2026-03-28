## Testing

Verify wrap-around correctness, full/empty distinction, and overwrite semantics at buffer boundaries.

### Unit Tests

- Write items up to capacity and read them back in FIFO order
- Write beyond capacity and verify the oldest items are overwritten (overwrite-on-full policy)
- Verify empty buffer read returns nothing or blocks as specified (no stale data from previous cycle)
- Test the full vs empty distinction when head equals tail (unambiguous state after wrap-around)

### Boundary Tests

- Write exactly capacity items, read all, write again, and verify wrap-around indexing is correct
- Test with capacity as a power of two and a non-power-of-two to verify modulo arithmetic handles both
- Write a single item, read it, repeat many times, and verify indices wrap correctly over multiple cycles

### Concurrency Tests

- For SPSC buffers: run a producer and consumer on separate threads and verify no data corruption or loss
- For MPSC/MPMC variants: run multiple producers and verify all items are consumed exactly once
- Verify lock-free implementations with a race detector enabled to catch unsynchronized memory access

