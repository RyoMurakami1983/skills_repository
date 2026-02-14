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


def test_get_section_content_ignores_h2_inside_fenced_code_block():
    mod = _load_validator_module()
    content = """---
name: extraction-skill
description: Ensure fenced headings do not truncate section extraction.
author: Tester
invocable: true
---

## Quick Reference
```markdown
## Summary
- This heading is inside a code fence.
```
- Keep this line in Quick Reference.

## Core Principles
- Keep fixtures small and explicit.
"""
    validator = mod.SkillValidator(content=content, file_path="C:\\tmp\\SKILL.md")
    section = validator.get_section_content("Quick Reference")
    assert section is not None
    assert "## Summary" in section
    assert "Keep this line in Quick Reference." in section
    assert "Core Principles" not in section


def test_get_section_content_stops_at_known_h2_when_fence_is_unclosed():
    mod = _load_validator_module()
    content = """---
name: extraction-skill
description: Unclosed fence should not consume subsequent sections.
author: Tester
invocable: true
---

## Quick Reference
```markdown
## Summary
- Fence is intentionally left unclosed.
- This content should remain in Quick Reference.

## Core Principles
- Keep fixtures small and explicit.
"""
    validator = mod.SkillValidator(content=content, file_path="C:\\tmp\\SKILL.md")
    section = validator.get_section_content("Quick Reference")
    assert section is not None
    assert "Fence is intentionally left unclosed." in section
    assert "Core Principles" not in section


def test_get_section_content_does_not_treat_4space_fence_as_real_fence():
    mod = _load_validator_module()
    content = """---
name: extraction-skill
description: Four-space indented fence marker should be treated as code text.
author: Tester
invocable: true
---

## Quick Reference
    ```
## Summary
- This should be treated as a real H2 boundary.

## Core Principles
- Keep fixtures small and explicit.
"""
    validator = mod.SkillValidator(content=content, file_path="C:\\tmp\\SKILL.md")
    section = validator.get_section_content("Quick Reference")
    assert section is not None
    assert "Core Principles" not in section
    assert "Summary" not in section


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

    category_names = {c.name for c in report.categories}
    assert {"Structure", "Content", "Code Quality", "Language"}.issubset(category_names)
    assert report.total_score == sum(c.score for c in report.categories)
    assert report.total_max_score == sum(c.max_score for c in report.categories)


# --- Warning system tests ---


def _write_skill_with_ja(tmp_path: Path, folder_name: str, en_content: str, ja_content: str) -> Path:
    """Write both EN and JA skill files, return path to EN SKILL.md"""
    skill_dir = tmp_path / folder_name
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(en_content, encoding="utf-8")
    (skill_dir / "references" / "SKILL.ja.md").write_text(ja_content, encoding="utf-8")
    return skill_dir / "SKILL.md"


def test_warning_en_ja_h2_mismatch(tmp_path: Path):
    """W1.1: H2 count mismatch between EN and JA triggers warning"""
    mod = _load_validator_module()
    en = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\n## B\n## C\n"
    ja = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\n## B\n"
    file_path = _write_skill_with_ja(tmp_path, "h2-mismatch", en, ja)
    report = mod.validate_skill_file(str(file_path))
    w_ids = [w.id for w in report.warnings]
    assert "W1.1" in w_ids


def test_warning_en_ja_step_mismatch(tmp_path: Path):
    """W1.3: Step count mismatch triggers warning"""
    mod = _load_validator_module()
    en = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n### Step 1\nDo A\n### Step 2\nDo B\n"
    ja = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n### Step 1\nDo A\n"
    file_path = _write_skill_with_ja(tmp_path, "step-mismatch", en, ja)
    report = mod.validate_skill_file(str(file_path))
    w_ids = [w.id for w in report.warnings]
    assert "W1.3" in w_ids


