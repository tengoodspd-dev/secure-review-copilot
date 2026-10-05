# Tasks — SecureReview Copilot

## Implementation Plan

Tasks are ordered by dependency. Each task references the requirement(s) it satisfies.

---

### TASK-01 — Project scaffold & dependencies
**Refs:** NF-001, NF-002, NF-004
- [ ] Create `requirements.txt` with pinned versions: streamlit, mcp, pytest, hypothesis
- [ ] Create `src/__init__.py`, `tests/__init__.py`, `mcp_server/__init__.py`
- [ ] Verify `python -m pytest tests/` exits 0 on empty test suite

---

### TASK-02 — Data models (`src/analyser.py` — models only)
**Refs:** REQ-002
- [ ] Define `Severity` enum (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- [ ] Define `Finding` dataclass with all required fields
- [ ] Define `SEVERITY_ORDER` for sorting

---

### TASK-03 — Control catalogue (`mcp_server/controls.json`)
**Refs:** REQ-003
- [ ] Write all 8 control definitions (AUTH-01/02, NET-01/02, ENC-01/02, LOG-01, PATCH-01)
- [ ] Each entry: id, title, category, severity, description, remediation, check_path, check_value

---

### TASK-04 — Analyser engine (`src/analyser.py` — logic)
**Refs:** REQ-002
- [ ] Implement checker for AUTH controls
- [ ] Implement checker for NET controls
- [ ] Implement checker for ENC controls
- [ ] Implement checker for LOG controls
- [ ] Implement checker for PATCH controls
- [ ] Implement `run_analysis(config) → list[Finding]` with deduplication and severity sort

---

### TASK-05 — MCP server (`mcp_server/server.py`)
**Refs:** REQ-003
- [ ] Implement `get_security_controls()` tool — returns controls list from controls.json
- [ ] Implement `evaluate_control(control_id, config_snippet)` tool — returns pass/warn/fail + evidence
- [ ] Register server as stdio MCP server
- [ ] Create `.kiro/settings/mcp.json` with server entry (no secrets)

---

### TASK-06 — Report generator (`src/report.py`)
**Refs:** REQ-006
- [ ] Implement `generate_markdown(findings, meta) → str`
- [ ] Include: title, timestamp, system_name, executive summary, findings table, checklist section

---

### TASK-07 — Streamlit app (`src/app.py`)
**Refs:** REQ-001, REQ-004, REQ-005, REQ-006
- [ ] JSON intake widget (text area + file uploader) with validation
- [ ] "Analyse" button triggers `run_analysis`
- [ ] Dashboard: severity-grouped findings with counts, pie chart
- [ ] Checklist: CRITICAL/HIGH items with checkboxes and progress bar (session_state)
- [ ] "Download Report" button using `generate_markdown`

---

### TASK-08 — Sample data (`sample_data/`)
**Refs:** REQ-001
- [ ] `good_config.json` — passes all controls
- [ ] `bad_config.json` — triggers all 8 controls
- [ ] `mixed_config.json` — triggers 3–4 controls across severity levels

---

### TASK-09 — Unit tests (`tests/test_analyser.py`, `tests/test_mcp_server.py`)
**Refs:** REQ-002, REQ-003, NF-005
- [ ] Test each checker function with fixture configs
- [ ] Test `run_analysis` deduplication
- [ ] Test `generate_markdown` output structure
- [ ] Test MCP server `get_security_controls` returns list
- [ ] Test MCP server `evaluate_control` returns correct status

---

### TASK-10 — Property-based tests (`tests/test_properties.py`)
**Refs:** REQ-007
- [ ] Property 1: Idempotency — `run_analysis(c) == run_analysis(c)`
- [ ] Property 2: Monotonicity — adding bad keys to config never decreases finding count
- [ ] Property 3: Severity membership — all returned severities are in `Severity` enum
- [ ] All three pass with `pytest --hypothesis-seed=0`

---

### TASK-11 — Kiro Hook (`tests/test_properties.py`)
**Refs:** REQ-008
- [ ] Create `.kiro/hooks/run-tests-on-save.json` using `createHook` tool
- [ ] Trigger: `PostFileSave`, matcher: `\.py$`
- [ ] Command: `cd /Users/kyb/Documents/Krio-Project && python -m pytest tests/ -q --tb=short`

---

### TASK-12 — Steering documents
**Refs:** Lesson 2
- [ ] `.kiro/steering/architecture.md` — module boundaries, data flow rules
- [ ] `.kiro/steering/coding.md` — Python style, type hints, docstring standards
- [ ] `.kiro/steering/security.md` — no secrets in code, input validation rules

---

### TASK-13 — Custom agent
**Refs:** Lesson 7
- [ ] `.kiro/agents/security-reviewer.md` — role, tools, resources, restricted permissions

---

### TASK-14 — README & submission checklist
**Refs:** All
- [ ] Installation & run instructions
- [ ] Architecture diagram (text)
- [ ] Lessons implementation table with file locations
- [ ] Powers usage section
- [ ] `SUBMISSION_CHECKLIST.md` — verify each of the 7 challenge items

---

### TASK-15 — Final verification
**Refs:** NF-005
- [ ] `python -m pytest tests/ -v` exits 0
- [ ] `streamlit run src/app.py` launches without import errors
- [ ] MCP server starts: `python mcp_server/server.py`
- [ ] All 7 challenge items have at least one committed file as evidence
