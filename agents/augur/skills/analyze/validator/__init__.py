"""Augur validator package.

Public entrypoints:
- `validate.py`: CLI entrypoint used by agents, hooks, and runtime wiring
- `main.py`: coordinator that loads artifacts, runs checks, appends `log.json`,
  optionally seals a clean run, and exits

Domain modules:
- `atlas_model.py`: atlas.json fields, graph/model domains, and health refs
- `atlas_health.py`: shared health block contract used from atlas validation
- `story.py`: story YAML shape, grounding, teaching quality, and atlas refs
- `narrative.py`: narratives.yaml shape and cross-artifact reading-path checks
- `meta.py`: final sealed metadata validation

Support modules:
- `context.py`: project/facts discovery and JSON loading
- `history.py`: validation log classification and append-only history writing
- `helpers.py`: path, grounding, overlap, and YAML helpers
"""

from .main import main

__all__ = ["main"]
