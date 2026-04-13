"""Structured Go extractors adapted from Codesight-style parsing."""

from __future__ import annotations

import re
from typing import Any

from .common import line_number_for_offset


def _normalize_path(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    normalized = "/" + "/".join(parts)
    return normalized or "/"


def extract_go_routes_structured(text: str) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    prefix_map: dict[str, str] = {}
    group_pattern = re.compile(r"(\w+)\s*:?=\s*(\w+)\.Group\s*\(\s*\"([^\"]*)\"")

    for match in group_pattern.finditer(text):
        var_name, receiver, prefix = match.groups()
        receiver_prefix = prefix_map.get(receiver, "")
        prefix_map[var_name] = _normalize_path(f"{receiver_prefix}/{prefix}")

    for var_name, prefix in prefix_map.items():
        route_pattern = re.compile(
            rf"{re.escape(var_name)}\s*\.\s*(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD|Get|Post|Put|Patch|Delete|Options|Head)\s*\(\s*\"([^\"]*)\"\s*,\s*([A-Za-z_][A-Za-z0-9_.]*)"
        )
        for match in route_pattern.finditer(text):
            method, path, handler = match.groups()
            routes.append(
                {
                    "method": method.upper(),
                    "path": _normalize_path(f"{prefix}/{path}"),
                    "handler": handler,
                    "decorator": "go-group-route",
                    "line": line_number_for_offset(text, match.start()),
                    "source": "structured",
                }
            )

    top_level_patterns = [
        (
            "route",
            re.compile(
                r"\.\s*(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD|Get|Post|Put|Patch|Delete|Options|Head)\s*\(\s*\"([^\"]*)\"\s*,\s*([A-Za-z_][A-Za-z0-9_.]*)"
            ),
        ),
        (
            "handle-func",
            re.compile(r"\.\s*HandleFunc\s*\(\s*\"([^\"]+)\"\s*,\s*([A-Za-z_][A-Za-z0-9_.]*)"),
        ),
        (
            "handle",
            re.compile(r"\.\s*Handle\s*\(\s*\"([^\"]+)\"\s*,\s*([A-Za-z_][A-Za-z0-9_.]*)"),
        ),
    ]
    seen = {(route["method"], route["path"], route["handler"]) for route in routes}

    for pattern_kind, pattern in top_level_patterns:
        for match in pattern.finditer(text):
            if pattern_kind in {"handle-func", "handle"}:
                path, handler = match.groups()
                method = "ALL"
                method_match = re.match(r"^(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\s+(\/.*)", path)
                if method_match:
                    method, path = method_match.groups()
                route = {
                    "method": method.upper(),
                    "path": _normalize_path(path),
                    "handler": handler,
                    "decorator": "go-handle",
                    "line": line_number_for_offset(text, match.start()),
                    "source": "structured",
                }
            else:
                method, path, handler = match.groups()
                route = {
                    "method": method.upper(),
                    "path": _normalize_path(path),
                    "handler": handler,
                    "decorator": "go-route",
                    "line": line_number_for_offset(text, match.start()),
                    "source": "structured",
                }
            key = (route["method"], route["path"], route["handler"])
            if key not in seen:
                routes.append(route)
                seen.add(key)

    return routes


def extract_go_gorm_models(text: str) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    struct_pattern = re.compile(r"type\s+([A-Za-z_][A-Za-z0-9_]*)\s+struct\s*\{([\s\S]*?)\n\}", re.M)

    for match in struct_pattern.finditer(text):
        name, body = match.groups()
        if "gorm.Model" not in body and "gorm:" not in body and "`json:" not in body:
            continue
        fields: list[str] = []
        for field_match in re.finditer(r"^\s*([A-Z][A-Za-z0-9_]*)\s+([^\s`]+)(?:\s+`([^`]+)`)?", body, re.M):
            field_name = field_match.group(1)
            field_type = field_match.group(2)
            if field_name in {"Model", "CreatedAt", "UpdatedAt", "DeletedAt"}:
                continue
            if field_type.startswith("[]") and not field_name.endswith("ID"):
                continue
            fields.append(field_name)
        models.append(
            {
                "name": name,
                "source": "gorm",
                "fields": fields,
                "line": line_number_for_offset(text, match.start()),
            }
        )
    return models


def extract_go_registrations(text: str) -> list[dict[str, Any]]:
    registrations: list[dict[str, Any]] = []
    patterns = [
        ("workflow-registration", r"\b(\w+)\.RegisterWorkflow\s*\(\s*([A-Za-z_][A-Za-z0-9_.]*)", "workflow"),
        ("activity-registration", r"\b(\w+)\.RegisterActivity\s*\(\s*([A-Za-z_][A-Za-z0-9_.]*)", "activity"),
        ("grpc-service-registration", r"\bRegister([A-Za-z0-9_]+)Server\s*\(\s*[^,]+,\s*([A-Za-z_][A-Za-z0-9_.]*)", "service"),
        ("service-registration", r"\b(fx\.Provide|wire\.Bind|wire\.NewSet|Provide)\s*\(", "service"),
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


def extract_go_handlers(text: str) -> list[dict[str, Any]]:
    handlers: list[dict[str, Any]] = []
    patterns = [
        ("grpc-handler", r"\bRegister([A-Za-z0-9_]+)Server\s*\(", "grpc"),
        ("workflow-handler", r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*error", "workflow"),
        ("http-handler", r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*Handler)\s*\(", "http"),
        ("message-handler", r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*(Consumer|Listener|Processor))\s*\(", "messaging"),
    ]
    for handler_type, pattern, transport in patterns:
        for match in re.finditer(pattern, text):
            name = match.group(1)
            handlers.append(
                {
                    "handler_type": handler_type,
                    "name": name,
                    "target": "",
                    "transport": transport,
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return handlers


def extract_go_dispatch_bindings(text: str) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    patterns = [
        ("topic-subscription", r"\b(?:Consume|Subscribe|RegisterHandler)\s*\(\s*\"([^\"]+)\"", "consumer"),
        ("topic-publish", r"\b(?:Publish|Emit|Send)\s*\(\s*\"([^\"]+)\"", "producer"),
        ("queue-binding", r"\b(?:TaskQueue|Queue|Topic)\s*:\s*\"([^\"]+)\"", "binding"),
    ]
    for binding_type, pattern, role in patterns:
        for match in re.finditer(pattern, text):
            bindings.append(
                {
                    "binding_type": binding_type,
                    "channel": match.group(1),
                    "producer_or_consumer": role,
                    "target": "",
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return bindings


def extract_go_boundaries(text: str) -> list[dict[str, Any]]:
    boundaries: list[dict[str, Any]] = []
    for match in re.finditer(r"type\s+([A-Za-z_][A-Za-z0-9_]*)\s+interface\s*\{", text):
        name = match.group(1)
        boundaries.append(
            {
                "boundary_type": "go-interface",
                "interface": name,
                "implementation": "",
                "storage_role": "interface",
                "line": line_number_for_offset(text, match.start()),
            }
        )
    for match in re.finditer(r"type\s+([A-Za-z_][A-Za-z0-9_]*(Repository|Store|Provider))\s+struct\s*\{", text):
        name = match.group(1)
        boundaries.append(
            {
                "boundary_type": "repository-boundary",
                "interface": name,
                "implementation": "",
                "storage_role": "storage",
                "line": line_number_for_offset(text, match.start()),
            }
        )
    return boundaries
