#!/usr/bin/env python3
"""Canonical CLI entrypoint for the Augur script validator.

This file does not implement checks itself. It exists so hooks, agents, and
runtime wiring can invoke one stable script path:
- `validate.py` -> starts one full validator run
- `main.py` -> orchestrates artifact loading, domain checks, logging, sealing,
  and exit status
"""

from .main import main


if __name__ == "__main__":
    raise SystemExit(main())
