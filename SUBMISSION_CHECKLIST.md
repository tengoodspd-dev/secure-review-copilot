# Kiro University Challenge — Submission Checklist

## SecureReview Copilot

- [x] **1. Spec-driven development**
  - Requirements, design, and tasks authored as Kiro Specs
  - Files: `.kiro/specs/secure-review-copilot/requirements.md`, `design.md`, `tasks.md`

- [x] **2. Steering documents**
  - Architecture, coding conventions, and security policies
  - Files: `.kiro/steering/architecture.md`, `coding.md`, `security.md`

- [x] **3. Hooks**
  - pytest auto-runs on Python file change
  - Files: `.kiro/hooks/` (hook configuration files)

- [x] **4. Property-based testing**
  - 3 Hypothesis properties: idempotency, monotonicity, severity membership
  - Spec Correctness traceability: each property is explicitly linked to REQ-002 in requirements.md
  - File: `tests/test_properties.py`
  - Traceability: `.kiro/specs/secure-review-copilot/requirements.md` → § Spec Correctness
  - Run: `pytest tests/test_properties.py -v`

- [x] **5. Powers**
  - Packaged as Agent Plugins v1.0.0 Power
  - `plugin.json` manifest with name, version, description, keywords
  - `mcp.json` declares the security-controls MCP server
  - `skills/security-review/SKILL.md` provides the skill instructions
  - Files: `power/plugin.json`, `power/mcp.json`, `power/skills/security-review/SKILL.md`
  - Install: Kiro IDE → Powers panel → Install from local path → select `power/`

- [x] **6. MCP**
  - Local stdio MCP server with `get_security_controls` and `evaluate_control` tools
  - Files: `mcp_server/server.py`, `mcp_server/controls.json`, `.kiro/settings/mcp.json`
  - Run: `python mcp_server/server.py`

- [x] **7. Custom agents**
  - `security-reviewer` agent with scoped permissions, MCP server access, and file path restrictions
  - File: `.kiro/agents/security-reviewer.md`

---

## Pre-submission verification

- [x] All tests pass: `pytest tests/ -v` → **29/29 passed** (Python 3.14, pytest 8.3.5, hypothesis 6.131.6)
- [x] Streamlit app imports cleanly (`from src.analyser import run_analysis` OK, `from src.report import generate_markdown` OK)
- [x] MCP server loads: `get_security_controls()` returns 8 controls, `evaluate_control` works correctly
- [x] Hook created: `.kiro/hooks/run-tests-on-save.json` (PostFileSave, matcher `\.py$`)
- [x] All 27 project files exist and are non-empty
- [x] No secrets or credentials in committed files
- [x] README explains all 7 lessons with file references

## Test results (final run)

```
29 passed, 1 warning in 0.30s
  - tests/test_analyser.py       17 tests ✅
  - tests/test_mcp_server.py      9 tests ✅
  - tests/test_properties.py      3 Hypothesis properties ✅
    - test_property_idempotency
    - test_property_monotonicity
    - test_property_severity_membership
```
