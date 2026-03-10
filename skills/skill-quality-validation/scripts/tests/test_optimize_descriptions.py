"""test_optimize_descriptions.py

Tests for the optimize_descriptions.py script.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Module loader (mirrors test_validate_skill.py pattern)
# ---------------------------------------------------------------------------

def _load_module():
    here = Path(__file__).parent
    script = here.parent / "optimize_descriptions.py"
    spec = importlib.util.spec_from_file_location("optimize_descriptions", script)
    assert spec and spec.loader, "Could not locate optimize_descriptions.py"
    mod = importlib.util.module_from_spec(spec)
    # Register in sys.modules BEFORE exec so dataclass forward-ref resolution works
    import sys as _sys
    _sys.modules["optimize_descriptions"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_skill(tmp_path: Path, skill_id: str, description: str, when_bullets: list[str] | None = None) -> Path:
    skill_dir = tmp_path / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    bullets = "\n".join(f"- {b}" for b in (when_bullets or []))
    content = (
        f'---\nname: {skill_id}\ndescription: "{description}"\n---\n\n'
        f'## When to Use This Skill\n{bullets}\n\n'
        '## Core Principles\n- Keep it simple.\n'
    )
    path = skill_dir / "SKILL.md"
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# W7 checker tests
# ---------------------------------------------------------------------------

def test_check_w7_passes_all_for_good_description():
    mod = _load_module()
    desc = "Use when validating skill quality — checks structure, content, language, and code quality gates."
    result = mod.check_w7(desc)
    assert result.passes_w7_1, f"W7.1 failed: {len(desc)} chars"
    assert result.passes_w7_2, "W7.2 failed: no verb"
    assert result.passes_w7_3, "W7.3 failed: no enumeration"
    assert result.passes_all


def test_check_w7_fails_short_description():
    mod = _load_module()
    result = mod.check_w7("Short desc")
    assert not result.passes_w7_1
    assert "W7.1" in result.failing_ids


def test_check_w7_fails_missing_verb():
    mod = _load_module()
    # Long enough, has commas, but no recognized action verb from the approved list.
    # Deliberately avoids: check, run, validate, review, analyze, use, write, etc.
    desc = "A tool for structural parity assessment between bilingual documentation files, targeting all heading hierarchies across language versions."
    result = mod.check_w7(desc)
    assert not result.passes_w7_2
    assert "W7.2" in result.failing_ids


def test_check_w7_fails_no_enumeration():
    mod = _load_module()
    # Has verb, ≥80 chars, but no comma-separated items
    desc = "Use when validating a single SKILL.md file in isolation without any comparative baseline."
    result = mod.check_w7(desc)
    assert not result.passes_w7_3
    assert "W7.3" in result.failing_ids


def test_parse_frontmatter_block_scalar(tmp_path: Path):
    """_parse_frontmatter should collapse YAML block scalar description into one string."""
    mod = _load_module()
    skill_dir = tmp_path / "skill-block"
    skill_dir.mkdir()
    content = (
        "---\n"
        "name: skill-block\n"
        "description: >\n"
        "  Use when deploying dotnet skills to a project directory.\n"
        "  Supports multiple skill categories and target directories.\n"
        "---\n\n"
        "## When to Use This Skill\n- Deploying skills\n"
    )
    path = skill_dir / "SKILL.md"
    path.write_text(content, encoding="utf-8")

    fm = mod._parse_frontmatter(content)
    assert "description" in fm
    assert "Use when deploying" in fm["description"]
    # Should be a single string (no newlines from block scalar continuation)
    assert "\n" not in fm["description"]




def test_rule_based_produces_w7_compliant_description():
    mod = _load_module()
    provider = mod.RuleBasedProvider()
    when_to_use = [
        "Creating a new skill from scratch",
        "Defining workflow patterns for a team",
        "Setting up bilingual documentation",
        "Reviewing skill quality before publishing",
    ]
    improved = provider.improve("skills-author-skill", "短い説明", when_to_use)
    w7 = mod.check_w7(improved)
    assert w7.passes_w7_1, f"W7.1 failed: {len(improved)} chars — {improved!r}"
    assert w7.passes_w7_2, f"W7.2 failed: no verb — {improved!r}"
    assert w7.passes_w7_3, f"W7.3 failed: no enumeration — {improved!r}"


def test_rule_based_works_with_no_bullets():
    mod = _load_module()
    provider = mod.RuleBasedProvider()
    improved = provider.improve("skills-validate-skill", "", [])
    w7 = mod.check_w7(improved)
    assert w7.passes_all, f"W7 failed with no bullets: {improved!r}"


def test_rule_based_does_not_exceed_512_chars():
    mod = _load_module()
    provider = mod.RuleBasedProvider()
    long_bullets = [f"A very long capability phrase number {i} that says many things" for i in range(10)]
    improved = provider.improve("some-skill", "x", long_bullets)
    assert len(improved) <= 512


# ---------------------------------------------------------------------------
# Scanner tests
# ---------------------------------------------------------------------------

def test_scan_finds_skill_files(tmp_path: Path):
    mod = _load_module()
    _write_skill(tmp_path, "skill-a", "Use when running quality checks on a SKILL.md — validates structure, content, language, and code quality.")
    _write_skill(tmp_path, "skill-b", "短い")
    report = mod.scan_all(tmp_path, mod.RuleBasedProvider(), skill_id_filter=None)
    assert report.total == 2
    assert report.passing == 1
    assert report.failing == 1


def test_scan_filter_by_skill_id(tmp_path: Path):
    mod = _load_module()
    _write_skill(tmp_path, "skill-a", "Use when running quality checks on a SKILL.md — validates structure, content, language, and code quality.")
    _write_skill(tmp_path, "skill-b", "短い")
    report = mod.scan_all(tmp_path, mod.RuleBasedProvider(), skill_id_filter="skill-a")
    assert report.total == 1
    assert report.results[0].skill_id == "skill-a"


def test_scan_populates_suggested_desc_for_failing(tmp_path: Path):
    mod = _load_module()
    _write_skill(tmp_path, "skill-x", "短い", when_bullets=["Doing something useful", "Handling edge cases"])
    report = mod.scan_all(tmp_path, mod.RuleBasedProvider(), skill_id_filter=None)
    failing = [r for r in report.results if not r.w7.passes_all]
    assert len(failing) == 1
    assert failing[0].suggested_desc != ""
    w7 = mod.check_w7(failing[0].suggested_desc)
    assert w7.passes_all, f"Suggested desc not W7 compliant: {failing[0].suggested_desc!r}"


def test_scan_no_suggestion_for_passing(tmp_path: Path):
    mod = _load_module()
    good_desc = "Use when validating skill quality — checks structure, content, language, and code quality gates."
    _write_skill(tmp_path, "skill-good", good_desc)
    report = mod.scan_all(tmp_path, mod.RuleBasedProvider(), skill_id_filter=None)
    assert report.passing == 1
    assert report.results[0].suggested_desc == ""


# ---------------------------------------------------------------------------
# Apply tests
# ---------------------------------------------------------------------------

def test_apply_updates_file(tmp_path: Path):
    mod = _load_module()
    path = _write_skill(tmp_path, "skill-upd", "短い", when_bullets=["Updating things", "Managing workflow"])
    report = mod.scan_all(tmp_path, mod.RuleBasedProvider(), skill_id_filter=None)
    assert report.failing == 1
    result = report.results[0]

    applied = mod.apply_improvement(result)
    assert applied

    updated_content = path.read_text(encoding="utf-8")
    assert result.suggested_desc in updated_content


def test_apply_skips_passing_skill(tmp_path: Path):
    mod = _load_module()
    good_desc = "Use when validating skill quality — checks structure, content, language, and code quality gates."
    path = _write_skill(tmp_path, "skill-pass", good_desc)
    report = mod.scan_all(tmp_path, mod.RuleBasedProvider(), skill_id_filter=None)
    result = report.results[0]

    applied = mod.apply_improvement(result)
    assert not applied  # should not touch passing skills

    # File should be unchanged
    assert path.read_text(encoding="utf-8").count(good_desc) == 1


# ---------------------------------------------------------------------------
# JSON output test
# ---------------------------------------------------------------------------

def test_json_output_structure(tmp_path: Path, capsys):
    mod = _load_module()
    _write_skill(tmp_path, "skill-json", "短い")
    report = mod.scan_all(tmp_path, mod.RuleBasedProvider(), skill_id_filter=None)
    mod.print_json_report(report)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "summary" in data
    assert "results" in data
    assert data["summary"]["total"] == 1
    assert isinstance(data["results"][0]["failing_ids"], list)


# ---------------------------------------------------------------------------
# GitHubModelsProvider fallback test
# ---------------------------------------------------------------------------

def test_github_models_provider_falls_back_on_error(monkeypatch):
    """When gh api fails, GitHubModelsProvider should return a rule-based result."""
    mod = _load_module()

    # Simulate `gh api` returning a non-zero exit code
    def _failing_run(*args, **kwargs):
        return MagicMock(returncode=1, stdout="", stderr="connection error")

    monkeypatch.setattr(subprocess, "run", _failing_run)

    provider = mod.GitHubModelsProvider()
    result = provider.improve("skills-author-skill", "短い", ["Creating skills", "Reviewing quality"])
    # Should not raise; should return a non-empty string
    assert isinstance(result, str)
    assert len(result) > 0
