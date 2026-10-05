---
inclusion: always
---

# Coding Standards — SecureReview Copilot

## Python Version

Target **Python 3.11+**. Use built-in `tomllib`, `dataclasses`, and `enum` — do not add third-party replacements for standard-library features.

## Type Hints

- All public functions must have complete type annotations (parameters + return type).
- Use `from __future__ import annotations` at the top of every module.
- Prefer `list[T]` / `dict[K, V]` over `List[T]` / `Dict[K, V]` (PEP 585).

```python
# Good
def run_analysis(config: dict[str, object]) -> list[Finding]:
    ...

# Bad
def run_analysis(config):
    ...
```

## Docstrings

- Every public function, class, and module must have a one-line summary docstring.
- Use Google-style docstrings for functions with non-trivial arguments.

```python
def evaluate_control(control_id: str, config_snippet: dict) -> dict:
    """Evaluate a single security control against a config snippet.

    Args:
        control_id: The ID of the control to evaluate (e.g. "AUTH-01").
        config_snippet: The portion of the system config relevant to this control.

    Returns:
        A dict with keys: control_id, status ("pass" | "warn" | "fail"), evidence (str).
    """
```

## Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Modules | `snake_case` | `analyser.py` |
| Classes | `PascalCase` | `Finding` |
| Functions | `snake_case` | `run_analysis` |
| Constants | `UPPER_SNAKE` | `SEVERITY_ORDER` |
| Private helpers | `_leading_underscore` | `_check_auth` |

## Error Handling

- Raise `ValueError` with a descriptive message for invalid input (e.g. malformed JSON, unknown control ID).
- Do NOT use bare `except:` — always name the exception type.
- Streamlit `app.py` must catch and display errors with `st.error()` rather than letting them propagate to an unhandled traceback.

## Imports

- Standard library first, then third-party, then local — separated by blank lines.
- No wildcard imports (`from module import *`).

## Line Length

Maximum 100 characters. Use parentheses for line continuation, not backslashes.

## Testing

- Test file names: `test_<module_name>.py`.
- Test function names: `test_<what>_<condition>`.
- Every new checker function must have at least one passing and one failing fixture test.
- Property tests go exclusively in `tests/test_properties.py`.