def test_warning_step_missing_values(tmp_path: Path):
    """W2: Step without Values marker triggers warning"""
    mod = _load_validator_module()
    en = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n### Step 1: Setup\nDo setup\n### Step 2: Run\nDo run\n> **Values**: 基礎と型\n"
    ja = "# dummy\n"
    file_path = _write_skill_with_ja(tmp_path, "missing-values", en, ja)
    report = mod.validate_skill_file(str(file_path))
    w_ids = [w.id for w in report.warnings]
    # Step 1 has no Values, Step 2 has Values
    assert "W2.1" in w_ids
    assert "W2.2" not in w_ids


def test_warning_ja_safety_keywords(tmp_path: Path):
    """W3.1: Safety keywords in JA trigger warning"""
    mod = _load_validator_module()
    en = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\nContent\n"
    ja = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\nセキュリティに注意。削除は禁止。\n"
    file_path = _write_skill_with_ja(tmp_path, "safety-kw", en, ja)
    report = mod.validate_skill_file(str(file_path))
    w_ids = [w.id for w in report.warnings]
    assert "W3.1" in w_ids
    assert "W3.2" in w_ids


def test_no_warnings_when_aligned(tmp_path: Path):
    """No warnings when EN/JA are structurally aligned and no safety keywords"""
    mod = _load_validator_module()
    en = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\n## B\n"
    ja = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\n## B\n"
    file_path = _write_skill_with_ja(tmp_path, "aligned", en, ja)
    report = mod.validate_skill_file(str(file_path))
    assert len(report.warnings) == 0


def test_warnings_do_not_affect_pass_fail(tmp_path: Path):
    """Warnings must not change overall_passed result"""
    mod = _load_validator_module()
    en = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\n## B\n## C\n"
    ja = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\nセキュリティ削除禁止\n"
    file_path = _write_skill_with_ja(tmp_path, "no-affect", en, ja)
    report = mod.validate_skill_file(str(file_path))
    # There should be warnings
    assert len(report.warnings) > 0
    # But overall_passed should be based only on category scores, not warnings
    expected_passed = (report.overall_percentage >= 85 and
                       all(c.passed for c in report.categories))
    assert report.overall_passed == expected_passed


def test_warning_glossary_missing_date(tmp_path: Path):
    """W4: Missing glossary date triggers warning"""
    mod = _load_validator_module()
    # Create .github/copilot-instructions.md without glossary date
    github_dir = tmp_path / "test-skill" / ".github"
    # We need repo root detection to work: place .github at parent of skill dir
    repo_root = tmp_path / "repo"
    (repo_root / ".github").mkdir(parents=True, exist_ok=True)
    (repo_root / ".github" / "copilot-instructions.md").write_text(
        "# Instructions\nNo glossary here.\n", encoding="utf-8"
    )
    skill_dir = repo_root / "skills" / "test-skill"
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    en = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\n"
    (skill_dir / "SKILL.md").write_text(en, encoding="utf-8")
    report = mod.validate_skill_file(str(skill_dir / "SKILL.md"))
    w_ids = [w.id for w in report.warnings]
    assert "W4" in w_ids


def test_warning_glossary_stale(tmp_path: Path):
    """W4: Stale glossary date triggers warning when skill is newer"""
    mod = _load_validator_module()
    import time
    repo_root = tmp_path / "repo2"
    (repo_root / ".github").mkdir(parents=True, exist_ok=True)
    (repo_root / ".github" / "copilot-instructions.md").write_text(
        "# Instructions\nGlossary Last Updated: 2020-01-01\n", encoding="utf-8"
    )
    skill_dir = repo_root / "skills" / "test-skill"
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    en = "---\nname: test\ndescription: test\nauthor: T\ninvocable: true\n---\n## A\n"
    (skill_dir / "SKILL.md").write_text(en, encoding="utf-8")
    report = mod.validate_skill_file(str(skill_dir / "SKILL.md"))
    w_ids = [w.id for w in report.warnings]
    assert "W4" in w_ids
