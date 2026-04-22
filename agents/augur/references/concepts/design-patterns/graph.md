---
kind: concept
name: graph
signatures: {}
source:
  memory_concept: memory/catalog/concepts/graph.md
type: pattern
abstraction:
- data
- algorithmic
scope: domain
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `Graph`, `DiGraph`, `DAG` class definitions or type aliases
- `topological_sort`, `topo_sort`, `toposort` function calls for DAG ordering
- `adjacency_list`, `adjacency_matrix`, `adj` data structures
- `BFS`, `DFS`, `breadth_first`, `depth_first` traversal implementations
- `shortest_path`, `dijkstra`, `bellman_ford`, `a_star` pathfinding algorithms
- `cycle_detect`, `has_cycle`, `is_acyclic` graph validation functions
- Python: `networkx`, `igraph`, `graphlib.TopologicalSorter` usage
- JS/TS: `graphlib`, `dagre`, `cytoscape` graph libraries
- Go: `gonum/graph`, custom `Graph` interface with `Nodes()` and `Edges()`
- Rust: `petgraph`, `Graph`, `DiGraph`, `Dfs`, `Bfs` traversal iterators
- Java: JGraphT (`org.jgrapht`), `DirectedAcyclicGraph`, `GraphWalk`

### Confidence

- **high** -- Dedicated graph library (networkx, petgraph, JGraphT) with explicit graph construction, traversal algorithms, and cycle detection or topological sorting
- **medium** -- Custom adjacency list or matrix with BFS/DFS traversal and path computation
- **low** -- Parent-child relationships forming an implicit tree or DAG without explicit graph modeling or algorithms

## Architecture

### When to use
- Dependency resolution systems (build tools, package managers, task schedulers)
- Workflow orchestration where tasks have ordering constraints
- Any domain with entities connected by directed relationships requiring traversal or ordering

### Anti-patterns
- Implicit graph relationships scattered across code without a centralized graph data structure
- Missing cycle detection in systems that assume DAG properties, causing infinite loops
- Recomputing traversals on every access instead of caching topological order or shortest paths

### Complements
- Property graphs and social graphs are specialized applications of this concept, not separate top-level graph families in Augur's working ontology.
- [workflow-engine](/concepts/workflow-engine) — workflow DAGs are a common graph application
- [pipeline-filter](/concepts/pipeline-filter) — pipelines are often modeled as DAGs

### Scope

Treat `graph` as the primary concept for graph-shaped domain models and graph algorithms.

- Use this concept when the code models nodes, edges, traversals, reachability, or topological ordering.
- Use supporting notes or examples to capture specialized graph variants such as attributed/property graphs or social-network graphs.
- Do not introduce a separate top-level concept unless the specialized graph changes architecture meaningfully beyond "graph with a specific domain."

## Impact

Graph algorithms determine execution order, dependency resolution, and reachability in systems that model relationships. Cycle detection failures in DAGs cause runtime hangs, and inefficient traversal algorithms become bottlenecks as graph size grows. Testing must verify graph invariants (acyclicity for DAGs, connectivity requirements) on every mutation.

### Relationship To Other Concepts

- Related to [workflow-engine](/concepts/workflow-engine) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [pipeline-filter](/concepts/pipeline-filter) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `graph` when the important observation is this specific architectural concern within a domain-modeling or product-domain concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
