---
inclusion: always
---

# Security Standards — SecureReview Copilot

## No Secrets in Code or Config

- **Never** hard-code credentials, tokens, API keys, or passwords anywhere in the repository.
- `.kiro/settings/mcp.json` must not contain secret values — use placeholder strings like `"<YOUR_TOKEN>"` if an example is needed, and document what to replace.
- The `.gitignore` must exclude `.env`, `*.key`, `*.pem`, and `secrets/`.

## Input Validation

All external input must be validated before use:

1. **JSON intake (app.py):** Parse with `json.loads()` inside a `try/except json.JSONDecodeError` block. Reject non-dict top-level values.
2. **MCP tool inputs (server.py):** Validate `control_id` exists in `CONTROLS_DB` before processing. Return a structured error dict rather than raising an unhandled exception.
3. **File upload (app.py):** Limit accepted MIME types to `application/json` and `text/plain`. Do not execute or `eval()` uploaded content.

## Dependency Security

- Pin all dependencies in `requirements.txt` to exact versions (e.g. `streamlit==1.40.0`).
- Do not add dependencies that are not actively maintained or that have known CVEs.
- When adding a new package, verify the package name carefully (typosquatting risk).

## Output Safety

- The generated Markdown report must not include raw user-supplied strings interpolated without escaping in contexts where injection is possible.
- Do NOT use `st.markdown(..., unsafe_allow_html=True)` unless the content is fully controlled by the application (not by user input).

## Principle of Least Privilege

- The MCP server process reads only `mcp_server/controls.json`. It must not read, write, or execute any other files.
- The Streamlit app must not spawn subprocesses or access the filesystem outside the project directory.

## Test Data

- Sample configs in `sample_data/` are fictional systems. They must not contain real IP addresses, domain names, usernames, or credentials.
- Replace any real-looking values (e.g. `192.168.1.1`) with clearly fictional ones (e.g. `10.0.example.1` or `<redacted>`).

## Reporting Bias

- The analyser must not suppress or downgrade findings based on the system name or operator identity.
- Finding severities must be determined solely by the control definition in `controls.json`.
