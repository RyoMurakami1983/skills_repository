from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest


def load_module():
    path = Path(__file__).resolve().parents[1] / "run_loop.py"
    spec = importlib.util.spec_from_file_location("unified_run_loop", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_rewrite_description_replaces_frontmatter_description(tmp_path: Path):
    mod = load_module()
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(
        """---
name: sample-skill
description: >
  Old description text.
compatibility: pytest
---

# Sample Skill
""",
        encoding="utf-8",
    )

    mod.rewrite_description(
        skill_path,
        'Improved description: keeps YAML-sensitive text like "#" and ":".',
    )

    content = skill_path.read_text(encoding="utf-8")
    assert "description: >\n  Improved description: keeps YAML-sensitive text like \"#\" and \":\".\n" in content
    assert "compatibility: pytest" in content
    assert "Old description text." not in content


def test_load_validator_raises_before_module_from_spec_when_loader_missing(monkeypatch: pytest.MonkeyPatch):
    mod = load_module()

    monkeypatch.setattr(
        mod.importlib.util,
        "spec_from_file_location",
        lambda *args, **kwargs: importlib.machinery.ModuleSpec("skill_validate_skill", None),
    )

    def fail_if_called(spec):
        raise AssertionError("module_from_spec should not be called")

    monkeypatch.setattr(mod.importlib.util, "module_from_spec", fail_if_called)

    with pytest.raises(ImportError, match="Could not load validator module spec"):
        mod.load_validator()
