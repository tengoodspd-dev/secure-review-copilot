---
inclusion: always
---

# Architecture Steering — SecureReview Copilot

## Module Boundaries

The project is divided into four layers. Each layer may only import from the layer below it; upward imports are forbidden.

```
Layer 4 (UI)        src/app.py
Layer 3 (Services)  src/report.py
Layer 2 (Engine)    src/analyser.py
Layer 1 (Data)      mcp_server/controls.json
```

**Rules:**
- `src/app.py` may import from `src/analyser.py` and `src/report.py`. It must NOT import from `mcp_server/`.
- `src/analyser.py` may import only from the Python standard library and `src/` siblings. It must NOT import Streamlit.
- `src/report.py` may import only from `src/analyser.py` and the standard library.
- `mcp_server/server.py` is a standalone process; it must NOT import from `src/`.

## Data Flow

```
User JSON input
  → src/app.py (validation)
  → src/analyser.py run_analysis() → list[Finding]
  → src/app.py (render dashboard + checklist)
  → src/report.py generate_markdown() → str
  → Streamlit download_button
```

The MCP server runs as a separate subprocess (stdio). Kiro agents call it directly; the Streamlit app does NOT call it at runtime (the analyser contains the same logic inline for the UI path).

## Adding New Controls

1. Add a new entry to `mcp_server/controls.json`.
2. Add a corresponding checker function in `src/analyser.py`.
3. Register the checker in the `CHECKERS` list at the bottom of `analyser.py`.
4. Add a unit test in `tests/test_analyser.py`.
5. Update `design.md` control catalogue table.

## Concurrency

The application is single-user and local. No async code, background threads, or multiprocessing is used unless explicitly required.
