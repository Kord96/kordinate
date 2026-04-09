"""Fact-family extraction helpers for deterministic Augur extraction."""

from .common import line_number_for_offset
from .csharp_structured import (
    extract_csharp_boundaries,
    extract_csharp_dispatch_bindings,
    extract_csharp_handlers,
    extract_csharp_registrations,
    extract_csharp_routes_structured,
    extract_entity_framework_models,
)
from .go_structured import (
    extract_go_boundaries,
    extract_go_dispatch_bindings,
    extract_go_gorm_models,
    extract_go_handlers,
    extract_go_registrations,
    extract_go_routes_structured,
)
from .runtime_signals import (
    extract_auth_surfaces,
    extract_config_sources,
    extract_events,
    extract_jobs,
)
from .structural import (
    extract_boundaries,
    extract_dispatch_bindings,
    extract_handlers,
    extract_registrations,
)

__all__ = [
    "extract_auth_surfaces",
    "extract_csharp_boundaries",
    "extract_csharp_dispatch_bindings",
    "extract_csharp_handlers",
    "extract_csharp_registrations",
    "extract_csharp_routes_structured",
    "extract_entity_framework_models",
    "extract_boundaries",
    "extract_config_sources",
    "extract_dispatch_bindings",
    "extract_events",
    "extract_go_boundaries",
    "extract_go_dispatch_bindings",
    "extract_go_gorm_models",
    "extract_go_handlers",
    "extract_go_registrations",
    "extract_go_routes_structured",
    "extract_handlers",
    "extract_jobs",
    "extract_registrations",
    "line_number_for_offset",
]
