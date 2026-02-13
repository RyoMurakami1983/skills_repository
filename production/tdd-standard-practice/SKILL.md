---
name: tdd-standard-practice
description: Standardize a production TDD workflow with test lists and Red-Green-Refactor.
author: RyoMurakami1983
tags: [tdd, testing, workflow, ci, quality]
invocable: false
version: 1.0.0
---

# TDD Standard Practice (Production)

Standardize a Test-Driven Development (TDD) workflow that balances delivery speed and production safety for Minimum Viable Product (MVP) and production systems.

**Test List**: A short backlog of behaviors to implement one at a time.  
**Red-Green-Refactor**: Write a failing test, make it pass, then clean up.  
**Developer Testing**: Developers verify their own code with automated tests.

Progression: Simple -> Intermediate -> Advanced examples improve reliability because each stage tightens feedback loops.  
Reason: Tight loops prevent uncertainty and keep changes safe.

## When to Use This Skill

Use this skill when:
- Building MVP or production features that must keep behavior stable under change.
- Changing core logic where customer-visible outcomes must stay consistent.
- Refactoring large modules while keeping a fast safety net of tests.
- Integrating AI-generated code and proving it with executable tests.
- Establishing a team-wide TDD workflow with shared red-green rules.
- Reducing defect leakage into staging or production releases.

## Related Skills

- **`skill-git-commit-practices`** - Commit hygiene for small safe steps
- **`skill-git-review-standards`** - Review quality and evidence checks
- **`skill-issue-intake`** - Capture deferred test debt as issues

---

## Dependencies

- Unit test framework (pytest, NUnit, Jest, etc.)
- Local test runner and fast feedback loop
- Continuous Integration (CI) pipeline to run tests on every change

---

## Core Principles

1. **Test List First** - Capture behavior before coding (基礎と型)
2. **One Step at a Time** - Red then green before refactor (継続は力)
3. **Behavior over Implementation** - Test public behavior (ニュートラル)
4. **Developer Testing** - Close the feedback loop (成長の複利)
5. **Learn and Improve** - Refactor based on test feedback (温故知新)

---

## Pattern 1: Build a Test List

### Overview

Create a small, explicit list of behaviors and pick one item at a time.

### Basic Example

```text
# ✅ CORRECT - pick one item
Test list:
- Reject empty email
- Accept valid email
Pick one: Reject empty email

# ❌ WRONG - multiple targets at once
Test list:
- Reject empty email
- Accept valid email
- Normalize case
Pick one: All three
```

### Intermediate Example

- Order the list by risk and user impact
- Add a "done" checkmark for completed items

### Advanced Example

```markdown
## Test list (PR description)
- [x] Reject empty email
- [ ] Accept valid email
- [ ] Normalize case
```

### When to Use

- At the start of a feature or bug fix
- When requirements are still fuzzy

**Why**: The list prevents skipping steps and keeps focus on one behavior.  
**Values**: 基礎と型 / 成長の複利

---

## Pattern 2: Red-Green-Refactor Loop

### Overview

Run the shortest cycle: failing test, passing code, then cleanup.

### Basic Example

```python
from decimal import Decimal

# Red
def test_price_with_tax():
    assert price_with_tax(Decimal("100.00")) == Decimal("110.00")
```

```python
from decimal import Decimal

# Green
def price_with_tax(amount: Decimal) -> Decimal:
    return (amount * Decimal("1.1")).quantize(Decimal("1.00"))
```

### Intermediate Example

- Refactor duplicate setup after the test passes
- Keep the red-green cycle under 10 minutes

### Advanced Example

- Commit after each green step
- Use a refactor checklist before merging

### When to Use

- For every behavior on the test list

**Why**: Small cycles reduce uncertainty and simplify debugging.  
**Values**: 継続は力 / 成長の複利

---

## Pattern 3: Test First in Small Steps

### Overview

Write one failing assertion that defines the next behavior.

### Basic Example

```python
def test_empty_email_is_invalid():
    assert is_valid_email("") is False
```

### Intermediate Example

- One assertion per test case
- Avoid multiple failures in a single test

### Advanced Example

- Use parameterized tests only after basic cases are green

### When to Use

- When behavior is simple and deterministic

**Why**: One failing test keeps the next action obvious.  
**Values**: 基礎と型 / 継続は力

---

## Pattern 4: Test Public Behavior First

### Overview

Focus tests on public interfaces and user-visible outcomes.

### Basic Example

```python
result = invoice.total_with_tax()
assert result == 110
```

### Intermediate Example

- Prefer API-level tests over internal helpers
- Name tests in terms of user intent

### Advanced Example

- Add contract tests for service boundaries

