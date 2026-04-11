#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path


SCRIPT = Path("/kord/workstation/home/project/kordinate/shared/skills/improve/scripts/collect_agent_reflections.py")


if __name__ == "__main__":
    runpy.run_path(str(SCRIPT), run_name="__main__")
