"""
Generic function call finder using AST.

Extracted from nokrashi-tools (Kord96/nokrashi-tools, archived).
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CallLocation:
    """A function call found in code."""

    function: str  # Name of function called
    file: str
    line: int
    args: dict = field(default_factory=dict)  # Extracted arguments


def find_calls(
    project_path: str | Path,
    function_names: list[str],
    extract_kwargs: list[str] | None = None,
    extract_args: list[int] | None = None,
) -> list[CallLocation]:
    """Find function calls and extract arguments.

    Args:
        project_path: Path to project root
        function_names: Function names to search for (e.g., ["Metric", "Counter"])
        extract_kwargs: Keyword argument names to extract (e.g., ["name", "type"])
        extract_args: Positional argument indices to extract (e.g., [0, 1])

    Returns:
        List of CallLocation with extracted arguments

    Example:
        # Find all Metric(name="...", prometheus_type=...) calls
        find_calls(
            ".",
            function_names=["Metric"],
            extract_kwargs=["name", "prometheus_type"]
        )

        # Find all Counter("metric_name", "description") calls
        find_calls(
            ".",
            function_names=["Counter", "Gauge", "Histogram"],
            extract_args=[0, 1]
        )
    """
    project_path = Path(project_path)
    results = []
    extract_kwargs = extract_kwargs or []
    extract_args = extract_args or []

    for py_file in project_path.rglob("*.py"):
        # Skip hidden dirs, venv, etc.
        if any(
            part.startswith(".") or part in ("venv", "node_modules", "__pycache__")
            for part in py_file.parts
        ):
            continue

        try:
            content = py_file.read_text()
            tree = ast.parse(content)
        except Exception:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            # Get function name
            func_name = _get_call_name(node)
            if func_name not in function_names:
                continue

            # Extract arguments
            args = {}

            # Extract positional args
            for idx in extract_args:
                if idx < len(node.args):
                    value = _extract_value(node.args[idx])
                    if value is not None:
                        args[f"arg{idx}"] = value

            # Extract keyword args
            for kw in node.keywords:
                if kw.arg in extract_kwargs:
                    value = _extract_value(kw.value)
                    if value is not None:
                        args[kw.arg] = value

            # Only include if we extracted something
            if args:
                try:
                    rel_path = str(py_file.relative_to(project_path))
                except ValueError:
                    rel_path = str(py_file)

                results.append(
                    CallLocation(
                        function=func_name,
                        file=rel_path,
                        line=node.lineno,
                        args=args,
                    )
                )

    return results


def _get_call_name(node: ast.Call) -> str | None:
    """Extract function name from a Call node."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    elif isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _extract_value(node: ast.expr) -> str | None:
    """Extract a constant value from an AST node."""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Attribute):
        # Handle Enum.VALUE (e.g., PrometheusType.GAUGE -> "GAUGE")
        # Only extract if it looks like an enum (UPPER_CASE attribute)
        if isinstance(node.value, ast.Name) and node.attr.isupper():
            return node.attr
        # Otherwise it's variable.attr which is a variable reference
        return None
    elif isinstance(node, ast.Name):
        # Variable reference - skip
        return None
    return None
