"""Tests for W7: Description quality checks (W7.1 length / W7.2 verb / W7.3 enumeration)."""

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
        sys.platform = "linux"
        spec.loader.exec_module(module)
    finally:
        sys.platform = original_platform
    return module


def _make_warning_validator(tmp_path: Path, filename: str, content: str):
    mod = _load_validator_module()
    filepath = tmp_path / filename
    filepath.write_text(content, encoding="utf-8")
    return mod.WarningValidator(content, str(filepath))


def _make_skill(description: str) -> str:
    """Return minimal SKILL.md with the given description."""
    return f"---\nname: test-skill\ndescription: {description!r}\n---\n\n## When to Use This Skill\n\nUse this skill.\n"


def _make_skill_block(description_lines: list[str]) -> str:
    """Return SKILL.md with a YAML block scalar description."""
    body = "\n".join(f"  {line}" for line in description_lines)
    return f"---\nname: test-skill\ndescription: >\n{body}\n---\n\n## When to Use\n\nUse this skill.\n"


class TestW71ShortDescription:
    """W7.1 triggers when description is shorter than 80 characters."""

    def test_short_description_triggers_warning(self, tmp_path: Path):
        # 30-char description — too short
        content = _make_skill("Use when testing short desc.")
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.1" in ids

    def test_description_exactly_80_chars_no_warning(self, tmp_path: Path):
        # 80+ chars — at or above the boundary, no W7.1 expected
        desc = "Use when you need to validate, review, create, build, or analyze something now!."
        assert len(desc) >= 80
        content = _make_skill(desc)
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.1" not in ids

    def test_long_description_no_w71(self, tmp_path: Path):
        desc = (
            "Create and manage workflow automation tasks using standard patterns. "
            "Use when setting up pipelines, validating inputs, or deploying artifacts."
        )
        assert len(desc) > 80
        content = _make_skill(desc)
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.1" not in ids


class TestW72ActionVerb:
    """W7.2 triggers when no recognized action verb is found."""

    def test_no_verb_triggers_warning(self, tmp_path: Path):
        # No action verb — purely noun-phrase description (padded to ≥80 chars)
        desc = "A comprehensive, reliable, and thoroughly tested quality assurance framework for all projects."
        assert len(desc) >= 80
        content = _make_skill(desc)
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.2" in ids

    def test_action_verb_present_no_warning(self, tmp_path: Path):
        desc = (
            "Create and validate SKILL.md quality against a rubric. "
            "Use when reviewing a new skill, building a suite, or analyzing gaps."
        )
        assert len(desc) >= 80
        content = _make_skill(desc)
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.2" not in ids

    def test_use_when_counts_as_verb(self, tmp_path: Path):
        # 'use' is in the action verb list; "use when" pattern also satisfies W7.2
        desc = (
            "Use when you need to check, review, or validate structured markdown files. "
            "Covers frontmatter, content, code quality, and language checks."
        )
        assert len(desc) >= 80
        content = _make_skill(desc)
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.2" not in ids


class TestW73CapabilityEnumeration:
    """W7.3 triggers when fewer than 2 capability items are enumerated."""

    def test_no_commas_triggers_warning(self, tmp_path: Path):
        # Single sentence with no comma — item_count = 0
        desc = "Use when you need to validate markdown files thoroughly in any context."
        assert "," not in desc
        content = _make_skill(desc)
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.3" in ids

    def test_single_comma_yields_two_items_no_warning(self, tmp_path: Path):
        # "A, B" → 1 comma-clause → item_count = 1+1 = 2 → no W7.3
        desc = (
            "Validate SKILL.md quality, checking structure and content completeness. "
            "Use when reviewing or auditing skill files before submission."
        )
        content = _make_skill(desc)
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.3" not in ids

    def test_multiple_commas_no_warning(self, tmp_path: Path):
        desc = (
            "Create, review, or validate SKILL.md files against quality standards. "
            "Use when building a new skill, auditing existing ones, or running CI checks."
        )
        content = _make_skill(desc)
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.3" not in ids


class TestW7BlockScalar:
    """W7 checks work correctly when description uses YAML block scalar (> or |)."""

    def test_block_scalar_short_triggers_w71(self, tmp_path: Path):
        # Block scalar with <80 chars total
        content = _make_skill_block(["Use when testing block scalars."])
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.1" in ids

    def test_block_scalar_long_with_verb_no_w71_w72(self, tmp_path: Path):
        lines = [
            "Create and manage automation tasks using repeatable patterns.",
            "Use when setting up pipelines, validating inputs, or deploying artifacts.",
        ]
        content = _make_skill_block(lines)
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        ids = [w.id for w in warnings]
        assert "W7.1" not in ids
        assert "W7.2" not in ids


class TestW7NoFrontmatter:
    """W7 does not crash when frontmatter is absent."""

    def test_no_frontmatter_returns_empty_warnings(self, tmp_path: Path):
        content = "# No frontmatter\n\nJust some content.\n"
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_description_quality()
        assert warnings == []
