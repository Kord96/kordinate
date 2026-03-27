"""
Reference pattern: Grafana dashboard management via API.

Use the grafana MCP for interactive dashboard work. This pattern is for
programmatic dashboard push/pull (e.g., CI/CD, bulk operations).

Usage:
    import json
    from pathlib import Path
    from urllib.request import Request, urlopen
    import base64

    GRAFANA_URL = "http://grafana.monitor.svc:3000"
    GRAFANA_USER = "admin"
    GRAFANA_PASSWORD = "admin"

    def _grafana_request(endpoint, method="GET", data=None):
        url = f"{GRAFANA_URL}/api{endpoint}"
        creds = base64.b64encode(f"{GRAFANA_USER}:{GRAFANA_PASSWORD}".encode()).decode()
        headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}
        body = json.dumps(data).encode() if data else None
        req = Request(url, data=body, headers=headers, method=method)
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def push_dashboard(path, overwrite=True, folder_uid=None):
        dashboard = json.loads(Path(path).read_text())
        payload = {"dashboard": dashboard, "overwrite": overwrite}
        if folder_uid:
            payload["folderUid"] = folder_uid
        return _grafana_request("/dashboards/db", method="POST", data=payload)

    def get_dashboard(uid):
        return _grafana_request(f"/dashboards/uid/{uid}")["dashboard"]
"""
