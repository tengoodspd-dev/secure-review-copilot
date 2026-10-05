from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    """Severity levels for security findings."""

    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MEDIUM   = "MEDIUM"
    LOW      = "LOW"
    INFO     = "INFO"


SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH:     1,
    Severity.MEDIUM:   2,
    Severity.LOW:      3,
    Severity.INFO:     4,
}


@dataclass(frozen=True)
class Finding:
    """A single security finding produced by the analyser."""

    control_id:  str
    title:       str
    severity:    Severity
    description: str
    remediation: str


_RISKY_PORTS = {21, 23, 3389, 5900}
_EOL_OS = {"Ubuntu 18.04", "Ubuntu 16.04", "CentOS 6", "Windows Server 2008"}


def _check_auth(config: dict) -> list[Finding]:
    """Check authentication-related controls."""
    findings = []
    if not config.get("mfa_enabled", False):
        findings.append(Finding(
            control_id="AUTH-01",
            title="MFA Not Enabled",
            severity=Severity.CRITICAL,
            description="Multi-factor authentication is disabled.",
            remediation="Enable MFA for all user accounts and administrative interfaces.",
        ))
    if config.get("default_credentials", False):
        findings.append(Finding(
            control_id="AUTH-02",
            title="Default Credentials In Use",
            severity=Severity.HIGH,
            description="Default credentials are still active on the system.",
            remediation="Change all default passwords immediately and enforce a strong password policy.",
        ))
    return findings


def _check_network(config: dict) -> list[Finding]:
    """Check network exposure controls."""
    findings = []
    open_ports = set(config.get("open_ports", []))
    risky = _RISKY_PORTS & open_ports
    if risky:
        findings.append(Finding(
            control_id="NET-01",
            title="High-Risk Ports Exposed",
            severity=Severity.HIGH,
            description=f"High-risk ports are open: {sorted(risky)}.",
            remediation="Close unnecessary ports. Use VPN or bastion host for administrative access.",
        ))
    if config.get("public_endpoint", False) and not config.get("tls_enabled", True):
        findings.append(Finding(
            control_id="NET-02",
            title="Public Endpoint Without TLS",
            severity=Severity.MEDIUM,
            description="A public-facing endpoint is accessible without TLS encryption.",
            remediation="Enable TLS 1.2+ on all public endpoints.",
        ))
    return findings


def _check_encryption(config: dict) -> list[Finding]:
    """Check encryption-at-rest and in-transit controls."""
    findings = []
    if not config.get("storage_encrypted", False):
        findings.append(Finding(
            control_id="ENC-01",
            title="Storage Not Encrypted",
            severity=Severity.CRITICAL,
            description="Data at rest is not encrypted.",
            remediation="Enable full-disk or volume-level encryption.",
        ))
    tls_ver = config.get("tls_version", "")
    if tls_ver in ("1.0", "1.1"):
        findings.append(Finding(
            control_id="ENC-02",
            title="Weak TLS Version",
            severity=Severity.HIGH,
            description=f"TLS {tls_ver} is in use, which has known vulnerabilities.",
            remediation="Upgrade to TLS 1.2 or 1.3 and disable older versions.",
        ))
    return findings


def _check_logging(config: dict) -> list[Finding]:
    """Check logging and monitoring controls."""
    if not config.get("audit_log_enabled", False):
        return [Finding(
            control_id="LOG-01",
            title="Audit Logging Disabled",
            severity=Severity.MEDIUM,
            description="Audit logging is not enabled; security events cannot be traced.",
            remediation="Enable audit logging and forward logs to a centralised SIEM.",
        )]
    return []


def _check_patching(config: dict) -> list[Finding]:
    """Check OS/software patching controls."""
    os_ver = config.get("os_version", "")
    if os_ver in _EOL_OS:
        return [Finding(
            control_id="PATCH-01",
            title="End-of-Life OS Version",
            severity=Severity.HIGH,
            description=f"Operating system '{os_ver}' is end-of-life and no longer receives security patches.",
            remediation="Upgrade to a supported OS version.",
        )]
    return []


CHECKERS = [_check_auth, _check_network, _check_encryption, _check_logging, _check_patching]


def run_analysis(config: dict[str, object]) -> list[Finding]:
    """Analyse a system configuration dict and return deduplicated, severity-sorted findings.

    Args:
        config: A dictionary representing the system configuration.

    Returns:
        A list of Finding objects sorted by severity (CRITICAL first).
    """
    seen: set[str] = set()
    findings: list[Finding] = []
    for checker in CHECKERS:
        for finding in checker(config):
            if finding.control_id not in seen:
                seen.add(finding.control_id)
                findings.append(finding)
    findings.sort(key=lambda f: SEVERITY_ORDER[f.severity])
    return findings
