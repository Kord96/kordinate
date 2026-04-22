"""Plugin/extensibility-oriented fact extractors."""

from __future__ import annotations

import re
from typing import Any

from .common import line_number_for_offset


def has_plugin_context(text: str, suffix: str) -> bool:
    lowered = text.lower()
    anchors = [
        "plugininstances",
        "plugin_instances",
        "plugindirectory",
        "pluginid",
        "pluginname",
        "loadplugin",
        "load_plugin",
        "unloadplugin",
        "wox_plugin",
        "pluginapi",
        "registerquerycommands",
    ]
    if any(anchor in lowered for anchor in anchors):
        return True
    if suffix == ".json" and '"TriggerKeywords"' in text and '"Entry"' in text:
        return True
    return False


def extract_plugin_registrations(text: str, suffix: str) -> list[dict[str, Any]]:
    if not has_plugin_context(text, suffix):
        return []
    registrations: list[dict[str, Any]] = []
    patterns = [
        ("plugin-load", r"\b(loadPlugin|load_plugin|LoadPlugin)\b", "plugin"),
        ("plugin-init", r"\b(initPlugin|init_plugin|OnPluginSettingChanged|RegisterQueryCommands)\b", "plugin"),
        ("plugin-instance-registry", r"\b(pluginInstances|plugin_instances)\b", "plugin"),
        ("plugin-api-surface", r"\b(class\s+PluginAPI|interface\s+PublicAPI|implements\s+PublicAPI)\b", "plugin"),
    ]
    for registration_type, pattern, runtime_role in patterns:
        for match in re.finditer(pattern, text):
            registrations.append(
                {
                    "registration_type": registration_type,
                    "symbol": match.group(1) if match.groups() else match.group(0),
                    "target": "",
                    "runtime_role": runtime_role,
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    if suffix == ".json" and '"TriggerKeywords"' in text and '"Entry"' in text:
        for match in re.finditer(r'"(Id|Name|TriggerKeywords|Entry)"\s*:', text):
            registrations.append(
                {
                    "registration_type": "plugin-manifest",
                    "symbol": match.group(1),
                    "target": "",
                    "runtime_role": "plugin",
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return registrations


def extract_plugin_dispatch_bindings(text: str, suffix: str) -> list[dict[str, Any]]:
    if not has_plugin_context(text, suffix):
        return []
    bindings: list[dict[str, Any]] = []
    patterns = [
        (
            "plugin-rpc-method",
            r"(?:Method\s*[:=]\s*[\"'](loadPlugin|init|query|action|formAction|unloadPlugin|onPluginSettingChange|onGetDynamicSetting|onDeepLink|onMRURestore|onLLMStream)[\"']|method\s*==\s*[\"'](loadPlugin|init|query|action|formAction|unloadPlugin|onPluginSettingChange|onGetDynamicSetting|onDeepLink|onMRURestore|onLLMStream)[\"'])",
            "dispatcher",
        ),
        ("plugin-message-type", r"(?:PluginId|PluginName|PluginDirectory|CallbackId)\b", "binding"),
        ("plugin-ws-send", r"\bws\.send\s*\(", "producer"),
        ("plugin-response-wait", r"\b(waitingForResponse|waiting_for_response)\b", "consumer"),
    ]
    for binding_type, pattern, role in patterns:
        for match in re.finditer(pattern, text):
            channel = ""
            if match.groups():
                for group in match.groups():
                    if group:
                        channel = group
                        break
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


def extract_plugin_boundaries(text: str, suffix: str) -> list[dict[str, Any]]:
    if not has_plugin_context(text, suffix):
        return []
    boundaries: list[dict[str, Any]] = []
    patterns = [
        ("plugin-host-boundary", r"\b(plugin_host|plugin\.host|PluginAPI|PluginInstance|pluginInstances|plugin_instances)\b"),
        ("plugin-sdk-boundary", r"\b(wox_plugin|wox-plugin|PublicAPI|PluginInitParams|RegisterQueryCommands)\b"),
        ("plugin-manifest-boundary", r"\b(plugin\.json|TriggerKeywords)\b"),
    ]
    for boundary_type, pattern in patterns:
        for match in re.finditer(pattern, text, re.I):
            boundaries.append(
                {
                    "boundary_type": boundary_type,
                    "interface": match.group(0),
                    "implementation": "",
                    "storage_role": "plugin",
                    "line": line_number_for_offset(text, match.start()),
                }
            )
    return boundaries
