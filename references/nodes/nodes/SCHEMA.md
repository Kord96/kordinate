---
schema: node-system.v1
---

# Node Output Schema

Each node module emits a JSON object:

```json
{
  "schema": "node-system.v1",
  "node_id": "<node id matching NODE.md>",
  "status": "success | warning | error",
  "facts": [
    {
      "id": "<stable fact id>",
      "label": "<short fact label>",
      "value": "<JSON scalar, array, or object>",
      "confidence": 1.0,
      "evidence": [
        {
          "kind": "<file | symbol | command | observation | note>",
          "path": "<repo-relative path when available>",
          "detail": "<short evidence note>"
        }
      ]
    }
  ],
  "issues": [
    {
      "level": "warning | error",
      "message": "<actionable message>",
      "path": "<optional repo-relative path>"
    }
  ]
}
```

`facts` is the current compatibility output because old concept units emitted
facts. Future node outputs may add graph-oriented fields under the same
`node-system.v1` contract only after updating this schema and the validator.
