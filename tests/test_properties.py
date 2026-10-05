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
    """Feature: security-analysis-correctness, Property 1: Idempotency

    run_analysis returns the same result for the same input (idempotent).
    """
    result1 = run_analysis(config)
    result2 = run_analysis(config)
    assert result1 == result2, (
        f"run_analysis is not idempotent\n"
        f"result1={result1}\n"
        f"result2={result2}"
    )


@settings(max_examples=50)
@given(_config_strategy)
def test_property_monotonicity(config):
    """Feature: security-analysis-correctness, Property 2: Monotonicity under weakening."""
    modified = dict(config)
    modified["mfa_enabled"] = False
    modified["storage_encrypted"] = False
    original_count = len(run_analysis(config))
    modified_count = len(run_analysis(modified))
    assert modified_count >= original_count, (
        f"Monotonicity violated:\n"
        f"  original config={config!r}  ->  finding count={original_count}\n"
        f"  mutated config={modified!r}  ->  finding count={modified_count}"
    )


@settings(max_examples=50)
@given(_config_strategy)
def test_property_severity_membership(config):
    """Feature: security-analysis-correctness, Property 3: Severity membership invariant."""
    valid_severities = set(Severity)
    for finding in run_analysis(config):
        assert finding.severity in valid_severities, (
            f"Severity membership violated: control_id={finding.control_id!r}, "
            f"invalid severity={finding.severity!r}"
        )
