"""Structured Java/Kotlin extractors for web and persistence patterns."""

from __future__ import annotations

import re
from typing import Any

from .common import line_number_for_offset


def _normalize_path(path: str) -> str:
    return ("/" + path).replace("//", "/").rstrip("/") or "/"


def extract_java_kotlin_routes_structured(text: str) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []

    class_mapping = re.search(r"@RequestMapping\s*\(\s*(?:value\s*=\s*)?[\"']([^\"']+)[\"']", text)
    spring_base = class_mapping.group(1) if class_mapping else ""
    spring_pattern = re.compile(r"@(Get|Post|Put|Patch|Delete)Mapping\s*\(\s*(?:value\s*=\s*)?(?:[\"']([^\"']*)[\"'])?\s*\)", re.I)
    for match in spring_pattern.finditer(text):
        method, sub_path = match.groups()
        routes.append(
            {
                "method": method.upper(),
                "path": _normalize_path((spring_base or "") + (sub_path or "")),
                "handler": "spring-handler",
                "decorator": f"{method}Mapping",
                "line": line_number_for_offset(text, match.start()),
                "source": "structured",
            }
        )

    req_mapping_pattern = re.compile(
        r"@RequestMapping\s*\([^)]*method\s*=\s*RequestMethod\.(\w+)[^)]*value\s*=\s*[\"']([^\"']+)[\"']",
        re.I,
    )
    for match in req_mapping_pattern.finditer(text):
        method, sub_path = match.groups()
        routes.append(
            {
                "method": method.upper(),
                "path": _normalize_path((spring_base or "") + sub_path),
                "handler": "spring-handler",
                "decorator": "RequestMapping",
                "line": line_number_for_offset(text, match.start()),
                "source": "structured",
            }
        )

    class_path_match = re.search(r"@Path\s*\(\s*[\"']([^\"']+)[\"']\s*\)", text)
    jaxrs_base = class_path_match.group(1) if class_path_match else ""
    resource_methods = {
        "GET": "@GET",
        "POST": "@POST",
        "PUT": "@PUT",
        "DELETE": "@DELETE",
        "PATCH": "@PATCH",
    }
    for method, marker in resource_methods.items():
        pattern = re.compile(
            rf"{re.escape(marker)}[\s\S]{{0,200}}?(?:@Path\s*\(\s*[\"']([^\"']*)[\"']\s*\))?[\s\S]{{0,400}}?(?:public|private|protected)\s+[A-Za-z0-9_<>, ?\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            re.M,
        )
        for match in pattern.finditer(text):
            sub_path, handler = match.groups()
            routes.append(
                {
                    "method": method,
                    "path": _normalize_path((jaxrs_base or "") + (sub_path or "")),
                    "handler": handler,
                    "decorator": marker.strip("@"),
                    "line": line_number_for_offset(text, match.start()),
                    "source": "structured",
                }
            )

    prefixes: dict[int, str] = {}
    route_block_pat = re.compile(r"\.?(?:route)\s*\(\s*\"([^\"]+)\"\s*\)\s*\{")
    for match in route_block_pat.finditer(text):
        prefixes[match.index + len(match.group(0))] = match.group(1)
    method_pat = re.compile(r"\b(get|post|put|patch|delete|head|options)\s*\(\s*\"([^\"]+)\"\s*\)", re.I)
    for match in method_pat.finditer(text):
        prefix = ""
        for offset, path in prefixes.items():
            if offset <= match.start():
                prefix = path
        method, sub_path = match.groups()
        routes.append(
            {
                "method": method.upper(),
                "path": _normalize_path(f"{prefix}/{sub_path}") if prefix else _normalize_path(sub_path),
                "handler": "ktor-handler",
                "decorator": f"ktor-{method}",
                "line": line_number_for_offset(text, match.start()),
                "source": "structured",
            }
        )

    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for route in routes:
        key = (route["method"], route["path"], route["decorator"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(route)
    return deduped


def extract_java_kotlin_models_structured(text: str) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []

    entity_pat = re.compile(
        r"@Entity(?:\s*\(\s*(?:name\s*=\s*)?[\"']?([A-Za-z0-9_]+)?[\"']?\s*\))?[\s\S]{0,200}?class\s+([A-Za-z_][A-Za-z0-9_]*)[\s\S]*?\{([\s\S]*?)\n\}",
        re.M,
    )
    for match in entity_pat.finditer(text):
        table_name, class_name, body = match.groups()
        fields: list[str] = []
        for field_match in re.finditer(
            r"(?:@Column\s*\([^)]*\)\s*)?(?:private|protected|public)\s+[A-Za-z0-9_<>, ?\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*;",
            body,
        ):
            field_name = field_match.group(1)
            if field_name.lower() in {"createdat", "updatedat", "deletedat"}:
                continue
            fields.append(field_name)
        models.append(
            {
                "name": table_name or class_name,
                "source": "jpa",
                "fields": fields,
                "line": line_number_for_offset(text, match.start()),
            }
        )

    exposed_pat = re.compile(r"object\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?:\w+\.)?(Table|IntIdTable|LongIdTable|UUIDTable|IdTable)\s*\([^)]*\)\s*\{", re.M)
    for match in exposed_pat.finditer(text):
        name = match.group(1)
        block_start = match.end()
        depth = 1
        i = block_start
        while i < len(text) and depth > 0:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        block = text[block_start : i - 1]
        fields: list[str] = []
        for field_match in re.finditer(r"val\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\w+)\s*\(", block):
            field_name = field_match.group(1)
            if field_name == "primaryKey":
                continue
            fields.append(field_name)
        models.append(
            {
                "name": name,
                "source": "exposed",
                "fields": fields,
                "line": line_number_for_offset(text, match.start()),
            }
        )

    return models


def extract_java_kotlin_registrations(text: str) -> list[dict[str, Any]]:
    registrations: list[dict[str, Any]] = []
    patterns = [
        ("service-registration", r"@(Service|Component|Repository)\b[\s\S]{0,120}?class\s+([A-Za-z_][A-Za-z0-9_]*)", "service"),
        ("bean-registration", r"@Bean\b[\s\S]{0,200}?(?:public|private|protected)\s+[A-Za-z0-9_<>, ?\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", "service"),
        ("resource-registration", r"@(Path|RestController|Controller)\b[\s\S]{0,120}?class\s+([A-Za-z_][A-Za-z0-9_]*)", "service"),
    ]
    for registration_type, pattern, runtime_role in patterns:
        for match in re.finditer(pattern, text, re.M):
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


def extract_java_kotlin_handlers(text: str) -> list[dict[str, Any]]:
    handlers: list[dict[str, Any]] = []
    patterns = [
        ("http-handler", r"(?:class|interface)\s+([A-Za-z_][A-Za-z0-9_]*(Resource|Controller|Endpoint))\b", "http"),
        ("command-handler", r"(?:class|interface)\s+([A-Za-z_][A-Za-z0-9_]*CommandHandler)\b", "command"),
        ("message-handler", r"(?:class|interface)\s+([A-Za-z_][A-Za-z0-9_]*(Listener|Consumer|Processor|Subscriber))\b", "messaging"),
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


def extract_java_kotlin_dispatch_bindings(text: str) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    patterns = [
        ("command-dispatch", r"\b(?:commandBus|dispatcher)\.(?:dispatch|execute|send)\s*\(", "dispatcher"),
        ("topic-subscription", r"@(?:KafkaListener|RabbitListener)\s*\([^)]*(?:topics?|queues?)\s*=\s*[\"']([^\"']+)[\"']", "consumer"),
        ("topic-publish", r"\b(?:publish|send)\s*\(\s*[\"']([^\"']+)[\"']", "producer"),
    ]
    for binding_type, pattern, role in patterns:
        for match in re.finditer(pattern, text, re.I):
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


def extract_java_kotlin_boundaries(text: str) -> list[dict[str, Any]]:
    boundaries: list[dict[str, Any]] = []
    for match in re.finditer(r"\binterface\s+([A-Za-z_][A-Za-z0-9_]*)", text):
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
        r"\b(?:class|record)\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:implements|:)\s+([A-Za-z_][A-Za-z0-9_, <>]+)",
        text,
    ):
        implementation, parents = match.groups()
        for parent in [part.strip().split("<", 1)[0] for part in parents.split(",")]:
            if not parent or not (
                parent.startswith("I")
                or parent.endswith(("Repository", "Store", "Provider", "Gateway", "Port", "Service", "Resource"))
            ):
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
    for match in re.finditer(r"\b(?:interface|class)\s+([A-Za-z_][A-Za-z0-9_]*(Repository|Store|Provider|Gateway|Port))\b", text):
        boundaries.append(
            {
                "boundary_type": "repository-boundary",
                "interface": match.group(1),
                "implementation": "",
                "storage_role": "storage",
                "line": line_number_for_offset(text, match.start()),
            }
        )
    return boundaries
