---
name: python-debug-tdd
description: Diagnose and fix Python bugs with a TDD-style workflow (Red → investigation → Green → side-effect checks) while preserving regression coverage. Use when a bug is reported and you need a minimal, verifiable fix.
metadata:
  author: RyoMurakami1983
  tags: [python, tdd, debugging, pytest, regression]
  invocable: false
  tool_versions:
    python: ">=3.11"
    pytest: ">=8.0"
    uv: ">=0.5"
  last_reviewed: "2026-03-05"
---

# Debug Python Bugs with TDD

Single-workflow guide for fixing Python bugs safely by reproducing first, investigating root cause, applying the smallest fix, and keeping regression tests permanently.

## When to Use This Skill

Use this skill when:
- A bug report exists but the failure is not yet reproducible in tests
- You need to avoid broad refactors and ship a minimal, confidence-building fix
- Similar failures have reappeared and regression retention is weak
- Team review asks for objective evidence (`red -> green`) before merge
- You want to collaborate with `@python-shihan` on Pythonic root-cause analysis

Trigger patterns:
- "Works locally but fails in production data shape"
- "Edge case around numeric weighting or penalty coefficients"
- "Constraints mismatch between caller and callee assumptions"
- "Type conversion silently changes behavior (str/int/float/bool)"
- "Timezone, rounding, or default-value drift across layers"

---

## Core Principles

1. **Reproduce before reasoning** — Start from a failing test, not intuition (基礎と型).
2. **Constrain blast radius** — Prefer the smallest code change that turns red to green (余白の設計).
3. **Investigate with hypotheses** — Record assumptions and falsify quickly (ニュートラルな視点).
4. **Protect future work** — Keep regression tests after fix; never delete bug tests (成長の複利).
5. **Improve in thin slices** — Refactor only after green and side-effect checks (継続は力).

---

## Workflow: TDD Bug Fix (Red → Root Cause → Green → Guard)

### Step 1: Reproduce the Bug as a Failing Test (Red)

Create a minimal reproducible test that fails for the reported behavior.

```python
import pytest

def test_calculate_score_handles_penalty_coefficient_regression():
    # Arrange: minimal production-like inputs
    base = 100
    penalty = "0.2"  # bug-prone string payload

    # Act
    result = calculate_score(base=base, penalty=penalty)

    # Assert: expected contract (documented behavior)
    assert result == 80
```

Minimal reproducible test pattern:
- Keep only one behavioral expectation per test
- Inline only the minimum fixture data needed to fail
- Encode expected domain contract in assertion message/comments
- Name test with defect context (`..._regression`, `..._edge_case`)

Use when bug description is ambiguous and shared understanding is needed.

> **Values**: 基礎と型の追求 / ニュートラルな視点

### Step 2: Investigate Root Cause with a Structured Checklist

Debug from failing path to the first incorrect state transition.

Investigation checklist:
- Input normalization: are `str`, `int`, `float`, `Decimal`, `None` handled explicitly?
- Penalty coefficients: are ranges, defaults, and signs validated?
- Constraints mismatch: does caller assume bounds that callee does not enforce?
- Unit/domain mismatch: percent (`20`) vs ratio (`0.2`) vs basis points (`2000`)
- Ordering effects: do sort/filter/group operations alter deterministic behavior?
- Boundary handling: inclusive/exclusive checks (`>=` vs `>`) and off-by-one
- Time/date conversion: timezone awareness, naive/aware datetime mixing
- Serialization/deserialization: JSON/YAML/env parsing drift

Collaboration note:
- Ask `@python-shihan` to review hypothesis logs and suggest Pythonic narrowing of the failing branch before changing implementation.

Use when multiple plausible causes exist and random edits would create noise.

> **Values**: 温故知新 / ニュートラルな視点

### Step 3: Apply the Smallest Fix to Turn Tests Green (Green)

Implement one focused change, then rerun only relevant tests first, followed by a broader subset.

```python
def calculate_score(base: int, penalty: float | str) -> int:
    penalty_value = float(penalty)
    if not 0 <= penalty_value <= 1:
        raise ValueError("penalty must be in [0, 1]")
    return int(base * (1 - penalty_value))
```

Use when root cause is identified and you can state the intended invariant in one sentence.

> **Values**: 余白の設計 / 基礎と型の追求

### Step 4: Add Side-Effect Tests and Refactor Safely

After green, add focused tests for nearby behavior and perform only readability refactors that keep behavior stable.

Post-fix checklist:
- Add at least 1 adjacent edge-case test (boundary or invalid input)
- Confirm no unrelated snapshot/golden tests changed unexpectedly
- Run targeted quality gates (`pytest -k`, lint, type check)
- Keep function signatures stable unless issue scope explicitly includes API change
- If refactoring, separate commit or clearly split patch sections in PR

Use when the initial fix passes but future regressions are likely in neighboring logic.

> **Values**: 成長の複利 / 継続は力

### Step 5: Retain Regression Protection and Close the Loop

Keep the original failing test as permanent regression coverage and document the failure mode in PR/issue links.

```bash
uv run pytest -k "regression or penalty_coefficient"
uv run pytest
```

Use when preparing merge and handoff to reviewers.

> **Values**: 温故知新 / 成長の複利

---

## Best Practices

- Write the failing test before touching production code.
- Keep bug-fix commits small: `test(red) -> fix(green) -> side-effect tests`.
- Prefer explicit type conversion and range validation at boundaries.
- Log assumptions in issue/PR description so reviewers can replay reasoning.
- Request `@python-shihan` review when bug involves typing, data modeling, or Python idioms.

---

## Common Pitfalls

1. **Fixing code without a failing test**  
   Fix: stop and create a minimal reproducer first.

2. **Overfitting to one fixture**  
   Fix: add one neighboring edge case to confirm generalized behavior.

3. **Silent coercion (`bool("0")`, `int("08")`, float rounding)**  
   Fix: make conversions explicit and validate domain constraints.

4. **Mixing bug fix and large refactor**  
   Fix: isolate behavioral fix from cleanup changes.

---

## Anti-Patterns

- "Maybe-fix" commits without red/green evidence
- Deleting flaky regression tests instead of stabilizing them
- Catch-all `except Exception` to hide root cause
- Expanding issue scope to rewrite modules during incident pressure

---

## Quick Reference

### Minimal command loop

```bash
# 1) Reproduce (red)
uv run pytest -k "<bug_keyword>" -q

# 2) Implement minimal fix
# edit code

# 3) Verify green + nearby effects
uv run pytest -k "<bug_keyword> or <adjacent_case>" -q
uv run pytest -q
```

### Defect triage table

| Symptom | First check | Typical fix |
|---|---|---|
| Wrong weighted result | penalty coefficient scale/range | normalize + validate bounds |
| Sporadic branch behavior | type conversion and truthiness | explicit conversion and guard clauses |
| Caller/callee disagreement | constraints contract | enforce invariant at boundary |
| Date/time drift | timezone normalization | convert to aware datetime in one layer |

### Ready-to-merge gate

- [ ] Original bug reproduced by test (red evidence captured)
- [ ] Minimal fix implemented and all relevant tests green
- [ ] Adjacent side-effect tests added
- [ ] Regression test retained (not removed/skipped)
- [ ] PR links issue and explains root cause in one paragraph
