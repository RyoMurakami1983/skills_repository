"""Tests for W5: EN SKILL.md Japanese leak detection."""

from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path


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
    """Create a WarningValidator instance with given content."""
    mod = _load_validator_module()
    filepath = tmp_path / filename
    filepath.write_text(content, encoding="utf-8")
    return mod.WarningValidator(content, str(filepath))


# --- Minimal valid SKILL.md skeleton ---
FRONTMATTER = """\
---
name: test-skill
description: A test skill.
metadata:
  author: tester
---
"""

EN_CLEAN = FRONTMATTER + """\
## When to Use This Skill

Use this skill when you need to test something.

## Core Principles

1. **Simplicity** — Keep it simple.

## Best Practices

- Write clear code.
"""


class TestW5TruePositive:
    """W5 should detect Japanese text in EN SKILL.md."""

    def test_japanese_in_body_detected(self, tmp_path: Path):
        content = FRONTMATTER + "## When to Use\n\nこのスキルは日本語テストです。\n"
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_en_japanese_leak()
        assert len(warnings) == 1
        assert warnings[0].id == "W5"
        assert "このスキルは日本語テストです。" in warnings[0].details

    def test_japanese_in_table_detected(self, tmp_path: Path):
        content = FRONTMATTER + "| Type | Example |\n|------|--------|\n| feat | 通知を追加 |\n"
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_en_japanese_leak()
        assert len(warnings) == 1
        assert warnings[0].id == "W5"


class TestW5FalsePositiveAvoidance:
    """W5 should NOT flag allowed Japanese contexts."""

    def test_values_in_parentheses_allowed(self, tmp_path: Path):
        content = EN_CLEAN + "\n1. **Principle** — Description (基礎と型)\n"
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_en_japanese_leak()
        assert len(warnings) == 0

    def test_values_blockquote_allowed(self, tmp_path: Path):
        content = EN_CLEAN + "\n> **Values**: 基礎と型 / 成長の複利\n"
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_en_japanese_leak()
        assert len(warnings) == 0

    def test_code_block_allowed(self, tmp_path: Path):
        content = EN_CLEAN + "\n```bash\ngit commit -m \"feat: 通知を追加\"\n```\n"
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_en_japanese_leak()
        assert len(warnings) == 0

    def test_frontmatter_allowed(self, tmp_path: Path):
        content = "---\nname: テストスキル\ndescription: 日本語テスト\n---\n\n## When to Use\n\nEnglish only.\n"
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_en_japanese_leak()
        assert len(warnings) == 0


class TestW5SkipJaFile:
    """W5 should skip JA version files entirely."""

    def test_ja_file_skipped(self, tmp_path: Path):
        content = FRONTMATTER + "## このスキルを使うとき\n\n日本語ファイルは検知対象外。\n"
        v = _make_warning_validator(tmp_path, "SKILL.ja.md", content)
        warnings = v._check_en_japanese_leak()
        assert len(warnings) == 0


class TestW5LineNumbers:
    """W5 should report line numbers from original file, not cleaned content."""

    def test_line_numbers_match_original(self, tmp_path: Path):
        content = FRONTMATTER + (
            "## When to Use\n\n"
            "English line.\n"
            "Another English line.\n"
            "日本語が混入した行。\n"
        )
        v = _make_warning_validator(tmp_path, "SKILL.md", content)
        warnings = v._check_en_japanese_leak()
        assert len(warnings) == 1
        # Frontmatter is 6 lines (---, name, description, metadata, author, ---),
        # then "## When to Use\n\n" is 2 lines, "English line.\n" is 1, "Another...\n" is 1
        # "日本語が混入した行。" should be on line 11 of original
        assert "L11" in warnings[0].details
