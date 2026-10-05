# Requirements — SecureReview Copilot

## Introduction

SecureReview Copilot is a local security analysis tool that accepts a system configuration (JSON) and produces a structured security risk report with severity-ranked findings, a checklist, and a Markdown export. It is designed for the Kiro University Challenge and demonstrates all seven challenge lessons in a single, runnable application.

No external paid APIs are required. All analysis logic runs locally.

---

## Requirements

### REQ-001 — JSON Configuration Intake
**User story:** As a security reviewer, I want to paste or upload a JSON system configuration so that the tool can analyse it without manual annotation.

**Acceptance criteria:**
- The UI provides a text area and a file-upload widget that accept JSON input.
- Malformed JSON is rejected with a clear error message before analysis begins.
- A valid JSON object of any depth is accepted.
- At least three sample configuration files are bundled with the project.

---

### REQ-002 — Security Risk Analysis
**User story:** As a security reviewer, I want the tool to detect common security misconfigurations automatically so that I do not have to inspect raw JSON manually.

**Acceptance criteria:**
- The analyser checks for at least the following control categories:
  - Authentication & access control (e.g., MFA disabled, default credentials)
  - Network exposure (e.g., open ports, public endpoints)
  - Encryption at rest and in transit (e.g., TLS version, storage encryption flag)
  - Logging & monitoring (e.g., audit log disabled)
  - Patch / version hygiene (e.g., EOL software versions)
- Each finding includes: control ID, title, severity (CRITICAL / HIGH / MEDIUM / LOW / INFO), description, and remediation hint.
- Findings are deduplicated; the same control fires at most once per analysis run.

---

### REQ-003 — MCP Security Controls Server
**User story:** As a developer, I want a local MCP server that exposes security control definitions so that the analyser and the custom agent can query controls programmatically.

**Acceptance criteria:**
- The server is implemented as a local stdio MCP server (`mcp_server/server.py`).
- It exposes at minimum two tools:
  - `get_security_controls` — returns the full list of controls with metadata.
  - `evaluate_control` — accepts a control ID and a configuration snippet; returns a pass/fail result with evidence.
- The server is registered in `.kiro/settings/mcp.json`.
- No secrets or credentials appear in the committed config.

---

### REQ-004 — Risk Dashboard UI
**User story:** As a security reviewer, I want a Streamlit dashboard so that I can view findings grouped by severity with colour coding.

**Acceptance criteria:**
- Findings are grouped into CRITICAL, HIGH, MEDIUM, LOW, INFO sections.
- Each section displays a count badge and an expandable list of findings.
- A summary pie chart shows the distribution of severities.
- The UI renders correctly when zero findings are returned.

---

### REQ-005 — Security Checklist
**User story:** As a security reviewer, I want an interactive checklist so that I can track which remediation actions I have completed.

**Acceptance criteria:**
- A checklist item is generated for every finding with severity CRITICAL or HIGH.
- Each item shows control ID, title, severity badge, and a checkbox.
- Checking an item persists within the current session (Streamlit session state).
- A progress bar shows percentage of items checked.

---

### REQ-006 — Markdown Report Export
**User story:** As a security reviewer, I want to download a Markdown report so that I can share findings with my team.

**Acceptance criteria:**
- A "Download Report" button generates a `.md` file.
- The report includes: title, scan date/time, system name (from JSON), executive summary, full findings table, and the checklist.
- The file is downloadable directly from the Streamlit UI without any server-side storage.

---

### REQ-007 — Property-Based Tests
**User story:** As a developer, I want property-based tests so that the analyser behaves correctly across a wide range of inputs.

**Acceptance criteria:**
- At least three Hypothesis-based properties are implemented in `tests/test_properties.py`:
  1. **Idempotency** — analysing the same config twice returns identical findings.
  2. **Monotonicity** — adding a known-bad key to a config never decreases the finding count.
  3. **Severity ordering** — the returned severity values are always members of the defined enum set.
- All three properties pass with `pytest` + `hypothesis`.

---

### REQ-008 — Kiro Hook Automation
**User story:** As a developer, I want pytest to run automatically when I save a Python file so that regressions are caught immediately.

**Acceptance criteria:**
- A hook defined in `.kiro/hooks/run-tests-on-save.json` triggers on `PostFileSave` for `*.py` files.
- The hook command runs `pytest tests/ -q --tb=short`.
- The hook file is committed to the repository.

---

### REQ-009 — Custom Security Reviewer Agent
**User story:** As a developer, I want a custom Kiro agent scoped to security review so that I can ask targeted questions without leaking broader context.

**Acceptance criteria:**
- Agent defined at `.kiro/agents/security-reviewer.md`.
- The agent's role is restricted to security review tasks.
- The agent references the MCP server tools (`get_security_controls`, `evaluate_control`).
- The agent definition is committed to the repository.

---

### Non-functional requirements
- **NF-001 Offline:** The application must run without internet access after initial `pip install`.
- **NF-002 Python version:** Compatible with Python 3.11+.
- **NF-003 No paid APIs:** No calls to OpenAI, Anthropic, or any paid service at runtime.
- **NF-004 Single command launch:** `streamlit run src/app.py` starts the full application.
- **NF-005 Test coverage:** `pytest tests/` must exit 0 with all tests passing.

---

## Spec Correctness — Property-Based Test Traceability

This section maps each requirement to the property-based test that validates it, fulfilling the Kiro Spec Correctness / Property-Based Testing lesson.

Kiro's Spec Correctness feature translates requirements into executable specifications: each acceptance criterion that expresses a universal rule ("for any input X, property Y holds") is directly linked to a Hypothesis property test in `tests/test_properties.py`.

| Requirement | Acceptance Criterion (property) | Property Test | Test Description |
|-------------|----------------------------------|---------------|------------------|
| REQ-002 — Security Risk Analysis | Analysing the same config twice returns identical findings | `test_property_idempotency` | For any config dict, `run_analysis(c) == run_analysis(c)` |
| REQ-002 — Security Risk Analysis | Adding a known-bad key never decreases the finding count | `test_property_monotonicity` | For any config, adding `mfa_enabled=False` + `storage_encrypted=False` never reduces findings |
| REQ-002 — Security Risk Analysis | Returned severity values are always members of the defined enum | `test_property_severity_membership` | For any config, every `finding.severity in set(Severity)` |

### How to verify

Run the property tests to confirm each requirement property holds across 50 randomised inputs:

```bash
pytest tests/test_properties.py -v
```

Expected output:
```
tests/test_properties.py::test_property_idempotency          PASSED  ← REQ-002 (idempotency)
tests/test_properties.py::test_property_monotonicity         PASSED  ← REQ-002 (monotonicity)
tests/test_properties.py::test_property_severity_membership  PASSED  ← REQ-002 (severity enum)
```

All three properties passed with `hypothesis==6.131.6` and `pytest==8.3.5` on Python 3.14.
No new tests were added — the existing tests in `tests/test_properties.py` are the executable specification.
