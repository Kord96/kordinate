#!/usr/bin/env python3
"""Canonical CLI entrypoint for the Augur script validator.

This file does not implement checks itself. It exists so hooks, agents, and
runtime wiring can invoke one stable script path:
- `validate.py` -> starts one full validator run
- `main.py` -> orchestrates artifact loading, domain checks, logging, sealing,
  and exit status
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    validator_dir = Path(__file__).resolve().parent
    augur_root = validator_dir.parents[2]
    if str(augur_root) not in sys.path:
        sys.path.insert(0, str(augur_root))
    from skills.analyze.validator.main import main
else:
    from .main import main


if __name__ == "__main__":
    raise SystemExit(main())
