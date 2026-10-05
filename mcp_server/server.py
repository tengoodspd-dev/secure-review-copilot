import json
from pathlib import Path
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("security-controls")
CONTROLS_DB: list[dict] = json.loads((Path(__file__).parent / "controls.json").read_text())


@mcp.tool()
def get_security_controls() -> list:
    """Return the full catalogue of security controls."""
    return CONTROLS_DB


@mcp.tool()
def evaluate_control(control_id: str, config_snippet: dict) -> dict:
    """Evaluate a single control against a config snippet.

    Args:
        control_id: The ID of the control to evaluate (e.g. "AUTH-01").
        config_snippet: The portion of the system config relevant to this control.

    Returns:
        A dict with keys: control_id, status ("pass" | "fail" | "error"), evidence (str).
    """
    control = next((c for c in CONTROLS_DB if c["id"] == control_id), None)
    if control is None:
        return {"control_id": control_id, "status": "error", "evidence": f"Unknown control: {control_id}"}

    check_path = control["check_path"]
    value: Any = config_snippet
    for key in check_path.split("."):
        if not isinstance(value, dict):
            value = None
            break
        value = value.get(key)

    if control_id == "NET-01":
        risky_ports = {21, 23, 3389, 5900}
        open_ports = config_snippet.get("open_ports", [])
        found = risky_ports.intersection(set(open_ports))
        if found:
            return {"control_id": control_id, "status": "fail", "evidence": f"High-risk ports open: {sorted(found)}"}
        return {"control_id": control_id, "status": "pass", "evidence": "No high-risk ports found"}

    elif control_id == "NET-02":
        public = config_snippet.get("public_endpoint", False)
        tls = config_snippet.get("tls_enabled", True)
        if public and not tls:
            return {"control_id": control_id, "status": "fail", "evidence": "Public endpoint exposed without TLS"}
        return {"control_id": control_id, "status": "pass", "evidence": "Public endpoint has TLS or is not public"}

    elif control_id == "ENC-02":
        tls_ver = config_snippet.get("tls_version", "1.3")
        if tls_ver in ["1.0", "1.1"]:
            return {"control_id": control_id, "status": "fail", "evidence": f"Weak TLS version: {tls_ver}"}
        return {"control_id": control_id, "status": "pass", "evidence": f"TLS version {tls_ver} is acceptable"}

    elif control_id == "PATCH-01":
        eol_versions = ["Ubuntu 18.04", "Ubuntu 16.04", "CentOS 6", "Windows Server 2008"]
        os_ver = config_snippet.get("os_version", "")
        if os_ver in eol_versions:
            return {"control_id": control_id, "status": "fail", "evidence": f"EOL OS version: {os_ver}"}
        return {"control_id": control_id, "status": "pass", "evidence": f"OS version {os_ver!r} is not EOL"}

    else:
        check_value = control.get("check_value")
        if value == check_value:
            return {
                "control_id": control_id,
                "status": "fail",
                "evidence": f"{check_path} = {value!r} (expected NOT {check_value!r})",
            }
        if value is None:
            if check_value is False:
                return {
                    "control_id": control_id,
                    "status": "fail",
                    "evidence": f"{check_path} is absent (defaults to false)",
                }
        return {"control_id": control_id, "status": "pass", "evidence": f"{check_path} = {value!r}"}


if __name__ == "__main__":
    mcp.run()
