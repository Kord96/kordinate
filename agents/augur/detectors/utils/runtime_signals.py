"""Runtime-oriented fact-family extractors."""

from __future__ import annotations

import re
from typing import Any


def extract_auth_surfaces(text: str, suffix: str) -> list[dict[str, Any]]:
    del suffix
    surfaces: list[dict[str, Any]] = []
    patterns = [
        ("oauth-oidc", r"\boauth\b|\boidc\b|\bopenid\b"),
        ("jwt", r"\bjwt\b|\bbearer\b"),
        ("session-auth", r"\bsession\b|\bcookie\b"),
        ("api-key-auth", r"x-api-key|api[_-]?key"),
        ("rbac", r"\brbac\b|\brole\b|\bpermission\b"),
        ("route-guard", r"\bguard\b|\bauthorize\b|\brequireAuth\b|@UseGuards\b"),
    ]
    lowered = text.lower()
    for kind, pattern in patterns:
        if re.search(pattern, lowered, re.I):
            surfaces.append({"technology": kind, "auth": kind})
    return surfaces


def extract_config_sources(text: str, suffix: str) -> list[dict[str, Any]]:
    del suffix
    configs: list[dict[str, Any]] = []
    patterns = [
        ("env", r"process\.env|os\.environ|getenv\(|environ\["),
        ("dotenv", r"\bdotenv\b|load_dotenv"),
        ("yaml", r"\.ya?ml\b|safe_load\(|yaml\."),
        ("json", r"\.json\b|json\.load"),
        ("service-url", r"https?://[^\s\"'`>]+|[A-Z0-9_]+_URL\b"),
        ("secret", r"\bsecret\b|\btoken\b|\bpassword\b|\bapi[_-]?key\b"),
    ]
    lowered = text.lower()
    for source_type, pattern in patterns:
        if re.search(pattern, text if "URL" in pattern else lowered, re.I):
            configs.append({"source_type": source_type})
    return configs


def extract_jobs(text: str, suffix: str) -> list[dict[str, Any]]:
    del suffix
    jobs: list[dict[str, Any]] = []
    patterns = [
        ("scheduler", r"\bcron\b|\bcrontab\b|\bschedule\b|\bapscheduler\b"),
        ("worker", r"\bworker\b|\bconsumer\b|\bcelery\b|\bbullmq\b|\bqueue\.process\b"),
        ("background-task", r"create_task\(|setInterval\(|BackgroundTasks\b"),
    ]
    lowered = text.lower()
    for job_type, pattern in patterns:
        if re.search(pattern, lowered, re.I):
            jobs.append({"job_type": job_type})
    return jobs


def extract_events(text: str, suffix: str) -> list[dict[str, Any]]:
    del suffix
    events: list[dict[str, Any]] = []
    patterns = [
        ("publish", r"\bpublish\(|\bemit\(|producer\.send|kafka\.producer"),
        ("consume", r"\bconsume\(|\bon\(['\"]message|consumer\.run|kafka\.consumer"),
        ("webhook", r"\bwebhook\b"),
    ]
    lowered = text.lower()
    for event_type, pattern in patterns:
        if re.search(pattern, lowered, re.I):
            events.append({"event_type": event_type})
    return events
