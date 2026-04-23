from __future__ import annotations

from pathlib import Path
import runpy
import sys


def run_util(name: str) -> None:
    utils_dir = Path(__file__).resolve().parents[1] / "utils"
    if str(utils_dir) not in sys.path:
        sys.path.insert(0, str(utils_dir))
    target = utils_dir / name
    runpy.run_path(str(target), run_name="__main__")
