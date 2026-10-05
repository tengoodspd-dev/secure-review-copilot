# Requirements Document

## Introduction

This spec defines correctness properties for the existing SecureReview Copilot analysis engine (`src/analyser.py`). It does not add new product features — it verifies that `run_analysis` already behaves correctly under three universal properties. All properties are enforced via Hypothesis property-based tests in `tests/test_properties.py`.

## Glossary

- **Analyser**: The `run_analysis` function in `src/analyser.py` that converts a configuration dict into a sorted, deduplicated list of `Finding` objects.
- **Finding**: A frozen dataclass with fields `control_id`, `title`, `severity`, `description`, and `remediation`.
- **Severity**: The `Severity` enum in `src/analyser.py` with values `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`.
- **Configuration**: A Python `dict` of security-relevant settings (boolean flags, port lists, version strings) matching the schema used in `tests/test_properties.py`.
- **Property_Test**: A Hypothesis-based test in `tests/test_properties.py` that asserts a universal property holds across many generated inputs.

---

## Requirements

### Requirement 1: Idempotency of Analysis

**User Story:** As a security reviewer, I want `run_analysis` to produce identical results on repeated calls with the same input, so that I can trust the output is deterministic and free of side effects.

#### Acceptance Criteria

1. FOR ANY valid Configuration, WHEN `run_analysis` is called twice with the same Configuration, THE Analyser SHALL return Finding lists with identical length, identical `control_id` values, identical `severity` values, and identical order.
2. THE Property_Test SHALL verify idempotency across at least 50 generated Configuration inputs using Hypothesis.
3. IF the two results differ, THEN THE Property_Test SHALL fail and report both Finding lists so the exact discrepancy is visible.

---

### Requirement 2: Monotonicity of Findings

**User Story:** As a security reviewer, I want weakening a configuration to never reduce the finding count, so that security regressions are never silently hidden in the report.

#### Acceptance Criteria

1. FOR ANY Configuration where `mfa_enabled` is `True`, WHEN `mfa_enabled` is set to `False` (all other keys unchanged), THE Analyser SHALL return a Finding count greater than or equal to the original count.
2. FOR ANY Configuration where `storage_encrypted` is `True`, WHEN `storage_encrypted` is set to `False` (all other keys unchanged), THE Analyser SHALL return a Finding count greater than or equal to the original count.
3. THE Property_Test SHALL verify both monotonicity mutations across at least 50 generated Configuration inputs using Hypothesis.
4. IF the Finding count decreases after a known-bad mutation, THEN THE Property_Test SHALL fail and report the original and mutated Configuration alongside their respective Finding counts.

---

### Requirement 3: Severity Membership Invariant

**User Story:** As a developer, I want every Finding returned by `run_analysis` to carry a valid Severity value, so that downstream consumers never encounter unexpected severity strings.

#### Acceptance Criteria

1. FOR ANY valid Configuration, THE Analyser SHALL produce only Finding objects whose `severity` field is a member of the `Severity` enum (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`).
2. THE Property_Test SHALL verify the severity membership invariant across at least 50 generated Configuration inputs using Hypothesis.
3. IF a Finding is returned with a `severity` value not in the `Severity` enum, THEN THE Property_Test SHALL fail and report the offending `control_id` and the invalid `severity` value.

---

## Non-Functional Requirements

- **NF-1 No new runtime dependencies:** Property tests SHALL use only `hypothesis` already listed in `requirements.txt`.
- **NF-2 No interface changes:** This spec SHALL NOT modify the public interface of `run_analysis`, `Finding`, or `Severity` in `src/analyser.py` unless a property test proves a change is necessary.
- **NF-3 Offline execution:** All Property_Tests SHALL run without network access.

---

## Spec Correctness — Property-Based Test Traceability

| Requirement | Property | Test Location | Pattern |
|---|---|---|---|
| REQ-1 Idempotency | `run_analysis(c) == run_analysis(c)` | `tests/test_properties.py` | Invariant |
| REQ-2 Monotonicity | `len(run_analysis(c_bad)) >= len(run_analysis(c))` | `tests/test_properties.py` | Metamorphic |
| REQ-3 Severity Membership | `all(f.severity in Severity for f in results)` | `tests/test_properties.py` | Invariant |
