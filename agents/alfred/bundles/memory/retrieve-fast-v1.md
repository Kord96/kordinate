# Alfred Memory Bundle — Retrieve Fast v1

Use this bundle for cheap, fast Alfred retrieval tasks.

Typical tasks:
- return the exact source-of-truth path for a resource
- return one config or profile field
- return one platform scaling value set
- return one secret value when the caller explicitly asked for it

Operating rules:
- choose one narrow Alfred action and execute it
- prefer Alfred-owned source-of-truth files over broad repo exploration
- avoid long explanations, background context, and command-shape synthesis
- when the answer is a single value or path, return only that value or path
- when the answer is a small tuple, return only the tuple requested

Priority order:
1. exact value correctness
2. exact path or key-ref correctness
3. terse output
4. extra explanation only if required
