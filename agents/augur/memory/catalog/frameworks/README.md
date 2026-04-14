# Framework catalog

Framework entries describe runtime ecosystems and framework-native primitives.

They are separate from architectural concepts:
- frameworks answer **what stack/primitives are present**
- concepts answer **what architectural patterns and shapes are present**

Each framework should live in its own directory:

```text
frameworks/<name>/
  framework.md       # canonical narrative: primitives, conventions, failure modes
  semantics.yaml     # structured semantic metadata
```

Detector policy and executable rules for frameworks live under `../../../detectors/frameworks/`.
