"""
Mock analysis utilities.

Provides:
- analyze_mock_completeness: Find potentially unmocked external dependencies
- analyze_mock_interface_mismatches: Detect mock/real interface mismatches

Extracted from nokrashi-tools (Kord96/nokrashi-tools, archived).
"""

import ast
import re
from pathlib import Path

MOCKABLE_PATTERNS = {
    "database": [
        r"\.query\(",
        r"\.execute\(",
        r"\.commit\(",
        r"\.rollback\(",
        r"session\.",
        r"engine\.",
        r"cursor\.",
        r"\.get_service\(",
        r"\.get_service_config\(",
    ],
    "network": [
        r"requests\.(get|post|put|delete|patch)",
        r"httpx\.",
        r"aiohttp\.",
        r"urllib\.",
        r"\.fetch\(",
    ],
    "filesystem": [
        r"open\(",
        r"Path\(.*\)\.(read|write)",
        r"\.read_text\(",
        r"\.write_text\(",
        r"os\.(remove|unlink|mkdir|rmdir)",
    ],
    "subprocess": [
        r"subprocess\.(run|call|Popen)",
        r"os\.system\(",
        r"os\.popen\(",
    ],
    "time": [
        r"time\.(sleep|time)",
        r"datetime\.now\(",
        r"datetime\.utcnow\(",
    ],
    "external_service": [
        r"is_service_running\(",
        r"get_status\(",
        r"health_check\(",
    ],
}


def _extract_patch_target(decorator) -> str | None:
    """Extract the target string from a @patch decorator."""
    if isinstance(decorator, ast.Call):
        func_name = ""
        if isinstance(decorator.func, ast.Attribute):
            func_name = decorator.func.attr
        elif isinstance(decorator.func, ast.Name):
            func_name = decorator.func.id

        if func_name == "patch" and decorator.args:
            if isinstance(decorator.args[0], ast.Constant):
                return decorator.args[0].value
    return None


def _find_containing_function(content: str, position: int) -> str:
    """Find the function name containing the given position."""
    lines = content[:position].split("\n")
    for line in reversed(lines):
        line = line.strip()
        if line.startswith("def "):
            match = re.match(r"def\s+(\w+)", line)
            if match:
                return match.group(1)
        elif line.startswith("class "):
            break
    return "unknown"


def analyze_mock_completeness(project_path: str, test_dir: str = "tests") -> dict:
    """Analyze whether tests have complete mocks for external dependencies.

    This function:
    1. Finds all @patch decorators and mock.patch() calls in tests
    2. Analyzes the source files being tested for external calls
    3. Identifies potentially unmocked external dependencies

    Returns:
        dict with:
            - mocked_targets: list of what's being mocked
            - potential_gaps: list of external calls that might need mocking
            - analysis_per_file: per-test-file analysis
    """
    test_path = Path(project_path) / test_dir
    src_path = Path(project_path)

    result = {
        "mocked_targets": [],
        "potential_gaps": [],
        "analysis_per_file": {},
        "summary": {},
    }

    if not test_path.exists():
        return result

    # Collect all mocked targets from test files
    mocked_targets = set()

    for test_file in test_path.rglob("test_*.py"):
        try:
            content = test_file.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Find @patch decorators
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        target = _extract_patch_target(decorator)
                        if target:
                            mocked_targets.add(target)

                # Find patch() calls in context managers
                if isinstance(node, ast.Call):
                    func_name = ""
                    if isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr
                    elif isinstance(node.func, ast.Name):
                        func_name = node.func.id

                    if func_name == "patch" and node.args:
                        if isinstance(node.args[0], ast.Constant):
                            mocked_targets.add(node.args[0].value)

        except (SyntaxError, IOError):
            continue

    result["mocked_targets"] = sorted(mocked_targets)

    # Analyze source files for external calls that might need mocking
    potential_gaps = []

    for src_file in src_path.rglob("*.py"):
        rel_path = str(src_file.relative_to(project_path))

        # Skip test files and common non-source directories
        if any(
            skip in rel_path
            for skip in ["test", "venv", "node_modules", ".git", "__pycache__"]
        ):
            continue

        try:
            content = src_file.read_text()

            for category, patterns in MOCKABLE_PATTERNS.items():
                for pattern in patterns:
                    matches = list(re.finditer(pattern, content))
                    if matches:
                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1
                            call_text = match.group(0)

                            # Check if this is mocked
                            is_mocked = False
                            for target in mocked_targets:
                                if (
                                    call_text.strip("(.") in target
                                    or rel_path.replace("/", ".").replace(".py", "")
                                    in target
                                ):
                                    is_mocked = True
                                    break

                            if not is_mocked:
                                func_name = _find_containing_function(
                                    content, match.start()
                                )

                                potential_gaps.append(
                                    {
                                        "file": rel_path,
                                        "line": line_num,
                                        "category": category,
                                        "call": call_text,
                                        "function": func_name,
                                        "suggestion": f"Consider mocking {category} call in {rel_path}:{line_num}",
                                    }
                                )

        except (IOError, UnicodeDecodeError):
            continue

    # Deduplicate and limit gaps
    seen = set()
    unique_gaps = []
    for gap in potential_gaps:
        key = (gap["file"], gap["line"], gap["call"])
        if key not in seen:
            seen.add(key)
            unique_gaps.append(gap)

    # Sort by category priority
    category_priority = {
        "database": 0,
        "external_service": 1,
        "network": 2,
        "subprocess": 3,
        "filesystem": 4,
        "time": 5,
    }
    unique_gaps.sort(
        key=lambda x: (category_priority.get(x["category"], 99), x["file"], x["line"])
    )

    result["potential_gaps"] = unique_gaps[:50]

    # Summary
    result["summary"] = {
        "total_mocked": len(mocked_targets),
        "potential_gaps_found": len(unique_gaps),
        "gaps_by_category": {},
    }

    for gap in unique_gaps:
        cat = gap["category"]
        result["summary"]["gaps_by_category"][cat] = (
            result["summary"]["gaps_by_category"].get(cat, 0) + 1
        )

    return result


