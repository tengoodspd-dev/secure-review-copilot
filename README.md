# SecureReview Copilot

> A local security analysis tool that accepts a system configuration (JSON) and produces a structured risk report with severity-ranked findings, an interactive checklist, and a Markdown export — built for the Kiro University Challenge.

---

## Prerequisites

- Python 3.11+
- pip

---

## Installation & Running

```bash
git clone <repo-url>
cd Krio-Project
pip install -r requirements.txt
streamlit run src/app.py
```

---

## Architecture

```
User
  │
  ▼
Streamlit UI  (src/app.py)
  │                │
  ▼                ▼
Analyser     Report Generator
(src/analyser.py)  (src/report.py)
  │
  │  (same logic, separate process for agent use)
  ▼
MCP Server  (mcp_server/server.py)
  │
  ▼
Security Controls DB  (mcp_server/controls.json)
  ▲
  │
Custom Agent  (.kiro/agents/security-reviewer.md)
```

**Data flow:**

1. User pastes or uploads a JSON config in the Streamlit UI.
2. `src/app.py` validates the JSON and calls `run_analysis()` in `src/analyser.py`.
3. The analyser runs 5 category checkers and returns a sorted list of `Finding` objects.
4. The UI renders the dashboard (severity counts, pie chart, expandable findings, checklist).
5. On download, `src/report.py` generates a Markdown report string delivered via `st.download_button`.
6. The MCP server runs as a **separate stdio process** — it exposes the same control catalogue to Kiro agents via `get_security_controls` and `evaluate_control` tools.

---

## Kiro University Challenge — 7 Lessons

| Lesson | Description | File(s) |
|--------|-------------|---------|
| 1. Spec-driven development | Requirements, design, and tasks authored as Kiro Specs | `.kiro/specs/secure-review-copilot/requirements.md`, `design.md`, `tasks.md` |
| 2. Steering documents | Architecture, coding conventions, and security policies | `.kiro/steering/architecture.md`, `.kiro/steering/coding.md`, `.kiro/steering/security.md` |
| 3. Hooks | Auto-run pytest on Python file save | `.kiro/hooks/run-tests-on-save.json` |
| 4. Property-based testing | 3 Hypothesis properties linked to REQ-002 via Spec Correctness traceability table | `tests/test_properties.py`, `.kiro/specs/secure-review-copilot/requirements.md` (§ Spec Correctness) |
| 5. Powers | Packaged as Agent Plugins v1.0.0 Power with `plugin.json`, `mcp.json`, and `skills/security-review/SKILL.md` | `power/plugin.json`, `power/mcp.json`, `power/skills/security-review/SKILL.md` |
| 6. MCP | Local stdio MCP server with `get_security_controls` and `evaluate_control` tools | `mcp_server/server.py`, `mcp_server/controls.json`, `.kiro/settings/mcp.json` |
| 7. Custom agents | `security-reviewer` agent with scoped tools, MCP access, and file path restrictions | `.kiro/agents/security-reviewer.md` |

---

## Powers

SecureReview Copilot ships as a **Kiro Power** packaged to the [Agent Plugins v1.0.0](https://agent-plugins.org) specification.

### Power location

```
power/
├── plugin.json                          ← Agent Plugins v1.0.0 manifest
├── mcp.json                             ← MCP server declaration (security-controls)
└── skills/
    └── security-review/
        └── SKILL.md                     ← Security review skill instructions
```

### Install the Power in Kiro IDE

1. Open Kiro IDE.
2. Go to **Powers** panel → **Install from local path**.
3. Select the `power/` directory in this repository.
4. Kiro loads the `security-controls` MCP server automatically and activates the `security-review` skill on demand.

Alternatively, copy the `power/` directory to `~/.kiro/powers/secure-review-copilot/` for user-level installation.

### How the Power was used

With the Power installed, the Security Reviewer agent can call MCP tools directly from chat:

```
# Example: ask the security-reviewer agent to evaluate a config snippet
"Evaluate this config against all controls:
 {\"mfa_enabled\": false, \"storage_encrypted\": true, \"open_ports\": [3389]}"
```

The agent calls `get_security_controls()` to fetch the catalogue, then `evaluate_control()` for each relevant control, and returns a severity-ranked finding list — all without leaving the IDE and without any network calls.

### Note on Lesson 6 (MCP)

The MCP server (`mcp_server/server.py`) and its Kiro-level registration (`.kiro/settings/mcp.json`) are preserved unchanged as the evidence for **Lesson 6**. The Power's `mcp.json` is an additional packaging layer on top of the same server.

---

## Running Tests

```bash
pytest tests/ -v
```

Property-based tests only:

```bash
pytest tests/test_properties.py -v
```

---

## Running the MCP Server Standalone

```bash
python mcp_server/server.py
```

The server speaks the MCP stdio protocol. In normal use, Kiro launches it automatically via the configuration in `.kiro/settings/mcp.json`.

---

## Project Structure

```
.
├── .kiro/
│   ├── agents/security-reviewer.md      # Custom agent (Lesson 7)
│   ├── hooks/run-tests-on-save.json     # Auto-test hook (Lesson 3)
│   ├── settings/mcp.json                # MCP server registration (Lesson 6)
│   ├── specs/secure-review-copilot/     # Kiro Specs (Lesson 1)
│   └── steering/                        # Steering documents (Lesson 2)
├── mcp_server/
│   ├── controls.json                    # Control catalogue
│   └── server.py                        # MCP server (Lesson 6)
├── power/                               # Kiro Power — Agent Plugins v1.0.0 (Lesson 5)
│   ├── plugin.json                      # Power manifest
│   ├── mcp.json                         # MCP server declaration
│   └── skills/security-review/
│       └── SKILL.md                     # Security review skill
├── sample_data/                         # Sample configs for demo
├── src/
│   ├── analyser.py                      # Core analysis engine
│   ├── app.py                           # Streamlit UI
│   └── report.py                        # Markdown report generator
├── tests/
│   ├── conftest.py
│   ├── test_analyser.py
│   ├── test_mcp_server.py
│   └── test_properties.py               # Property-based tests (Lesson 4)
├── README.md
├── requirements.txt
└── SUBMISSION_CHECKLIST.md
```
