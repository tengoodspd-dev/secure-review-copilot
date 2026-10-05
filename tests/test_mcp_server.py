from mcp_server.server import get_security_controls, evaluate_control


def test_get_security_controls_returns_list():
    controls = get_security_controls()
    assert isinstance(controls, list)
    assert len(controls) > 0


def test_get_security_controls_have_id():
    controls = get_security_controls()
    for c in controls:
        assert "id" in c, f"Control missing 'id': {c}"


def test_evaluate_auth01_fail():
    result = evaluate_control("AUTH-01", {"mfa_enabled": False})
    assert result["status"] == "fail"
    assert result["control_id"] == "AUTH-01"


def test_evaluate_auth01_pass():
    result = evaluate_control("AUTH-01", {"mfa_enabled": True})
    assert result["status"] == "pass"


def test_evaluate_net01_fail():
    result = evaluate_control("NET-01", {"open_ports": [3389]})
    assert result["status"] == "fail"


def test_evaluate_net01_pass():
    result = evaluate_control("NET-01", {"open_ports": [443, 80]})
    assert result["status"] == "pass"


def test_evaluate_unknown_control():
    result = evaluate_control("UNKNOWN-99", {})
    assert result["status"] == "error"


def test_evaluate_enc01_fail():
    result = evaluate_control("ENC-01", {"storage_encrypted": False})
    assert result["status"] == "fail"


def test_evaluate_enc01_pass():
    result = evaluate_control("ENC-01", {"storage_encrypted": True})
    assert result["status"] == "pass"
