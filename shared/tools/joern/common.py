#!/usr/bin/env python3
"""Shared helpers for Joern-backed exporters."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import uuid
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

JOERN_BINARY = os.environ.get("JOERN_BINARY", "joern")
JOERN_HOME = Path(os.environ.get("JOERN_HOME", "/opt/joern"))


def _running_in_container() -> bool:
    return Path("/.dockerenv").exists() or bool(os.environ.get("KUBERNETES_SERVICE_HOST"))


def _docker_command(*args: str) -> list[str]:
    return ["docker", *args]


def _run_docker(command: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _create_joern_container(image_tag: str, script: str) -> str:
    result = _run_docker(
        _docker_command("create", image_tag, "bash", "-lc", script),
        timeout=120,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(stderr or f"failed to create joern container with exit code {result.returncode}")
    return result.stdout.strip()


def _docker_cp_to_container(container_id: str, source: Path, destination: str, timeout: int) -> None:
    result = _run_docker(
        _docker_command("cp", str(source), f"{container_id}:{destination}"),
        timeout=timeout,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(stderr or f"docker cp failed with exit code {result.returncode}")


def _remove_container(container_id: str) -> None:
    _run_docker(_docker_command("rm", "-f", container_id), timeout=120)


def _run_joern_query_docker_copy(
    repo: Path,
    language: str,
    query_script_path: Path,
    script_name: str,
    image_tag: str,
) -> str:
    container_id = ""
    repo_source = repo / "."
    frontend = FRONTENDS.get(language)
    if not frontend:
        raise RuntimeError(f"unsupported language for Joern export: {language}")
    container_script = (
        "mkdir -p /repo && "
        f"{frontend} /repo -o /tmp/cpg.bin >/dev/null && "
        f"joern --script /tmp/{script_name} --param cpgFile=/tmp/cpg.bin"
    )
    try:
        container_id = _create_joern_container(image_tag, container_script)
        _docker_cp_to_container(container_id, repo_source, "/repo", timeout=1800)
        _docker_cp_to_container(container_id, query_script_path, f"/tmp/{script_name}", timeout=120)
        result = _run_docker(_docker_command("start", "-a", container_id), timeout=1800)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise RuntimeError(stderr or f"joern export failed with exit code {result.returncode}")
        return result.stdout
    finally:
        if container_id:
            _remove_container(container_id)


def _run_joern_queries_docker_copy(
    repo: Path,
    language: str,
    queries: list[tuple[Path, str]],
    image_tag: str,
) -> dict[str, str]:
    container_id = ""
    repo_source = repo / "."
    frontend = FRONTENDS.get(language)
    if not frontend:
        raise RuntimeError(f"unsupported language for Joern export: {language}")
    marker = f"__KORD_OUTPUT__{uuid.uuid4().hex}__"
    setup_parts = ["mkdir -p /repo"]
    run_parts = [f"{frontend} /repo -o /tmp/cpg.bin >/dev/null"]
    collect_parts: list[str] = []
    for _, script_name in queries:
        output_name = script_name.removesuffix(".sc") + ".out"
        run_parts.append(f"joern --script /tmp/{script_name} --param cpgFile=/tmp/cpg.bin > /tmp/{output_name}")
        collect_parts.append(
            f"printf '{marker}BEGIN:%s\\n' '{script_name}' && cat /tmp/{output_name} && printf '{marker}END:%s\\n' '{script_name}'"
        )
    container_script = " && ".join(setup_parts + run_parts + collect_parts)
    try:
        container_id = _create_joern_container(image_tag, container_script)
        _docker_cp_to_container(container_id, repo_source, "/repo", timeout=1800)
        for query_script_path, script_name in queries:
            _docker_cp_to_container(container_id, query_script_path, f"/tmp/{script_name}", timeout=120)
        result = _run_docker(_docker_command("start", "-a", container_id), timeout=2400)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise RuntimeError(stderr or f"joern export failed with exit code {result.returncode}")
        outputs: dict[str, list[str]] = {}
        current: str | None = None
        for line in result.stdout.splitlines():
            if line.startswith(f"{marker}BEGIN:"):
                current = line.split(":", 1)[1]
                outputs[current] = []
                continue
            if line.startswith(f"{marker}END:"):
                current = None
                continue
            if current is not None:
                outputs[current].append(line)
        return {name: "\n".join(lines) for name, lines in outputs.items()}
    finally:
        if container_id:
            _remove_container(container_id)


def _resolve_frontend(language: str) -> str:
    frontend = FRONTENDS.get(language)
    if not frontend:
        raise RuntimeError(f"unsupported language for Joern export: {language}")
    if frontend.startswith("/opt/joern/"):
        candidate = JOERN_HOME / frontend.removeprefix("/opt/joern/")
        return str(candidate)
    return frontend


def _run_joern_query_direct(repo: Path, language: str, query_script_path: Path, script_name: str) -> str:
    frontend = _resolve_frontend(language)
    joern_binary = shutil.which(JOERN_BINARY) or shutil.which("joern")
    if not joern_binary:
        raise RuntimeError("joern is not available")
    if shutil.which(frontend) is None and not Path(frontend).exists():
        raise RuntimeError(f"joern frontend is not available: {frontend}")
    if not query_script_path.exists():
        raise RuntimeError(f"query script not found: {query_script_path}")

    with tempfile.TemporaryDirectory(prefix="joern-query-") as temp_dir:
        temp_path = Path(temp_dir)
        cpg_path = temp_path / "cpg.bin"
        script_path = temp_path / script_name
        script_path.write_text(query_script_path.read_text(encoding="utf-8"), encoding="utf-8")

        frontend_result = subprocess.run(
            [frontend, str(repo), "-o", str(cpg_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=900,
        )
        if frontend_result.returncode != 0 or not cpg_path.exists():
            stderr = frontend_result.stderr.strip()
            raise RuntimeError(stderr or f"joern frontend failed with exit code {frontend_result.returncode}")

        result = subprocess.run(
            [joern_binary, "--script", str(script_path), "--param", f"cpgFile={cpg_path}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=900,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise RuntimeError(stderr or f"joern export failed with exit code {result.returncode}")
        return result.stdout


def _run_joern_queries_direct(repo: Path, language: str, queries: list[tuple[Path, str]]) -> dict[str, str]:
    frontend = _resolve_frontend(language)
    joern_binary = shutil.which(JOERN_BINARY) or shutil.which("joern")
    if not joern_binary:
        raise RuntimeError("joern is not available")
    if shutil.which(frontend) is None and not Path(frontend).exists():
        raise RuntimeError(f"joern frontend is not available: {frontend}")
    for query_script_path, _ in queries:
        if not query_script_path.exists():
            raise RuntimeError(f"query script not found: {query_script_path}")

    with tempfile.TemporaryDirectory(prefix="joern-query-") as temp_dir:
        temp_path = Path(temp_dir)
        cpg_path = temp_path / "cpg.bin"
        frontend_result = subprocess.run(
            [frontend, str(repo), "-o", str(cpg_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=1200,
        )
        if frontend_result.returncode != 0 or not cpg_path.exists():
            stderr = frontend_result.stderr.strip()
            raise RuntimeError(stderr or f"joern frontend failed with exit code {frontend_result.returncode}")

        outputs: dict[str, str] = {}
        for query_script_path, script_name in queries:
            script_path = temp_path / script_name
            script_path.write_text(query_script_path.read_text(encoding="utf-8"), encoding="utf-8")
            result = subprocess.run(
                [joern_binary, "--script", str(script_path), "--param", f"cpgFile={cpg_path}"],
                check=False,
                capture_output=True,
                text=True,
                timeout=1200,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise RuntimeError(stderr or f"joern export failed with exit code {result.returncode}")
            outputs[script_name] = result.stdout
        return outputs


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
    docker_available = shutil.which("docker") is not None
    if not docker_available:
        return _run_joern_query_direct(repo, language, query_script_path, script_name)
    if _running_in_container():
        return _run_joern_query_docker_copy(repo, language, query_script_path, script_name, image_tag)
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
        container_script.replace(
            f"joern /tmp/cpg.bin --script /tmp/{script_name}",
            f"joern --script /tmp/{script_name} --param cpgFile=/tmp/cpg.bin",
        ),
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
    docker_available = shutil.which("docker") is not None
    if not docker_available:
        return _run_joern_queries_direct(repo, language, queries)
    if _running_in_container():
        return _run_joern_queries_docker_copy(repo, language, queries, image_tag)
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
    container_script = container_script.replace(
        "joern /tmp/cpg.bin --script /tmp/",
        "joern --script /tmp/",
    ).replace(" > /tmp/", " --param cpgFile=/tmp/cpg.bin > /tmp/")
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
