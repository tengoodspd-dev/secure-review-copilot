# Design — SecureReview Copilot

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│              Streamlit UI (src/app.py)        │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐ │
│  │ JSON     │  │ Dashboard │  │ Checklist │ │
│  │ Intake   │  │ (charts)  │  │ + Export  │ │
│  └────┬─────┘  └─────┬─────┘  └─────┬─────┘ │
└───────┼──────────────┼──────────────┼────────┘
        │              │              │
        ▼              ▼              ▼
┌───────────────────────────────────────────────┐
│           Analyser Engine (src/analyser.py)    │
│  run_analysis(config: dict) → [Finding]        │
└──────────────────┬────────────────────────────┘
                   │  calls via subprocess / MCP SDK
                   ▼
┌───────────────────────────────────────────────┐
│   Local stdio MCP Server (mcp_server/server.py)│
│   tools: get_security_controls                │
│           evaluate_control                    │
└───────────────────────────────────────────────┘
```

## Module Responsibilities

### `src/analyser.py`
- `Finding` dataclass: `control_id`, `title`, `severity`, `description`, `remediation`
- `Severity` enum: CRITICAL, HIGH, MEDIUM, LOW, INFO
- `run_analysis(config: dict) → list[Finding]`
  - Iterates over registered control checkers
  - Returns deduplicated, sorted list (CRITICAL first)
- Individual checker functions: one per control category (auth, network, encryption, logging, patching)

### `src/report.py`
- `generate_markdown(findings, config_meta) → str`
  - Produces the full Markdown report string
  - Includes scan timestamp, system name, findings table, checklist section

### `src/app.py`
- Streamlit entry point
- Widgets: JSON text area, file uploader, "Analyse" button
- Renders dashboard, checklist (session_state), download button
- Calls `run_analysis` directly (no network hop needed for UI path)

### `mcp_server/server.py`
- FastMCP-based stdio server
- `CONTROLS_DB`: in-memory list of all control definitions loaded from `mcp_server/controls.json`
- `get_security_controls()` → full list
- `evaluate_control(control_id, config_snippet)` → `{control_id, status, evidence}`

### `mcp_server/controls.json`
- Static JSON file: list of control objects
- Schema: `{id, title, category, severity, description, remediation, check_path, check_value}`

### `tests/test_analyser.py`
- Unit tests for each checker function using fixture configs

### `tests/test_properties.py`
- Hypothesis property tests (idempotency, monotonicity, severity membership)

### `tests/test_mcp_server.py`
- Tests that MCP server tools return expected shapes

### `sample_data/`
- `good_config.json` — a well-configured system (zero HIGH/CRITICAL findings)
- `bad_config.json` — a misconfigured system (multiple CRITICAL findings)
- `mixed_config.json` — partial misconfigurations (mix of severities)

## Data Models

```python
from dataclasses import dataclass
from enum import Enum

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MEDIUM   = "MEDIUM"
    LOW      = "LOW"
    INFO     = "INFO"

@dataclass
class Finding:
    control_id:  str
    title:       str
    severity:    Severity
    description: str
    remediation: str
```

## Control Catalogue (mcp_server/controls.json)

| ID      | Category       | Severity | What it checks                                 |
|---------|----------------|----------|------------------------------------------------|
| AUTH-01 | Auth           | CRITICAL | `mfa_enabled` is false or absent               |
| AUTH-02 | Auth           | HIGH     | `default_credentials` is true                  |
| NET-01  | Network        | HIGH     | Any port in `open_ports` is in high-risk list  |
| NET-02  | Network        | MEDIUM   | `public_endpoint` is true without TLS          |
| ENC-01  | Encryption     | CRITICAL | `storage_encrypted` is false or absent         |
| ENC-02  | Encryption     | HIGH     | `tls_version` < "1.2"                          |
| LOG-01  | Logging        | MEDIUM   | `audit_log_enabled` is false or absent         |
| PATCH-01| Patching       | HIGH     | `os_version` in known-EOL list                 |

## Kiro Integration Points

| Lesson | File(s) |
|--------|---------|
| 1 — Spec | `.kiro/specs/secure-review-copilot/` |
| 2 — Steering | `.kiro/steering/architecture.md`, `coding.md`, `security.md` |
| 3 — Hooks | `.kiro/hooks/run-tests-on-save.json` |
| 4 — Property tests | `tests/test_properties.py` |
| 5 — Powers | README.md §Powers (documented usage) |
| 6 — MCP | `mcp_server/server.py`, `.kiro/settings/mcp.json` |
| 7 — Custom agent | `.kiro/agents/security-reviewer.md` |

## Technology Choices

| Concern | Choice | Reason |
|---------|--------|--------|
| UI | Streamlit | Zero-boilerplate, single-file apps; suitable for local tools |
| MCP | `mcp` (Python SDK) | Official SDK; stdio transport requires no network |
| Testing | pytest + Hypothesis | Standard; Hypothesis covers combinatorial corner cases |
| Data | Plain dataclasses | No ORM needed; simple, serialisable, testable |
| Packaging | `requirements.txt` | Minimal friction; no build step required |

## File Tree

```
SecureReview-Copilot/
├── .kiro/
│   ├── agents/
│   │   └── security-reviewer.md
│   ├── hooks/
│   │   └── run-tests-on-save.json
│   ├── settings/
│   │   └── mcp.json
│   ├── specs/
│   │   └── secure-review-copilot/
│   │       ├── requirements.md
│   │       ├── design.md
│   │       └── tasks.md
│   └── steering/
│       ├── architecture.md
│       ├── coding.md
│       └── security.md
├── mcp_server/
│   ├── __init__.py
│   ├── server.py
│   └── controls.json
├── sample_data/
│   ├── good_config.json
│   ├── bad_config.json
│   └── mixed_config.json
├── src/
│   ├── __init__.py
│   ├── analyser.py
│   ├── app.py
│   └── report.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_analyser.py
│   ├── test_mcp_server.py
│   └── test_properties.py
├── README.md
├── requirements.txt
└── SUBMISSION_CHECKLIST.md
```
