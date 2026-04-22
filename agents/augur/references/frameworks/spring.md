---
kind: framework
name: spring
signatures:
  framework: spring
  manifest_packages:
    pom:
    - spring-boot
    - springframework
  source_extensions:
  - .java
  - .kt
  - .xml
  path_patterns:
    strong: []
    medium: []
    weak: []
  source_patterns:
    strong:
    - '@RestController\b'
    - '@SpringBootApplication\b'
    - '@GetMapping\s*\('
    - '@PostMapping\s*\('
    - '@RequestMapping\s*\('
    medium:
    - '@Autowired\b'
    - '@Component\b'
    weak: []
  negative_path_patterns: []
  negative_source_patterns: []
source:
  memory_framework: memory/catalog/frameworks/spring/framework.md
  semantics: memory/catalog/frameworks/spring/semantics.yaml
language: java
framework_kind: full-stack
scope: backend
status: primary
---

# Explanation

Spring is a framework Augur recognizes during deterministic analysis. Its semantic role is defined in `semantics.yaml`, and Phase 2 should treat detection as strong but revisable evidence when interpreting the architecture.

## Recognition
Use the framework reference in `references/frameworks/` as the canonical shared explanation and signatures source. Deterministic detector policy or rules, when present, live under `detectors/frameworks/spring/`.

## Architectural implications
- framework scope: `backend`
- framework kind: `full-stack`
- framework-native traits and relationships are defined in `semantics.yaml`

## Common failure modes
- annotation-heavy-indirection
- service-layer-bloat
- hidden-runtime-magic
