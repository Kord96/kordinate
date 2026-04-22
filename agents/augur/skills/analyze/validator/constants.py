import os
import re


def _is_truthy(value: str | None) -> bool:
    return str(value or "") in {"1", "true", "TRUE", "yes", "YES"}


KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RUN_LOG_FILE = "log.json"

REQUIRED_ATLAS_FIELDS = [
    "version",
    "generated",
    "project",
    "purpose",
    "components",
    "flows",
    "state",
    "external_dependencies",
    "failure_scenarios",
    "monitoring",
    "gaps",
    "concepts",
    "tensions",
]

CANONICAL_NARRATIVE_IDS = {
    "system-overview",
    "runtime-paths",
    "state-and-data",
    "integrations",
    "operations-and-failure",
    "extensibility",
    "security-and-access",
}

# Prefer the new flag name, but keep the historical input for compatibility.
FACTS_ONLY_MODE = _is_truthy(os.getenv("AUGUR_FACTS_ONLY_MODE")) or _is_truthy(
    os.getenv("AUGUR_DETERMINISTIC_ONLY")
)
