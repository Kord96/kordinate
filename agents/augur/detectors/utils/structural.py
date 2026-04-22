"""Structural fact-family extractors."""

from __future__ import annotations

import re
from typing import Any

from .common import line_number_for_offset


def extract_registrations(text: str, suffix: str) -> list[dict[str, Any]]:
    del suffix
    registrations: list[dict[str, Any]] = []
    patterns = [
        (
            "plugin-registration",
            r"\b(registerPlugin|RegisterPlugin|plugin[s]?\.(add|register)|extension[s]?\.(add|register))\b",
            "plugin",
        ),
        (
            "workflow-registration",
            r"\b(RegisterWorkflow|registerWorkflow|workflow\.Register|worker\.RegisterWorkflow)\b",
            "workflow",
        ),
        (
            "activity-registration",
            r"\b(RegisterActivity|registerActivity|worker\.RegisterActivity)\b",
            "activity",
        ),
        (
            "service-registration",
            r"\b(AddSingleton|AddScoped|AddTransient|registerService|ServiceCollection|Provide\(|fx\.Provide|wire\.Bind)\b",
            "service",
        ),
    ]
    for registration_type, pattern, runtime_role in patterns:
        for match in re.finditer(pattern, text, re.I):
            registrations.append(
                {
                    "registration_type": registration_type,
                    "symbol": match.group(1) if match.groups() else match.group(0),
                    "target": "",
                    "runtime_role": runtime_role,
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return registrations


def extract_handlers(text: str, suffix: str) -> list[dict[str, Any]]:
    handlers: list[dict[str, Any]] = []
    if suffix in {".java", ".kt", ".kts", ".cs", ".cpp", ".cc", ".cxx", ".h", ".hpp"}:
        patterns = [
            ("http-handler", r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*(Controller|Handler))\b", "http"),
            ("message-handler", r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*(Consumer|Subscriber|Listener|Processor))\b", "messaging"),
            ("command-handler", r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*CommandHandler)\b", "command"),
        ]
    elif suffix == ".go":
        patterns = [
            ("grpc-handler", r"\b(Register[A-Za-z0-9_]*Server|[A-Za-z_][A-Za-z0-9_]*Server)\b", "grpc"),
            ("workflow-handler", r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*(Workflow|Activity))\s*\(", "workflow"),
            ("message-handler", r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*(Consumer|Subscriber|Listener|Processor))\s*\(", "messaging"),
            ("go-handle-func", r"\bHandleFunc\s*\(\s*\"([^\"]+)\"", "http"),
        ]
    else:
        patterns = [
            ("http-handler", r"\b([A-Za-z_][A-Za-z0-9_]*(Handler|Controller))\b", "http"),
            ("grpc-handler", r"\b(Register[A-Za-z0-9_]*Server|[A-Za-z_][A-Za-z0-9_]*Server)\b", "grpc"),
            ("workflow-handler", r"\b([A-Za-z_][A-Za-z0-9_]*(Workflow|Activity))\b", "workflow"),
            ("message-handler", r"\b([A-Za-z_][A-Za-z0-9_]*(Consumer|Subscriber|Listener|Processor))\b", "messaging"),
            ("command-handler", r"\b([A-Za-z_][A-Za-z0-9_]*CommandHandler)\b", "command"),
            ("go-handle-func", r"\bHandleFunc\s*\(\s*\"([^\"]+)\"", "http"),
        ]
    for handler_type, pattern, transport in patterns:
        for match in re.finditer(pattern, text):
            name = match.group(1) if match.groups() else match.group(0)
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


def extract_dispatch_bindings(text: str, suffix: str) -> list[dict[str, Any]]:
    del suffix
    bindings: list[dict[str, Any]] = []
    patterns = [
        ("topic-subscription", r"\b(Subscribe|subscribe|OnMessage|AddHandler)\s*\(\s*[\"'`]([^\"'`]+)[\"'`]", "consumer"),
        ("topic-publish", r"\b(Publish|publish|Emit|emit|Send)\s*\(\s*[\"'`]([^\"'`]+)[\"'`]", "producer"),
        ("queue-binding", r"\b(queue|topic|subject|channel)\s*[:=]\s*[\"'`]([^\"'`]+)[\"'`]", "binding"),
        ("command-dispatch", r"\b(commandBus|dispatcher|Dispatch|ExecuteAsync|SendAsync)\b", "dispatcher"),
    ]
    for binding_type, pattern, role in patterns:
        for match in re.finditer(pattern, text, re.I):
            channel = match.group(2) if len(match.groups()) >= 2 else ""
            bindings.append(
                {
                    "binding_type": binding_type,
                    "channel": channel,
                    "producer_or_consumer": role,
                    "target": match.group(1) if match.groups() else "",
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return bindings


def extract_boundaries(text: str, suffix: str) -> list[dict[str, Any]]:
    boundaries: list[dict[str, Any]] = []
    repo_pattern = r"\b([A-Za-z_][A-Za-z0-9_]*(Repository|Store|Provider|Gateway|Port))\b"
    if suffix in {".java", ".kt", ".kts", ".cs", ".cpp", ".cc", ".cxx", ".h", ".hpp"}:
        repo_pattern = r"\b(?:class|interface|record|struct)\s+([A-Za-z_][A-Za-z0-9_]*(Repository|Store|Provider|Gateway|Port))\b"
    patterns = [
        ("interface", r"\binterface\s+([A-Za-z_][A-Za-z0-9_]*)", "interface"),
        ("repository-boundary", repo_pattern, "storage"),
        ("go-interface", r"\btype\s+([A-Za-z_][A-Za-z0-9_]*)\s+interface\s*\{", "interface"),
    ]
    for boundary_type, pattern, storage_role in patterns:
        for match in re.finditer(pattern, text):
            interface = match.group(1) if match.groups() else ""
            implementation = match.group(2).strip() if len(match.groups()) >= 2 else ""
            boundaries.append(
                {
                    "boundary_type": boundary_type,
                    "interface": interface,
                    "implementation": implementation,
                    "storage_role": storage_role,
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    if suffix in {".java", ".kt", ".kts"}:
        impl_pattern = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s+implements\s+([A-Za-z_][A-Za-z0-9_, ]+)")
        for match in impl_pattern.finditer(text):
            implementation, parents = match.groups()
            for parent in [part.strip() for part in parents.split(",")]:
                if not parent or not (
                    parent.startswith("I")
                    or parent.endswith(("Repository", "Store", "Provider", "Gateway", "Port", "Strategy"))
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
    return boundaries
