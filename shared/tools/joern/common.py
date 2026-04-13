#!/usr/bin/env python3
"""Shared helpers for Joern-backed exporters."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_PROFILE_SCRIPT = ROOT.parent / "repo_profile" / "detect_repo_profile.py"
DEFAULT_IMAGE_TAG = os.environ.get("JOERN_IMAGE_TAG", "kordinate/joern:4.0.518")

FRONTENDS = {
    "java": "/opt/joern/joern-cli/javasrc2cpg",
    "c": "/opt/joern/joern-cli/c2cpg.sh",
    "cpp": "/opt/joern/joern-cli/c2cpg.sh",
    "javascript": "/opt/joern/joern-cli/jssrc2cpg.sh",
    "python": "/opt/joern/joern-cli/pysrc2cpg",
    "go": "/opt/joern/joern-cli/gosrc2cpg",
    "kotlin": "/opt/joern/joern-cli/kotlin2cpg",
    "csharp": "/opt/joern/joern-cli/csharpsrc2cpg",
    "php": "/opt/joern/joern-cli/php2cpg",
    "ruby": "/opt/joern/joern-cli/rubysrc2cpg",
    "swift": "/opt/joern/joern-cli/swiftsrc2cpg.sh",
}


def detect_language(repo: Path) -> str:
    result = subprocess.run(
        [sys.executable, str(REPO_PROFILE_SCRIPT), str(repo), "--field", "dominant_language"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to detect repo language")
    language = result.stdout.strip()
    if not language:
        raise RuntimeError("repo language detector returned an empty language")
    return language


def decode_field(value: str) -> str:
    return (
        value.replace("\\t", "\t")
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\\\", "\\")
    )


def run_joern_query(repo: Path, language: str, query_script_path: Path, script_name: str, image_tag: str) -> str:
    frontend = FRONTENDS.get(language)
    if not frontend:
        raise RuntimeError(f"unsupported language for Joern export: {language}")
    if shutil.which("docker") is None:
        raise RuntimeError("docker is not available")
    if not query_script_path.exists():
        raise RuntimeError(f"query script not found: {query_script_path}")

    query_script = query_script_path.read_text(encoding="utf-8")
    container_script = (
        f"cat >/tmp/{script_name} <<'EOF'\n"
        f"{query_script}\n"
        "EOF\n"
        f"{frontend} /repo -o /tmp/cpg.bin >/dev/null && "
        f"joern /tmp/cpg.bin --script /tmp/{script_name}"
    )
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{repo}:/repo:ro",
        image_tag,
        "bash",
        "-lc",
        container_script,
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=900,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(stderr or f"joern export failed with exit code {result.returncode}")
    return result.stdout


def run_joern_queries(
    repo: Path,
    language: str,
    queries: list[tuple[Path, str]],
    image_tag: str,
) -> dict[str, str]:
    frontend = FRONTENDS.get(language)
    if not frontend:
        raise RuntimeError(f"unsupported language for Joern export: {language}")
    if shutil.which("docker") is None:
        raise RuntimeError("docker is not available")
    for query_script_path, _ in queries:
        if not query_script_path.exists():
            raise RuntimeError(f"query script not found: {query_script_path}")

    script_parts: list[str] = []
    run_parts = [f"{frontend} /repo -o /tmp/cpg.bin >/dev/null"]
    for query_script_path, script_name in queries:
        query_script = query_script_path.read_text(encoding="utf-8")
        script_parts.append(
            f"cat >/tmp/{script_name} <<'EOF'\n"
            f"{query_script}\n"
            "EOF\n"
        )
        output_name = script_name.removesuffix(".sc") + ".out"
        run_parts.append(f"joern /tmp/cpg.bin --script /tmp/{script_name} > /tmp/{output_name}")
    collect_parts = []
    for _, script_name in queries:
        output_name = script_name.removesuffix(".sc") + ".out"
        collect_parts.append(
            f"printf '__KORD_OUTPUT_BEGIN__%s\\n' '{script_name}' && cat /tmp/{output_name} && printf '__KORD_OUTPUT_END__%s\\n' '{script_name}'"
        )

    container_script = "".join(script_parts) + " && ".join(run_parts + collect_parts)
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{repo}:/repo:ro",
        image_tag,
        "bash",
        "-lc",
        container_script,
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=1200,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(stderr or f"joern export failed with exit code {result.returncode}")

    outputs: dict[str, list[str]] = {}
    current: str | None = None
    for line in result.stdout.splitlines():
        if line.startswith("__KORD_OUTPUT_BEGIN__"):
            current = line.removeprefix("__KORD_OUTPUT_BEGIN__")
            outputs[current] = []
            continue
        if line.startswith("__KORD_OUTPUT_END__"):
            current = None
            continue
        if current is not None:
            outputs[current].append(line)
    return {name: "\n".join(lines) + ("\n" if lines else "") for name, lines in outputs.items()}
