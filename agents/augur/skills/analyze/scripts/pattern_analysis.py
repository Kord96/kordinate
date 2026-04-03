"""
Test pattern analysis utilities.

Provides:
- analyze_timeout_prone_patterns: Detect patterns that could cause infinite loops
- get_test_to_code_mapping: Analyze which tests cover which functions
- analyze_assertion_quality: Detect weak tests
- check_test_isolation: Detect shared state issues
- analyze_import_chains: Suggest correct mock targets

Extracted from nokrashi-tools (Kord96/nokrashi-tools, archived).
"""

import ast
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from .mock_analysis import _extract_mock_configurations, _extract_patch_target
except ImportError:
    from mock_analysis import _extract_mock_configurations, _extract_patch_target


# ---------------------------------------------------------------------------
# Inlined utilities (formerly nokrashi.analysis.utils)
# ---------------------------------------------------------------------------

def _get_cache_dir(project_path: str) -> Path:
    """Get cache directory for a project (in system temp)."""
    project_hash = hashlib.md5(project_path.encode()).hexdigest()[:8]
    cache_dir = Path(tempfile.gettempdir()) / "test_analysis" / project_hash
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _run_command(
    cmd: list[str],
    cwd: str | None = None,
    timeout: int = 300,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        run_env = None
        if env:
            run_env = os.environ.copy()
            run_env.update(env)
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout, env=run_env
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


# ---------------------------------------------------------------------------
# Timeout-prone pattern detection
# ---------------------------------------------------------------------------

def _analyze_test_for_timeout_risks(
    func_node: ast.FunctionDef, content: str, test_file: str
) -> list:
    """Analyze a test function for timeout-prone patterns."""
    risks = []

    mock_params = set()
    for decorator in func_node.decorator_list:
        if _extract_patch_target(decorator):
            mock_params.add(decorator)

    param_names = {arg.arg for arg in func_node.args.args}
    configured_methods = _extract_mock_configurations(func_node)

    test_calls_methods = set()
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                test_calls_methods.add(node.func.attr)

    for param, configs in configured_methods.items():
        configured_attrs = {c.get("method") for c in configs}

        if "__iter__" in configured_attrs:
            loop_methods = {"poll", "recv", "read", "get", "fetch", "consume"}
            if not (configured_attrs & loop_methods):
                risks.append(
                    {
                        "test_file": test_file,
                        "test_function": func_node.name,
                        "line": func_node.lineno,
                        "pattern": "iterator_without_polling",
                        "risk_level": "high",
                        "description": "Mock configures __iter__ but might need poll/recv/read for real implementation",
                        "suggestion": "Check if the real code uses poll-based consumption instead of iteration",
                    }
                )

        if param in param_names:
            has_termination = any(
                "side_effect" in str(c) or "StopIteration" in str(c) for c in configs
            )
            if not has_termination and configured_attrs:
                sets_stop = False
                for node in ast.walk(func_node):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Attribute):
                                if target.attr in (
                                    "stop_requested",
                                    "running",
                                    "should_stop",
                                    "_stop",
                                ):
                                    sets_stop = True

                if not sets_stop and "__iter__" in configured_attrs:
                    risks.append(
                        {
                            "test_file": test_file,
                            "test_function": func_node.name,
                            "line": func_node.lineno,
                            "pattern": "no_loop_termination",
                            "risk_level": "medium",
                            "description": "Test configures iterator but may not set termination condition",
                            "suggestion": "Ensure test sets stop_requested=True or mock returns finite data",
                        }
                    )

    return risks


