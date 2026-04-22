---
kind: concept
name: tensor
signatures: {}
source:
  memory_concept: memory/catalog/concepts/tensor.md
type: pattern
abstraction:
- data
- compute
scope: domain
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `torch.Tensor`, `torch.tensor()`, `torch.zeros()`, `torch.randn()` tensor creation
- `tf.Tensor`, `tf.constant()`, `tf.Variable()` TensorFlow tensor operations
- `jax.numpy`, `jnp.array()`, `jax.jit`, `jax.grad` JAX functional transforms
- `numpy.ndarray`, `np.array()`, `np.dot()`, `np.matmul()` array operations
- `model.predict()`, `model.forward()`, `model.__call__()` inference entry points
- `.to('cuda')`, `.to(device)`, `torch.cuda.is_available()` GPU dispatch
- `batch_size`, `DataLoader`, `Dataset` training/inference pipeline components
- Go: `gonum/mat`, `gorgonia` tensor operations
- Rust: `ndarray`, `tch-rs` (PyTorch bindings), `candle` tensor library
- Java: `DJL` (Deep Java Library), `nd.NDArray`, `tensorflow-java` bindings

### Confidence

- **high** -- PyTorch/TensorFlow/JAX model with tensor operations, GPU dispatch, and a DataLoader-based inference or training pipeline
- **medium** -- NumPy ndarray computations with matrix operations and batch processing but no deep learning framework
- **low** -- Simple array math without explicit tensor semantics or multi-dimensional broadcasting

## Architecture

### When to use
- Machine learning model training and inference pipelines
- Scientific computing with multi-dimensional array operations
- GPU-accelerated numerical workloads requiring batch processing

### Anti-patterns
- Running inference on CPU in production when GPU is available, causing unnecessary latency
- Loading the full model on every request instead of keeping it warm in memory
- Ignoring tensor dtype and device mismatches, causing silent precision loss or runtime errors

### Complements
- [feature-store](/concepts/feature-store) — tensor models consume features from feature stores
- [model-registry](/concepts/model-registry) — trained models are versioned and served from a registry
- [training-pipeline](/concepts/training-pipeline) — tensor computations are core to training pipelines

## Impact

Tensor workloads have fundamentally different resource profiles than typical services — they require GPU scheduling, batch-oriented scaling, and memory management for large model weights. Monitoring must track inference latency, GPU utilization, and memory pressure to prevent OOM failures.

### Relationship To Other Concepts

- Related to [feature-store](/concepts/feature-store) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [model-registry](/concepts/model-registry) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [training-pipeline](/concepts/training-pipeline) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `tensor` when the important observation is this specific architectural concern within a domain-modeling or product-domain concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
