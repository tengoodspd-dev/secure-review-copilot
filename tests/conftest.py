import pytest


@pytest.fixture
def good_config():
    """A fully secure system configuration that should produce zero findings."""
    return {
        "system_name": "test-good",
        "mfa_enabled": True,
        "default_credentials": False,
        "open_ports": [443],
        "public_endpoint": True,
        "tls_enabled": True,
        "tls_version": "1.3",
        "storage_encrypted": True,
        "audit_log_enabled": True,
        "os_version": "Ubuntu 22.04",
    }


@pytest.fixture
def bad_config():
    """A fully misconfigured system that should trigger all 8 controls."""
    return {
        "system_name": "test-bad",
        "mfa_enabled": False,
        "default_credentials": True,
        "open_ports": [23, 3389],
        "public_endpoint": True,
        "tls_enabled": False,
        "tls_version": "1.0",
        "storage_encrypted": False,
        "audit_log_enabled": False,
        "os_version": "Ubuntu 18.04",
    }