def analyze_timeout_prone_patterns(project_path: str, test_dir: str = "tests") -> dict:
    """Detect test patterns that could cause infinite loops or timeouts.

    Detects:
    1. While loops with mocked conditions that may never change
    2. Iterators on mocks that might not terminate
    3. Polling patterns without proper mock setup

    Returns:
        dict with:
            - timeout_risks: list of detected risky patterns
            - summary: counts by risk level
    """
    test_path = Path(project_path) / test_dir

    result = {
        "timeout_risks": [],
        "summary": {
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
        },
    }

    if not test_path.exists():
        return result

    for test_file in test_path.rglob("test_*.py"):
        try:
            content = test_file.read_text()
            tree = ast.parse(content)
            rel_path = str(test_file.relative_to(project_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    risks = _analyze_test_for_timeout_risks(node, content, rel_path)
                    result["timeout_risks"].extend(risks)

        except (SyntaxError, IOError):
            continue

    for risk in result["timeout_risks"]:
        level = risk.get("risk_level", "low")
        result["summary"][f"{level}_risk"] = (
            result["summary"].get(f"{level}_risk", 0) + 1
        )

    return result


# ---------------------------------------------------------------------------
# Test-to-code mapping
# ---------------------------------------------------------------------------

def _has_dedicated_test(func_name: str, test_names: set) -> bool:
    """Check if any test name suggests it's dedicated to testing this function."""
    func_name_lower = func_name.lower()

    for test in test_names:
        test_lower = test.lower()
        if func_name_lower in test_lower:
            return True
        if f"test_{func_name_lower}" in test_lower:
            return True

    return False


def get_test_to_code_mapping(project_path: str, test_dir: str = "tests") -> dict:
    """Analyze which tests cover which functions using coverage contexts.

    Uses pytest-cov's --cov-context=test to track coverage per test.

    Returns:
        dict with:
            - function_coverage: dict of function -> list of tests covering it
            - uncovered_functions: functions with 0% coverage
            - incidentally_covered: functions covered but with no dedicated test
    """
    cache_dir = _get_cache_dir(project_path)
    coverage_db = cache_dir / ".coverage_contexts"

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_dir,
        "--cov=.",
        f"--cov-report=",
        "--cov-context=test",
        "-q",
        "--no-header",
        "--timeout=120",
        f"-o=cache_dir={cache_dir / 'pytest_cache'}",
    ]

    env = {"COVERAGE_FILE": str(coverage_db)}
    _run_command(cmd, cwd=project_path, timeout=600, env=env)

    result = {
        "function_coverage": {},
        "uncovered_functions": [],
        "incidentally_covered": [],
        "dedicated_tests": [],
    }

    if not coverage_db.exists():
        return result

    try:
        import sqlite3

        conn = sqlite3.connect(str(coverage_db))
        cursor = conn.cursor()

        cursor.execute("SELECT id, context FROM context")
        contexts = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT id, path FROM file")
        files = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute(
            """
            SELECT file_id, context_id, numbits
            FROM line_bits
        """
        )

        line_contexts = {}
        for file_id, context_id, numbits in cursor.fetchall():
            file_path = files.get(file_id, "")
            context = contexts.get(context_id, "")

            if not file_path or not context or context == "":
                continue

            if "test" in file_path.lower():
                continue

            if numbits:
                for i, byte in enumerate(numbits):
                    for bit in range(8):
                        if byte & (1 << bit):
                            line_num = i * 8 + bit + 1
                            key = f"{file_path}:{line_num}"
                            if key not in line_contexts:
                                line_contexts[key] = set()
                            line_contexts[key].add(context)

        conn.close()

        src_path = Path(project_path)
        function_to_tests = {}

        for src_file in src_path.rglob("*.py"):
            rel_path = str(src_file.relative_to(project_path))

            if any(
                skip in rel_path
                for skip in ["test", "venv", "node_modules", ".git", "__pycache__"]
            ):
                continue

            try:
                content = src_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_key = f"{rel_path}::{node.name}"
                        tests_covering = set()

                        for line_num in range(
                            node.lineno,
                            (
                                node.end_lineno + 1
                                if hasattr(node, "end_lineno")
                                else node.lineno + 50
                            ),
                        ):
                            line_key = f"{rel_path}:{line_num}"
                            if line_key in line_contexts:
                                tests_covering.update(line_contexts[line_key])

                        if tests_covering:
                            function_to_tests[func_key] = {
                                "tests": sorted(tests_covering),
                                "test_count": len(tests_covering),
                                "has_dedicated_test": _has_dedicated_test(
                                    node.name, tests_covering
                                ),
                            }

            except (SyntaxError, IOError):
                continue

        result["function_coverage"] = function_to_tests

        for func_key, data in function_to_tests.items():
            if not data["has_dedicated_test"]:
                result["incidentally_covered"].append(
                    {
                        "function": func_key,
                        "covered_by": data["tests"][:5],
                        "reason": "No test name matches this function",
                    }
                )
            else:
                result["dedicated_tests"].append(func_key)

    except Exception as e:
        result["error"] = str(e)

    return result


# ---------------------------------------------------------------------------
# Assertion quality analysis
# ---------------------------------------------------------------------------

def _analyze_function_assertions(node: ast.FunctionDef, source: str) -> dict:
    """Analyze assertions within a test function."""
    counts = {
        "total": 0,
        "real": 0,
        "mock": 0,
        "trivial": 0,
        "pytest_raises": 0,
    }

    source_lower = source.lower()

    for child in ast.walk(node):
        if isinstance(child, ast.Assert):
            counts["total"] += 1

            assert_line = (
                ast.unparse(child) if hasattr(ast, "unparse") else str(child.test)
            )
            is_trivial = any(
                pattern.lower() in assert_line.lower()
                for pattern in ["assert True", "assert False", "is not None", "is None"]
            )

            if is_trivial:
                counts["trivial"] += 1
            else:
                counts["real"] += 1

    mock_patterns = [
        "assert_called",
        "assert_any_call",
        "assert_has_calls",
        "assert_not_called",
    ]
    for pattern in mock_patterns:
        counts["mock"] += source_lower.count(pattern)

    counts["pytest_raises"] = source_lower.count("pytest.raises") + source_lower.count(
        "with raises"
    )

    counts["total"] += counts["mock"] + counts["pytest_raises"]
    counts["real"] += counts["pytest_raises"]

    return counts


def analyze_assertion_quality(project_path: str, test_dir: str = "tests") -> dict:
    """Analyze the quality of assertions in test files.

    Detects:
    - Tests with no assertions
    - Tests with only mock assertions (assert_called, etc.)
    - Tests with trivial assertions (assert True, assert x is not None)
    - Tests with good assertions

    Returns:
        dict with weak_tests, mock_only_tests, good_tests, and summary stats
    """
    test_path = Path(project_path) / test_dir

    result = {
        "no_assertions": [],
        "mock_only": [],
        "trivial_only": [],
        "good_tests": [],
        "summary": {
            "total_tests": 0,
            "no_assertions_count": 0,
            "mock_only_count": 0,
            "trivial_only_count": 0,
            "good_tests_count": 0,
        },
    }

    if not test_path.exists():
        return result

    for test_file in test_path.rglob("test_*.py"):
        rel_path = str(test_file.relative_to(project_path))

        try:
            content = test_file.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    result["summary"]["total_tests"] += 1

                    func_lines = content.split("\n")[
                        node.lineno
                        - 1 : (
                            node.end_lineno
                            if hasattr(node, "end_lineno")
                            else node.lineno + 100
                        )
                    ]
                    func_source = "\n".join(func_lines)

                    assertion_info = _analyze_function_assertions(node, func_source)

                    test_info = {
                        "test": f"{rel_path}::{node.name}",
                        "line": node.lineno,
                        "assertions": assertion_info,
                    }

                    if assertion_info["total"] == 0:
                        result["no_assertions"].append(test_info)
                        result["summary"]["no_assertions_count"] += 1
                    elif assertion_info["real"] == 0 and assertion_info["mock"] > 0:
                        result["mock_only"].append(test_info)
                        result["summary"]["mock_only_count"] += 1
                    elif assertion_info["real"] == 0 and assertion_info["trivial"] > 0:
                        result["trivial_only"].append(test_info)
                        result["summary"]["trivial_only_count"] += 1
                    else:
                        result["good_tests"].append(test_info["test"])
                        result["summary"]["good_tests_count"] += 1

        except (SyntaxError, IOError):
            continue

    return result


# ---------------------------------------------------------------------------
# Test isolation checking
# ---------------------------------------------------------------------------

def check_test_isolation(project_path: str, test_dir: str = "tests") -> dict:
    """Check for test isolation issues that could cause flaky or order-dependent tests.

    Detects:
    - Class-level fixtures with mutable state
    - Global variable modifications
    - Singleton pattern usage
    - Database session scope issues
    """
    test_path = Path(project_path) / test_dir

    result = {
        "class_level_state": [],
        "global_modifications": [],
        "singleton_usage": [],
        "broad_scope_fixtures": [],
        "summary": {
            "total_issues": 0,
            "high_risk": 0,
            "medium_risk": 0,
        },
    }

    if not test_path.exists():
        return result

    global_mod_patterns = [
        r"global\s+\w+",
        r"os\.environ\[",
        r"sys\.path\.(append|insert)",
        r"setattr\(.*,.*,",
        r"monkeypatch\.setenv",
    ]

    singleton_patterns = [
        r"_instance\s*=",
        r"__instance\s*=",
        r"\.instance\(\)",
        r"@singleton",
        r"Singleton",
    ]

    for test_file in test_path.rglob("test_*.py"):
        rel_path = str(test_file.relative_to(project_path))

        try:
            content = test_file.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(
                                    target, ast.Name
                                ) and not target.id.startswith("_"):
                                    result["class_level_state"].append(
                                        {
                                            "file": rel_path,
                                            "class": node.name,
                                            "variable": target.id,
                                            "line": item.lineno,
                                            "risk": "high",
                                            "reason": "Class-level mutable state can leak between tests",
                                        }
                                    )
                                    result["summary"]["high_risk"] += 1
                                    result["summary"]["total_issues"] += 1

            for pattern in global_mod_patterns:
                for match in re.finditer(pattern, content):
                    line_num = content[: match.start()].count("\n") + 1
                    result["global_modifications"].append(
                        {
                            "file": rel_path,
                            "line": line_num,
                            "pattern": match.group(0)[:50],
                            "risk": "medium",
                            "reason": "Global state modification can affect other tests",
                        }
                    )
                    result["summary"]["medium_risk"] += 1
                    result["summary"]["total_issues"] += 1

            for pattern in singleton_patterns:
                for match in re.finditer(pattern, content):
                    line_num = content[: match.start()].count("\n") + 1
                    result["singleton_usage"].append(
                        {
                            "file": rel_path,
                            "line": line_num,
                            "pattern": match.group(0)[:50],
                            "risk": "medium",
                            "reason": "Singleton state persists across tests",
                        }
                    )
                    result["summary"]["medium_risk"] += 1
                    result["summary"]["total_issues"] += 1

        except (SyntaxError, IOError):
            continue

    for conftest in test_path.rglob("conftest.py"):
        rel_path = str(conftest.relative_to(project_path))

        try:
            content = conftest.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            for keyword in decorator.keywords:
                                if keyword.arg == "scope":
                                    if isinstance(keyword.value, ast.Constant):
                                        scope = keyword.value.value
                                        if scope in ("class", "module", "session"):
                                            result["broad_scope_fixtures"].append(
                                                {
                                                    "file": rel_path,
                                                    "fixture": node.name,
                                                    "scope": scope,
                                                    "line": node.lineno,
                                                    "risk": (
                                                        "high"
                                                        if scope == "session"
                                                        else "medium"
                                                    ),
                                                    "reason": f"Fixture with scope='{scope}' can cause state sharing",
                                                }
                                            )
                                            if scope == "session":
                                                result["summary"]["high_risk"] += 1
                                            else:
                                                result["summary"]["medium_risk"] += 1
                                            result["summary"]["total_issues"] += 1

        except (SyntaxError, IOError):
            continue

    return result


# ---------------------------------------------------------------------------
# Import chain analysis
# ---------------------------------------------------------------------------

def analyze_import_chains(project_path: str, test_dir: str = "tests") -> dict:
    """Analyze import chains to suggest correct mock targets.

    When you patch 'module.function', Python patches where the name is looked up,
    not where it's defined. This analyzes imports to suggest the right patch location.

    Returns:
        dict with import_map, suggested_patches, and common_mistakes
    """
    src_path = Path(project_path)
    test_path = Path(project_path) / test_dir

    result = {
        "import_map": {},
        "suggested_patches": [],
        "patch_mistakes": [],
    }

    for src_file in src_path.rglob("*.py"):
        rel_path = str(src_file.relative_to(project_path))

        if any(
            skip in rel_path
            for skip in ["test", "venv", "node_modules", ".git", "__pycache__"]
        ):
            continue

        try:
            content = src_file.read_text()
            tree = ast.parse(content)

            module_imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_imports.append(
                            {
                                "type": "import",
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            }
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for name in node.names:
                            module_imports.append(
                                {
                                    "type": "from",
                                    "module": node.module,
                                    "name": name.name,
                                    "alias": name.asname,
                                    "line": node.lineno,
                                }
                            )

            if module_imports:
                module_name = rel_path.replace("/", ".").replace(".py", "")
                result["import_map"][module_name] = module_imports

        except (SyntaxError, IOError):
            continue

    # Analyze test files for patch targets
    if test_path.exists():
        for test_file in test_path.rglob("test_*.py"):
            try:
                content = test_file.read_text()
                tree = ast.parse(content)
                rel_path = str(test_file.relative_to(project_path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for decorator in node.decorator_list:
                            target = _extract_patch_target(decorator)
                            if target:
                                # Check if this patch target matches common mistakes
                                parts = target.rsplit(".", 1)
                                if len(parts) >= 2:
                                    module_part, name_part = parts[0], parts[1]

                                    # Look for "from X import Y" patterns that suggest
                                    # patching should be at the usage site
                                    for mod_name, imports in result[
                                        "import_map"
                                    ].items():
                                        for imp in imports:
                                            if (
                                                imp["type"] == "from"
                                                and imp["name"] == name_part
                                            ):
                                                if module_part != mod_name:
                                                    suggestion = {
                                                        "test_file": rel_path,
                                                        "test_function": node.name,
                                                        "current_patch": target,
                                                        "suggested_patch": f"{mod_name}.{name_part}",
                                                        "reason": f"'{name_part}' is imported into {mod_name}, patch there instead of definition site",
                                                    }
                                                    result["suggested_patches"].append(
                                                        suggestion
                                                    )

            except (SyntaxError, IOError):
                continue

    return result
