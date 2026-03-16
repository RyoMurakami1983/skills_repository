from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "validate_skill.py"
    spec = importlib.util.spec_from_file_location("unified_validate_skill", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_skill(tmp_path: Path, folder: str, content: str) -> Path:
    skill_dir = tmp_path / folder
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    (skill_dir / "references" / "SKILL.ja.md").write_text("# ja\n", encoding="utf-8")
    return skill_dir / "SKILL.md"


def test_l1_passes_for_router_style_skill(tmp_path: Path):
    mod = load_module()
    skill_path = write_skill(
        tmp_path,
        "router-skill",
        """---
name: router-skill
description: >
  Route skill operations. Use when creating skills, validating drafts, or
  improving published guidance.
compatibility: test
---

# Router Skill

## When to Use This Skill

Use this skill when:
- Creating router logic for skill workflows
- Validating critical checks before rollout
- Improving bundled skill guidance with evidence

## Decision Table

| Intent | Route |
| --- | --- |
| Create | new |
| Improve | improve |
""",
    )
    report = mod.validate(skill_path, "L1")
    assert report.critical_passed is True
    assert len(report.critical) == 5


def test_l1_fails_without_use_when_trigger(tmp_path: Path):
    mod = load_module()
    skill_path = write_skill(
        tmp_path,
        "bad-skill",
        """---
name: bad-skill
description: Missing trigger phrase.
---

# Bad Skill

## When to Use This Skill

Use this skill when:
- Creating a document
- Updating a document
- Reviewing a document

## Workflow: Minimal

### Step 1 — Do the thing
Because the workflow needs a step.
""",
    )
    report = mod.validate(skill_path, "L1")
    assert report.critical_passed is False
    failed_ids = {check.id for check in report.critical if not check.passed}
    assert "C3" in failed_ids
