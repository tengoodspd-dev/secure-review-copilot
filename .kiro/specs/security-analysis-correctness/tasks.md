# Implementation Plan: Security Analysis Correctness

## Overview

Align the existing property-based tests in `tests/test_properties.py` precisely to the acceptance criteria: correct failure messages, correct docstrings, and confirmed passing runs. No new source files and no changes to `src/analyser.py`.

## Tasks

- [x] 1. Audit existing tests against acceptance criteria
  - Read `tests/test_properties.py` and compare each test's assertion messages and docstrings to REQ-1 AC3, REQ-2 AC4, and REQ-3 AC3
  - Note any gaps between the current implementation and the required failure message content
  - _Requirements: 1.1, 1.3, 2.1, 2.2, 2.4, 3.1, 3.3_

- [x] 2. Update idempotency test
  - [x] 2.1 Update `test_property_idempotency` assertion message
    - Ensure the failure message includes both `result1` and `result2` Finding lists
    - Verify docstring references **Property 1: Idempotency** from the design document
    - _Requirements: 1.1, 1.3_

  - [ ]* 2.2 Run `test_property_idempotency` in isolation
    - Execute `pytest tests/test_properties.py::test_property_idempotency -v` and confirm it passes
    - _Requirements: 1.2_

- [x] 3. Update monotonicity test
  - [x] 3.1 Update `test_property_monotonicity` assertion message and docstring
    - Ensure the failure message includes: original config, mutated config, original finding count, and mutated finding count
    - Confirm both mutations (`mfa_enabled=False` and `storage_encrypted=False`) are applied simultaneously
    - Verify docstring references **Property 2: Monotonicity under weakening** from the design document
    - _Requirements: 2.1, 2.2, 2.4_

  - [ ]* 3.2 Run `test_property_monotonicity` in isolation
    - Execute `pytest tests/test_properties.py::test_property_monotonicity -v` and confirm it passes
    - _Requirements: 2.3_

- [x] 4. Update severity membership test
  - [x] 4.1 Update `test_property_severity_membership` assertion message and docstring
    - Ensure the failure message includes the offending `control_id` and the invalid `severity` value
    - Verify docstring references **Property 3: Severity membership invariant** from the design document
    - _Requirements: 3.1, 3.3_

  - [ ]* 4.2 Run `test_property_severity_membership` in isolation
    - Execute `pytest tests/test_properties.py::test_property_severity_membership -v` and confirm it passes
    - _Requirements: 3.2_

- [x] 5. Final checkpoint — confirm all tests pass
  - Run `pytest tests/test_properties.py -v` and confirm all three property tests pass with `@settings(max_examples=50)`
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- All work is confined to `tests/test_properties.py` — no other files should be modified
- Each task references specific requirements for traceability
- The existing tests already implement the core logic; these tasks ensure the failure messages precisely satisfy the acceptance criteria

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["2.1", "3.1", "4.1"] },
    { "id": 1, "tasks": ["2.2", "3.2", "4.2"] }
  ]
}
```
