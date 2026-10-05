from src.analyser import run_analysis, Finding, Severity
from src.report import generate_markdown


def test_good_config_no_findings(good_config):
    """Good config should produce zero findings."""
    findings = run_analysis(good_config)
    assert findings == [], f"Expected no findings, got: {findings}"


def test_bad_config_all_findings(bad_config):
    """Bad config should trigger all 8 control IDs."""
    findings = run_analysis(bad_config)
    ids = {f.control_id for f in findings}
    expected = {"AUTH-01", "AUTH-02", "NET-01", "NET-02", "ENC-01", "ENC-02", "LOG-01", "PATCH-01"}
    assert ids == expected, f"Expected {expected}, got {ids}"


def test_auth01_fires_when_mfa_disabled():
    config = {"mfa_enabled": False}
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "AUTH-01" in ids


def test_auth01_does_not_fire_when_mfa_enabled():
    config = {"mfa_enabled": True, "storage_encrypted": True, "audit_log_enabled": True}
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "AUTH-01" not in ids


def test_auth02_fires_when_default_credentials():
    config = {
        "default_credentials": True,
        "mfa_enabled": True,
        "storage_encrypted": True,
        "audit_log_enabled": True,
    }
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "AUTH-02" in ids


def test_net01_fires_for_risky_ports():
    config = {
        "mfa_enabled": True,
        "storage_encrypted": True,
        "audit_log_enabled": True,
        "open_ports": [23, 3389],
    }
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "NET-01" in ids


def test_net01_does_not_fire_for_safe_ports():
    config = {
        "mfa_enabled": True,
        "storage_encrypted": True,
        "audit_log_enabled": True,
        "open_ports": [443, 8080],
    }
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "NET-01" not in ids


def test_net02_fires_for_public_endpoint_without_tls():
    config = {
        "mfa_enabled": True,
        "storage_encrypted": True,
        "audit_log_enabled": True,
        "public_endpoint": True,
        "tls_enabled": False,
    }
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "NET-02" in ids


def test_enc01_fires_when_storage_not_encrypted():
    config = {"mfa_enabled": True, "storage_encrypted": False, "audit_log_enabled": True}
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "ENC-01" in ids


def test_enc02_fires_for_weak_tls():
    config = {
        "mfa_enabled": True,
        "storage_encrypted": True,
        "audit_log_enabled": True,
        "tls_version": "1.0",
    }
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "ENC-02" in ids


def test_log01_fires_when_audit_disabled():
    config = {"mfa_enabled": True, "storage_encrypted": True, "audit_log_enabled": False}
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "LOG-01" in ids


def test_patch01_fires_for_eol_os():
    config = {
        "mfa_enabled": True,
        "storage_encrypted": True,
        "audit_log_enabled": True,
        "os_version": "Ubuntu 18.04",
    }
    findings = run_analysis(config)
    ids = {f.control_id for f in findings}
    assert "PATCH-01" in ids


def test_run_analysis_deduplicates():
    """Running analysis twice on the same config returns the same result."""
    config = {"mfa_enabled": False, "storage_encrypted": False}
    r1 = run_analysis(config)
    r2 = run_analysis(config)
    assert len(r1) == len(r2)
    assert {f.control_id for f in r1} == {f.control_id for f in r2}


def test_findings_sorted_by_severity():
    config = {
        "mfa_enabled": False,
        "storage_encrypted": False,
        "audit_log_enabled": False,
        "open_ports": [3389],
    }
    findings = run_analysis(config)
    severities = [f.severity for f in findings]
    severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    indices = [severity_order.index(s.value) for s in severities]
    assert indices == sorted(indices), "Findings are not sorted by severity"


def test_generate_markdown_includes_system_name():
    findings = run_analysis({"mfa_enabled": False})
    md = generate_markdown(findings, {"system_name": "my-system"})
    assert "my-system" in md


def test_generate_markdown_includes_finding_title():
    findings = run_analysis({"mfa_enabled": False})
    assert len(findings) > 0
    md = generate_markdown(findings, {"system_name": "test"})
    assert findings[0].title in md


def test_generate_markdown_no_findings():
    md = generate_markdown([], {"system_name": "clean"})
    assert "No security issues" in md
