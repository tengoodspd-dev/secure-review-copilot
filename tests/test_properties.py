from hypothesis import given, settings
from hypothesis import strategies as st
from src.analyser import run_analysis, Severity

_config_strategy = st.fixed_dictionaries({
    "mfa_enabled": st.booleans(),
    "default_credentials": st.booleans(),
    "open_ports": st.lists(st.integers(min_value=1, max_value=65535), max_size=10),
    "public_endpoint": st.booleans(),
    "tls_enabled": st.booleans(),
    "tls_version": st.sampled_from(["1.0", "1.1", "1.2", "1.3"]),
    "storage_encrypted": st.booleans(),
    "audit_log_enabled": st.booleans(),
    "os_version": st.sampled_from([
        "Ubuntu 22.04", "Ubuntu 20.04", "Ubuntu 18.04", "CentOS 7", "Windows Server 2022",
    ]),
})


@settings(max_examples=50)
@given(_config_strategy)
def test_property_idempotency(config):
    """Property 1: run_analysis returns the same result for the same input (idempotent)."""
    result1 = run_analysis(config)
    result2 = run_analysis(config)
    assert result1 == result2, "run_analysis is not idempotent"


@settings(max_examples=50)
@given(_config_strategy)
def test_property_monotonicity(config):
    """Property 2: adding known-bad keys never decreases the finding count."""
    modified = dict(config)
    modified["mfa_enabled"] = False
    modified["storage_encrypted"] = False
    original_count = len(run_analysis(config))
    modified_count = len(run_analysis(modified))
    assert modified_count >= original_count, (
        f"Monotonicity violated: original={original_count}, modified={modified_count}\n"
        f"config={config}\nmodified={modified}"
    )


@settings(max_examples=50)
@given(_config_strategy)
def test_property_severity_membership(config):
    """Property 3: all findings have a valid Severity enum value."""
    valid_severities = set(Severity)
    for finding in run_analysis(config):
        assert finding.severity in valid_severities, (
            f"Invalid severity {finding.severity!r} in finding {finding.control_id}"
        )
