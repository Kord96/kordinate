#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_elapsed(started_at: str | None) -> str:
    if not started_at:
        return "-"
    try:
        start = datetime.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        return "-"
    delta = datetime.now(UTC) - start
    total = int(delta.total_seconds())
    mins, secs = divmod(total, 60)
    hours, mins = divmod(mins, 60)
    if hours:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def artifact_flags(run_dir: Path) -> str:
    flags = []
    for name in ("atlas.json", "narratives.yaml", "repair-log.json"):
        if (run_dir / name).exists():
            flags.append(name.split(".")[0])
    stories_dir = run_dir / "stories"
    if stories_dir.is_dir() and any(stories_dir.iterdir()):
        flags.append("stories")
    return ",".join(flags) if flags else "-"


def render(run_root: Path) -> str:
    summary_path = run_root / "summary.json"
    summary = load_json(summary_path)
    lines = [
        f"run_root: {run_root}",
        f"manifest: {summary.get('manifest')}",
        f"model: {summary.get('model')}",
        f"started_at: {summary.get('started_at')}",
        f"completed_at: {summary.get('completed_at', '-')}",
        "",
        "condition | status | isolation | elapsed | artifacts",
        "--- | --- | --- | --- | ---",
    ]
    for condition in summary.get("conditions", []):
        cid = str(condition.get("condition_id") or "?")
        status = str(condition.get("status") or "?")
        isolation = "-"
        started = condition.get("started_at")
        run_json = run_root / cid / "run.json"
        if run_json.exists():
            try:
                run_data = load_json(run_json)
                status = str(run_data.get("status") or status)
                started = run_data.get("started_at") or started
                isolation = str(run_data.get("isolation", {}).get("status") or isolation)
            except Exception:
                pass
        artifacts = artifact_flags(run_root / cid)
        lines.append(f"{cid} | {status} | {isolation} | {fmt_elapsed(started)} | {artifacts}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch an ablation run root and print live condition status.")
    parser.add_argument("run_root", type=Path, help="Ablation run root containing summary.json")
    parser.add_argument("--interval", type=float, default=5.0, help="Refresh interval in seconds")
    parser.add_argument("--once", action="store_true", help="Print one snapshot and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = args.run_root.resolve()
    summary_path = run_root / "summary.json"
    if not summary_path.exists():
        raise SystemExit(f"missing summary.json under {run_root}")
    while True:
        os.system("clear")
        print(render(run_root))
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
