from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path

import pytest


@lru_cache(maxsize=1)
def _load_validator_module():
    validator_path = Path(__file__).resolve().parents[1] / "validate_skill.py"
    spec = importlib.util.spec_from_file_location("validate_skill", validator_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    original_platform = sys.platform
    try:
        # Avoid Win32 stdout/stderr re-wrapping during pytest capture.
        sys.platform = "linux"
        spec.loader.exec_module(module)
    finally:
        sys.platform = original_platform
    return module


def _write_skill_file(tmp_path: Path, folder_name: str, content: str) -> Path:
    skill_dir = tmp_path / folder_name
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    (skill_dir / "references" / "SKILL.ja.md").write_text("# ダミー\n", encoding="utf-8")
    return skill_dir / "SKILL.md"


def _find_check(report, category_name: str, check_id: str):
    for category in report.categories:
        if category.name != category_name:
            continue
        for check in category.checks:
            if check.id == check_id:
                return check
    raise AssertionError(f"Check not found: {category_name} / {check_id}")


def test_get_section_content_when_to_use_extracts_bullets():
    mod = _load_validator_module()
    content = """---
name: extraction-skill
description: Minimal content for section extraction test.
author: Tester
invocable: true
---

## When to Use This Skill
- Designing reproducible checks around parsing behavior.
- Implementing focused tests for section extraction.

## Core Principles
- Keep fixtures small and explicit.
"""
    validator = mod.SkillValidator(content=content, file_path="C:\\tmp\\SKILL.md")
    section = validator.get_section_content("When to Use")
    assert section is not None
    assert "Designing reproducible checks" in section
    assert "Core Principles" not in section


@pytest.mark.parametrize(
    "folder_name, skill_name, body, expected_substring",
    [
        (
            "workflow-skill",
            "workflow-skill",
            """## Workflow:
### Step 1: Prepare
```bash
echo prepare
```
### Step 2: Run
```bash
echo run
```
### Step 3: Review
```bash
echo review
```
""",
            "Workflow section found",
        ),
        (
            "legacy-skill",
            "legacy-skill",
            """## Pattern 1: One
Text
## Pattern 2: Two
Text
## Pattern 3: Three
Text
## Pattern 4: Four
Text
## Pattern 5: Five
Text
## Pattern 6: Six
Text
## Pattern 7: Seven
Text
""",
            "Legacy:",
        ),
    ],
)
def test_structure_check_1_7_detects_workflow_or_legacy(tmp_path: Path, folder_name: str, skill_name: str, body: str, expected_substring: str):
    mod = _load_validator_module()
    skill_md = f"""---
name: {skill_name}
description: This fixture validates structure detection behavior.
author: Tester
invocable: true
---

## When to Use This Skill
- Designing deterministic validator tests for markdown structure.
- Implementing workflow and legacy fixtures for parser checks.
- Troubleshooting route detection in mixed skill repositories.
- Validating score aggregation across category results.
- Refactoring validation logic while protecting behavior.

## Core Principles
- Prefer small, explicit fixtures (Values: 基礎と型 / 成長の複利)

{body}

## Common Pitfalls
- Skipping baseline validation before refactoring.

## Anti-Patterns
- Broad edits without focused tests.

## Quick Reference
- uv run python skills\\skill-quality-validation\\scripts\\validate_skill.py PATH
"""
    file_path = _write_skill_file(tmp_path, folder_name, skill_md)
    report = mod.validate_skill_file(str(file_path))
    check = _find_check(report, "Structure", "1.7")
    assert expected_substring in (check.details or "")


def test_router_skips_structure_1_8_and_score_totals_are_consistent(tmp_path: Path):
    mod = _load_validator_module()
    skill_md = """---
name: router-skill
description: Router skill fixture for N/A checks.
author: Tester
invocable: true
---

## When to Use This Skill
- Routing requests to the correct validation workflow.
- Choosing specialized skills when scope is ambiguous.
- Avoiding duplicated validation instructions across skills.

## Core Principles
- Keep routing rules lightweight (Values: 基礎と型 / ニュートラル)

## Workflow:
### Step 1: Decide destination
```text
Route to the best matching skill.
```

## Common Pitfalls
- Not applicable.

## Anti-Patterns
- Not applicable.

## Quick Reference
- skills-validate-skill
"""
    file_path = _write_skill_file(tmp_path, "router-skill", skill_md)
    report = mod.validate_skill_file(str(file_path))

    check = _find_check(report, "Structure", "1.8")
    assert check.passed is True
    assert "N/A" in (check.details or "")

    assert len(report.categories) == 4
    assert report.total_score == sum(c.score for c in report.categories)
    assert report.total_max_score == sum(c.max_score for c in report.categories)