### When to Use

- When refactoring internal structure
- When exposing APIs to other teams

**Why**: Behavior-focused tests survive refactors.  
**Values**: ニュートラル / 成長の複利

---

## Pattern 5: Mock or Stub at the Boundary

### Overview

Isolate external systems, but keep core logic real.

### Basic Example

```python
# ✅ CORRECT - mock at boundary
gateway = FakePaymentGateway()
service = BillingService(gateway)

# ❌ WRONG - mock inside domain
pricing = MockPriceCalculator()
service = BillingServiceWithMock(pricing)
```

### Intermediate Example

- Use in-memory fakes for databases or queues
- Mock only network or time dependencies

### Advanced Example

```csharp
// ✅ CORRECT - DI for test doubles
using Microsoft.Extensions.DependencyInjection;

var services = new ServiceCollection();
services.AddSingleton<IPaymentGateway, FakePaymentGateway>();
services.AddSingleton<BillingService>();
```

```csharp
// ❌ WRONG - hard-coded dependency in tests
var service = new BillingService(new PaymentGateway());
```

- Enforce a "no mocks inside domain" rule

### When to Use

- When tests become slow or flaky

**Why**: Boundary-only mocks keep tests trustworthy.  
**Values**: 基礎と型 / ニュートラル

---

## Pattern 6: Refactor After Green

### Overview

Only refactor after tests pass, then re-run tests.

### Basic Example

- Run all tests before refactor
- Clean duplication after green

### Intermediate Example

- Extract helper methods with no behavior change
- Keep refactors under 30 minutes

### Advanced Example

- Use automated refactoring tools and re-run tests after each step

### When to Use

- After every green step

**Why**: Refactoring with green tests keeps safety and speed.  
**Values**: 温故知新 / 継続は力

---

## Pattern 7: CI as a Guardrail

### Overview

Make red builds visible and block merges.

### Basic Example

```yaml
# .github/workflows/tests.yml
name: tests
on: [push, pull_request]
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

### Intermediate Example

- Require test checks for merge
- Fail fast on red builds

### Advanced Example

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-q"
```

File: appsettings.json

```json
{
  "Testing": {
    "FastFail": true
  }
}
```

- Separate unit and integration stages
- Enforce coverage thresholds on main

### When to Use

- On every repository that ships to production

**Why**: CI turns local discipline into team-wide safety.  
**Values**: 成長の複利 / 継続は力

---

## Pattern 8: Add Regression Tests for Bugs

### Overview

Reproduce a bug with a failing test before fixing it.

### Basic Example

```python
def test_discount_rounding_bug():
    assert apply_discount(100, 0.1) == 90
```

### Intermediate Example

- Add the test to the test list before coding
- Reference the issue ID in the test name

### Advanced Example

```python
from pathlib import Path

def load_fixture(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Fixture missing: {path}") from exc
```

- Keep a "bug diary" section in release notes

### When to Use

- When fixing production defects

**Why**: Regression tests prevent repeat failures.  
**Values**: 温故知新 / 成長の複利

---

## Best Practices

- Keep tests fast; move slow checks to integration suites
- Keep one failing test at a time
- Use descriptive test names that explain behavior
- Run the full suite before refactor
- Commit only after green
- Review test list items during planning

---

## Common Pitfalls

- Writing multiple failing tests at once  
  Fix: Keep one failing test and finish it before the next.
- Refactoring before green  
  Fix: Only refactor after tests pass.
- Overusing mocks  
  Fix: Mock only at system boundaries.

---

## Anti-Patterns

- Writing tests after the implementation is done
- Excessive mocking of internal logic
- Skipping the test list and jumping to coding
- Combining multiple behaviors in one test

---

## FAQ

**Q: Is TDD required for prototypes?**  
A: Use a lighter approach for prototypes; this skill is optimized for MVP and production.

**Q: How big should a test list be?**  
A: Keep it short and reorder often; the next action should be obvious.

**Q: Can TDD work with legacy code?**  
A: Yes. Start with characterization tests around the current behavior.

---

## Quick Reference

| Step | Action | Output |
|------|--------|--------|
| 1 | Write test list | Next behavior chosen |
| 2 | Write failing test | Red |
| 3 | Implement minimal code | Green |
| 4 | Refactor | Clean code |
| 5 | Commit + push | CI validates |

```text
Test list -> Red -> Green -> Refactor -> Commit
```

---

## Resources

- Kent Beck, "Test-Driven Development by Example"
- T-Wada: Test list and Red-Green-Refactor workflow

---

## Changelog

### Version 1.0.0 (2026-02-13)

- Initial release
- Test list, Red-Green-Refactor, CI, and mock discipline patterns
