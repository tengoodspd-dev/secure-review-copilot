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
  - File: `tests/test_properties.py`
  - Run: `pytest tests/test_properties.py -v`

- [x] **5. Powers**
  - All analysis logic runs locally with no external paid APIs
  - Local MCP server acts as the "power" layer for control cataloguing
  - File: `mcp_server/server.py`

- [x] **6. MCP**
  - Local stdio MCP server with `get_security_controls` and `evaluate_control` tools
  - Files: `mcp_server/server.py`, `mcp_server/controls.json`, `.kiro/settings/mcp.json`
  - Run: `python mcp_server/server.py`

- [x] **7. Custom agents**
  - `security-reviewer` agent with scoped permissions, MCP server access, and file path restrictions
  - File: `.kiro/agents/security-reviewer.md`

---

## Pre-submission verification

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Streamlit app launches: `streamlit run src/app.py`
- [ ] MCP server starts: `python mcp_server/server.py`
- [ ] All 20 project files exist and are non-empty
- [ ] No secrets or credentials in committed files
- [ ] README explains all 7 lessons with file references
