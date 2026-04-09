"""Structured C# extractors adapted from Codesight-style parsing."""

from __future__ import annotations

import re
from typing import Any

from .common import line_number_for_offset


def _normalize_path(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    normalized = "/" + "/".join(parts)
    return normalized or "/"


def extract_csharp_routes_structured(text: str) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    class_route_match = re.search(r"\[Route(?:Prefix)?\s*\(\s*\"([^\"]*)\"\s*\)\]", text)
    class_prefix = class_route_match.group(1) if class_route_match else ""

    for method in ("Get", "Post", "Put", "Patch", "Delete", "Options", "Head"):
        pattern = re.compile(rf"\[Http{method}(?:\s*\(\s*\"([^\"]*)\"\s*\))?\]")
        for match in pattern.finditer(text):
            sub_path = match.group(1) or ""
            if sub_path.startswith("/"):
                full_path = sub_path
            elif class_prefix and sub_path:
                full_path = f"/{class_prefix.strip('/')}/{sub_path.strip('/')}"
            elif class_prefix:
                full_path = f"/{class_prefix.strip('/')}"
            elif sub_path:
                full_path = f"/{sub_path.strip('/')}"
            else:
                full_path = "/"
            routes.append(
                {
                    "method": method.upper(),
                    "path": _normalize_path(full_path),
                    "handler": "controller-action",
                    "decorator": f"Http{method}",
                    "line": line_number_for_offset(text, match.start()),
                    "source": "structured",
                }
            )

    map_pattern = re.compile(r"\.Map(Get|Post|Put|Patch|Delete|Options|Head)\s*\(\s*\"([^\"]+)\"")
    for match in map_pattern.finditer(text):
        method, path = match.groups()
        routes.append(
            {
                "method": method.upper(),
                "path": _normalize_path(path),
                "handler": "minimal-api",
                "decorator": f"Map{method}",
                "line": line_number_for_offset(text, match.start()),
                "source": "structured",
            }
        )

    seen = set()
    deduped: list[dict[str, Any]] = []
    for route in routes:
        key = (route["method"], route["path"], route["decorator"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(route)
    return deduped


def extract_entity_framework_models(text: str) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    if "DbContext" not in text and "DbSet<" not in text:
        return models

    dbset_pattern = re.compile(r"DbSet\s*<\s*(\w+)\s*>")
    model_names = sorted({match.group(1) for match in dbset_pattern.finditer(text)})
    for name in model_names:
        class_pattern = re.compile(rf"class\s+{name}\s*(?::\s*[\w<>, ]+)?\s*\{{([\s\S]*?)\n\s*\}}", re.M)
        class_match = class_pattern.search(text)
        fields: list[str] = []
        line = 1
        if class_match:
            body = class_match.group(1)
            line = line_number_for_offset(text, class_match.start())
            prop_pattern = re.compile(
                r"(?:\[[^\]]*\]\s*)*public\s+([\w?<>, \[\]]+?)\s+(\w+)\s*\{\s*get;\s*(?:set;|init;)"
            )
            for prop_match in prop_pattern.finditer(body):
                raw_type, field_name = prop_match.groups()
                if field_name in {"CreatedAt", "UpdatedAt", "DeletedAt", "Timestamp", "RowVersion"}:
                    continue
                if re.match(r"^I?(?:Collection|List|Enumerable|Queryable)<", raw_type.strip()):
                    continue
                fields.append(field_name)
        models.append({"name": name, "source": "entity-framework", "fields": fields, "line": line})
    return models


def extract_csharp_registrations(text: str) -> list[dict[str, Any]]:
    registrations: list[dict[str, Any]] = []
    patterns = [
        ("service-registration", r"\.(AddSingleton|AddScoped|AddTransient)\s*<\s*([\w.]+)", "service"),
        ("middleware-registration", r"\.(Use[A-Z][A-Za-z0-9_]*)\s*\(", "middleware"),
    ]
    for registration_type, pattern, runtime_role in patterns:
        for match in re.finditer(pattern, text):
            symbol = match.group(2) if len(match.groups()) >= 2 else match.group(1)
            registrations.append(
                {
                    "registration_type": registration_type,
                    "symbol": symbol,
                    "target": "",
                    "runtime_role": runtime_role,
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return registrations


def extract_csharp_handlers(text: str) -> list[dict[str, Any]]:
    handlers: list[dict[str, Any]] = []
    patterns = [
        ("http-handler", r"class\s+([A-Za-z_][A-Za-z0-9_]*Controller)\b", "http"),
        ("command-handler", r"class\s+([A-Za-z_][A-Za-z0-9_]*CommandHandler)\b", "command"),
        ("message-handler", r"class\s+([A-Za-z_][A-Za-z0-9_]*(Consumer|Listener|Processor))\b", "messaging"),
    ]
    for handler_type, pattern, transport in patterns:
        for match in re.finditer(pattern, text):
            handlers.append(
                {
                    "handler_type": handler_type,
                    "name": match.group(1),
                    "target": "",
                    "transport": transport,
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return handlers


def extract_csharp_dispatch_bindings(text: str) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    patterns = [
        ("command-dispatch", r"\b(?:commandBus|dispatcher)\.(?:Send|Dispatch|ExecuteAsync|SendAsync)\s*\(", "dispatcher"),
        ("topic-publish", r"\b(?:Publish|Emit|Send)\s*\(\s*\"([^\"]+)\"", "producer"),
        ("topic-subscription", r"\b(?:Subscribe|OnMessage|AddHandler)\s*\(\s*\"([^\"]+)\"", "consumer"),
    ]
    for binding_type, pattern, role in patterns:
        for match in re.finditer(pattern, text):
            channel = match.group(1) if match.groups() else ""
            bindings.append(
                {
                    "binding_type": binding_type,
                    "channel": channel,
                    "producer_or_consumer": role,
                    "target": "",
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return bindings


def extract_csharp_boundaries(text: str) -> list[dict[str, Any]]:
    boundaries: list[dict[str, Any]] = []
    for match in re.finditer(r"(?:public\s+)?interface\s+([A-Za-z_][A-Za-z0-9_]*)", text):
        boundaries.append(
            {
                "boundary_type": "interface",
                "interface": match.group(1),
                "implementation": "",
                "storage_role": "interface",
                "line": line_number_for_offset(text, match.start()),
            }
        )
    for match in re.finditer(
        r"(?:public\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z_][A-Za-z0-9_, ]+)",
        text,
    ):
        implementation, parents = match.groups()
        for parent in [part.strip() for part in parents.split(",")]:
            if not parent or parent in {"Controller", "ControllerBase"}:
                continue
            boundaries.append(
                {
                    "boundary_type": "implementation",
                    "interface": parent,
                    "implementation": implementation,
                    "storage_role": "implementation",
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return boundaries
