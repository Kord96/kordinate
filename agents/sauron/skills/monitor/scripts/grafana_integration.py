"""
Grafana Integration - Reusable validation for Grafana dashboards.

Validates dashboard configuration against application requirements:
- State-timeline panels must have interval <= metrics_interval_seconds

Extracted from nokrashi-tools (Kord96/nokrashi-tools, archived).

Usage:
    grafana = GrafanaIntegration(
        grafana_url="https://grafana.example.com",
        dashboard_uid="my-dashboard",
        metrics_interval_seconds=15,
    )
    grafana.set_api_token("glsa_...")
    result = grafana.validate_panel_intervals()
"""

import json
from dataclasses import dataclass, field
from urllib.error import URLError
from urllib.request import Request, urlopen


@dataclass
class GrafanaIntegration:
    """Configurable Grafana integration checker."""

    # ==========================================================================
    # Required
    # ==========================================================================
    grafana_url: str
    dashboard_uid: str
    metrics_interval_seconds: int

    # ==========================================================================
    # Configuration
    # ==========================================================================
    api_token: str | None = None
    skip_tests: set[str] = field(default_factory=set)

    # Panel types that MUST have interval set (correctness required)
    required_interval_panel_types: set[str] = field(
        default_factory=lambda: {"state-timeline"}
    )

    # Panel types that SHOULD have interval set (recommended)
    optional_interval_panel_types: set[str] = field(
        default_factory=lambda: {"timeseries"}
    )

    # ==========================================================================
    # Methods
    # ==========================================================================

    def set_api_token(self, token: str) -> None:
        """Set the API token for Grafana authentication."""
        self.api_token = token

    def _parse_interval_seconds(self, interval: str) -> float:
        """Parse interval string to seconds."""
        s = interval.strip().lower()
        if s.endswith("ms"):
            return float(s[:-2]) / 1000
        elif s.endswith("s"):
            return float(s[:-1])
        elif s.endswith("m"):
            return float(s[:-1]) * 60
        elif s.endswith("h"):
            return float(s[:-1]) * 3600
        else:
            return float(s)

    def _fetch_dashboard(self, api_token: str | None = None) -> dict | None:
        """Fetch dashboard JSON from Grafana API.

        Args:
            api_token: Optional API token override. Uses self.api_token if not provided.

        Returns:
            Dashboard dict or None if fetch failed.
        """
        token = api_token or self.api_token
        if not token:
            return None

        url = f"{self.grafana_url}/api/dashboards/uid/{self.dashboard_uid}"

        try:
            req = Request(url, method="GET")
            req.add_header("Authorization", f"Bearer {token}")
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return data.get("dashboard", {})
        except (URLError, Exception):
            return None

    def validate_panel_intervals(self, api_token: str | None = None) -> dict:
        """Validate that panel intervals are configured correctly.

        Args:
            api_token: Optional API token override. Uses self.api_token if not provided.

        Returns:
            dict with:
                - valid: bool - True if all panels pass validation
                - violations: list of violation messages
                - warnings: list of warning messages (for optional panels)
                - error: str if fetch failed
        """
        result = {
            "valid": True,
            "violations": [],
            "warnings": [],
            "error": None,
        }

        token = api_token or self.api_token
        if not token:
            result["valid"] = False
            result["error"] = (
                "No API token provided. Pass api_token parameter or call set_api_token()."
            )
            return result

        dashboard = self._fetch_dashboard(token)
        if dashboard is None:
            result["valid"] = False
            result["error"] = (
                f"Failed to fetch dashboard '{self.dashboard_uid}' from {self.grafana_url}"
            )
            return result

        max_interval_seconds = self.metrics_interval_seconds
        max_interval_display = f"{max_interval_seconds}s"

        def check_panels(panels: list) -> None:
            """Recursively check panels for interval violations."""
            for panel in panels:
                # Handle nested panels (rows)
                if "panels" in panel:
                    check_panels(panel["panels"])
                    continue

                panel_type = panel.get("type", "")
                title = panel.get("title", f"Panel {panel.get('id')}")
                targets = panel.get("targets", [])

                is_required = panel_type in self.required_interval_panel_types
                is_optional = panel_type in self.optional_interval_panel_types

                if not is_required and not is_optional:
                    continue

                for i, target in enumerate(targets):
                    interval = target.get("interval")
                    if not interval:
                        msg = f"{title}: target[{i}] missing interval (required <= {max_interval_display})"
                        if is_required:
                            result["violations"].append(msg)
                            result["valid"] = False
                        else:
                            result["warnings"].append(msg)
                    else:
                        interval_seconds = self._parse_interval_seconds(interval)
                        if interval_seconds > max_interval_seconds:
                            msg = f"{title}: target[{i}] interval={interval} > push_interval={max_interval_display}"
                            if is_required:
                                result["violations"].append(msg)
                                result["valid"] = False
                            else:
                                result["warnings"].append(msg)

        check_panels(dashboard.get("panels", []))
        return result

    def create_test_class(self):
        """Create a test class with Grafana integration tests."""
        grafana = self

        class GrafanaIntegrationTests:
            """Reusable Grafana integration tests."""

            def test_state_timeline_panels_have_valid_interval(self):
                """State-timeline panels must have interval <= metrics push interval."""
                if (
                    "test_state_timeline_panels_have_valid_interval"
                    in grafana.skip_tests
                ):
                    return

                result = grafana.validate_panel_intervals()

                if result["error"]:
                    try:
                        import pytest

                        pytest.skip(result["error"])
                    except ImportError:
                        return

                assert result["valid"], (
                    f"Grafana state-timeline panel interval violations:\n"
                    f"  {chr(10).join(result['violations'])}\n\n"
                    f"State-timeline panels must have interval <= {grafana.metrics_interval_seconds}s "
                    f"to show all state transitions."
                )

        return GrafanaIntegrationTests