def _index_source_classes(src_path: Path, project_path: str) -> dict:
    """Build an index of classes/functions and their methods from source files."""
    index = {}

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
                if isinstance(node, ast.ClassDef):
                    methods = set()
                    attributes = set()

                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.add(item.name)
                        elif isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    attributes.add(target.id)

                    module_path = rel_path.replace("/", ".").replace(".py", "")
                    full_name = f"{module_path}.{node.name}"

                    index[node.name] = {
                        "file": rel_path,
                        "methods": methods,
                        "attributes": attributes,
                        "full_name": full_name,
                    }
                    index[full_name] = index[node.name]

        except (SyntaxError, IOError):
            continue

    return index


def _get_attribute_chain(node: ast.Attribute) -> tuple:
    """Get the root name and attribute chain from an ast.Attribute node."""
    attrs = []
    current = node

    while isinstance(current, ast.Attribute):
        attrs.insert(0, current.attr)
        current = current.value

    if isinstance(current, ast.Name):
        return current.id, attrs

    return None, []


def _extract_mock_configurations(func_node: ast.FunctionDef) -> dict:
    """Extract what methods/attributes are configured on mock objects in a test."""
    configs = {}

    param_names = set(arg.arg for arg in func_node.args.args)
    mock_vars = set(param_names)

    for node in ast.walk(func_node):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call):
                func_name = ""
                if isinstance(node.value.func, ast.Name):
                    func_name = node.value.func.id
                elif isinstance(node.value.func, ast.Attribute):
                    func_name = node.value.func.attr

                if func_name in ("MagicMock", "Mock", "create_autospec"):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            mock_vars.add(target.id)

            if isinstance(node.value, ast.Attribute):
                root, _ = _get_attribute_chain(node.value)
                if root in mock_vars:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            mock_vars.add(target.id)

    for var in mock_vars:
        configs[var] = []

    for node in ast.walk(func_node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    root, attrs = _get_attribute_chain(target)
                    if root in mock_vars and attrs:
                        configs[root].append(
                            {
                                "method": attrs[0],
                                "full_chain": attrs,
                            }
                        )

    return configs


def _find_methods_called_on_target(
    patch_target: str, attr_name: str, src_path: Path, project_path: str
) -> set:
    """Find what methods are actually called on a patched target in source code."""
    methods = set()

    parts = patch_target.rsplit(".", 1)
    if len(parts) < 2:
        return methods

    module_path = parts[0].replace(".", "/") + ".py"
    target_file = src_path / module_path

    if not target_file.exists():
        parts = parts[0].rsplit(".", 1)
        if len(parts) >= 1:
            module_path = parts[0].replace(".", "/") + ".py"
            target_file = src_path / module_path

    if not target_file.exists():
        return methods

    try:
        content = target_file.read_text()
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    root, attrs = _get_attribute_chain(node.func)
                    if attrs:
                        methods.add(node.func.attr)

                    if isinstance(node.func.value, ast.Attribute):
                        if node.func.value.attr == attr_name or attr_name in str(
                            ast.dump(node.func.value)
                        ):
                            methods.add(node.func.attr)

    except (SyntaxError, IOError):
        pass

    return methods


def _find_mocks_without_spec(func_node: ast.FunctionDef, test_file: str) -> list:
    """Find MagicMock() calls without spec= argument."""
    missing = []

    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name == "MagicMock":
                has_spec = any(
                    kw.arg in ("spec", "spec_set", "autospec") for kw in node.keywords
                )
                if not has_spec:
                    missing.append(
                        {
                            "test_file": test_file,
                            "test_function": func_node.name,
                            "line": node.lineno,
                            "suggestion": "MagicMock without spec= can silently accept wrong method names",
                        }
                    )

    return missing


def _find_stale_mocks(test_path: Path, source_classes: dict, project_path: str) -> list:
    """Find mocks that reference non-existent methods or classes."""
    stale = []

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
                            parts = target.rsplit(".", 1)
                            if len(parts) >= 2:
                                class_or_module = parts[0].split(".")[-1]
                                method_name = parts[1]

                                if class_or_module in source_classes:
                                    class_info = source_classes[class_or_module]
                                    if (
                                        method_name not in class_info["methods"]
                                        and method_name not in class_info["attributes"]
                                    ):
                                        stale.append(
                                            {
                                                "test_file": rel_path,
                                                "test_function": node.name,
                                                "line": node.lineno,
                                                "patch_target": target,
                                                "reason": f"'{method_name}' not found in {class_or_module}",
                                            }
                                        )

        except (SyntaxError, IOError):
            continue

    return stale


def _analyze_test_mocks(
    func_node: ast.FunctionDef,
    content: str,
    test_file: str,
    source_classes: dict,
    src_path: Path,
    project_path: str,
) -> list:
    """Analyze a test function for mock interface mismatches."""
    mismatches = []

    patch_targets = []
    for decorator in func_node.decorator_list:
        target = _extract_patch_target(decorator)
        if target:
            patch_targets.append(target)

    if not patch_targets:
        return mismatches

    mock_configs = _extract_mock_configurations(func_node)

    for target in patch_targets:
        parts = target.rsplit(".", 1)
        if len(parts) < 2:
            continue

        module_path, attr_name = parts

        real_methods = _find_methods_called_on_target(
            target, attr_name, src_path, project_path
        )

        if not real_methods:
            continue

        for param_name, configured_attrs in mock_configs.items():
            if not configured_attrs:
                continue

            for config in configured_attrs:
                configured_method = config.get("method")
                if configured_method and configured_method not in real_methods:
                    if configured_method not in (
                        "return_value",
                        "side_effect",
                        "__class__",
                    ):
                        mismatches.append(
                            {
                                "test_file": test_file,
                                "test_function": func_node.name,
                                "line": func_node.lineno,
                                "patch_target": target,
                                "mock_configures": configured_method,
                                "real_code_calls": list(real_methods)[:5],
                                "severity": "high" if real_methods else "medium",
                                "suggestion": f"Mock configures '{configured_method}' but real code calls: {', '.join(list(real_methods)[:3])}",
                            }
                        )

    return mismatches


def analyze_mock_interface_mismatches(
    project_path: str, test_dir: str = "tests"
) -> dict:
    """Detect tests where mock setup doesn't match what the real code calls.

    For each test that patches an object:
    1. Extract what methods/attributes are configured on the mock
    2. Find the real implementation being tested
    3. Extract what methods the real code actually calls
    4. Flag mismatches

    Example detection:
    - Test sets: mock_consumer.__iter__ = ...
    - Real code: self._consumer.poll(timeout_ms=5000)
    - Mismatch: "Mock configures __iter__ but code calls poll()"

    Returns:
        dict with:
            - mismatches: list of detected mismatches
            - summary: counts by category
    """
    test_path = Path(project_path) / test_dir
    src_path = Path(project_path)

    result = {
        "mismatches": [],
        "stale_mocks": [],
        "missing_spec": [],
        "summary": {
            "total_mismatches": 0,
            "total_stale": 0,
            "total_missing_spec": 0,
        },
    }

    if not test_path.exists():
        return result

    source_classes = _index_source_classes(src_path, project_path)

    for test_file in test_path.rglob("test_*.py"):
        try:
            content = test_file.read_text()
            tree = ast.parse(content)
            rel_path = str(test_file.relative_to(project_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    mismatches = _analyze_test_mocks(
                        node, content, rel_path, source_classes, src_path, project_path
                    )
                    result["mismatches"].extend(mismatches)

                    missing_spec = _find_mocks_without_spec(node, rel_path)
                    result["missing_spec"].extend(missing_spec)

        except (SyntaxError, IOError):
            continue

    result["stale_mocks"] = _find_stale_mocks(test_path, source_classes, project_path)

    result["summary"]["total_mismatches"] = len(result["mismatches"])
    result["summary"]["total_stale"] = len(result["stale_mocks"])
    result["summary"]["total_missing_spec"] = len(result["missing_spec"])

    return result
