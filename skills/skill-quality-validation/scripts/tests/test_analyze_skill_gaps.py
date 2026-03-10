from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Module loader (mirrors test_validate_skill.py pattern)
# ---------------------------------------------------------------------------


def _load_analyzer_module():
    analyzer_path = Path(__file__).resolve().parents[1] / "analyze_skill_gaps.py"
    spec = importlib.util.spec_from_file_location("analyze_skill_gaps", analyzer_path)
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


# Load once for the whole test session
_mod = _load_analyzer_module()
GapAnalyzer = _mod.GapAnalyzer
GapReport = _mod.GapReport
DimensionScore = _mod.DimensionScore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_analyzer(content: str, file_path: str = "/tmp/fake/SKILL.md") -> GapAnalyzer:
    return GapAnalyzer(content, file_path)


def _minimal_skill(name: str = "my-skill", description: str = "") -> str:
    """Return a minimal SKILL.md with only name + description."""
    desc = description or (
        "Use when you need a concise example skill. "
        "Provides basic testing functionality."
    )
    return f"---\nname: {name}\ndescription: {desc}\n---\n\n## When to Use\n- Use this.\n"


# ---------------------------------------------------------------------------
# 1. Frontmatter parsing
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_parses_name_and_description(self):
        content = _minimal_skill("test-skill", "Use when you need a test. Covers basics.")
        analyzer = _make_analyzer(content)
        assert analyzer.frontmatter["name"] == "test-skill"
        assert "Use when" in analyzer.frontmatter["description"]

    def test_returns_empty_dict_when_no_frontmatter(self):
        content = "# Just a heading\nNo frontmatter here."
        analyzer = _make_analyzer(content)
        assert analyzer.frontmatter == {}

    def test_folded_block_scalar_description(self):
        content = (
            "---\n"
            "name: folded-skill\n"
            "description: >\n"
            "  Use when you need a folded description example.\n"
            "  Supports multi-line block scalars in YAML.\n"
            "---\n\n## When to Use\n- Example.\n"
        )
        analyzer = _make_analyzer(content)
        desc = analyzer.frontmatter.get("description", "")
        assert "folded description example" in desc
        assert "multi-line" in desc

    def test_ignores_metadata_block_values(self):
        """metadata: sub-keys should be parsed under 'metadata' key, not top-level."""
        content = (
            "---\n"
            "name: legacy-skill\n"
            "description: Use when testing legacy frontmatter parsing.\n"
            "metadata:\n"
            "  version: 1.0\n"
            "  author: tester\n"
            "---\n\n## When to Use\n- Legacy.\n"
        )
        analyzer = _make_analyzer(content)
        assert "version" not in analyzer.frontmatter
        assert "author" not in analyzer.frontmatter
        assert analyzer.frontmatter.get("metadata", {}).get("version") == "1.0"

    def test_minimal_frontmatter_has_only_two_keys(self):
        content = _minimal_skill()
        analyzer = _make_analyzer(content)
        assert set(analyzer.frontmatter.keys()) == {"name", "description"}


# ---------------------------------------------------------------------------
# 2. Progressive Disclosure scoring (references/ directory)
# ---------------------------------------------------------------------------


class TestProgressiveDisclosure:
    def test_no_references_dir_scores_lower(self, tmp_path):
        skill_dir = tmp_path / "bare-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            _minimal_skill("bare-skill", "Use when testing bare skill with no references directory."),
            encoding="utf-8",
        )
        analyzer = GapAnalyzer(skill_file.read_text(encoding="utf-8"), str(skill_file))
        result = analyzer.analyze_progressive_disclosure()
        # No references/ means no ref_count bonus
        assert result.score < 1.0
        assert any("references/" in r for r in result.recommendations)

    def test_one_reference_file_partial_bonus(self, tmp_path):
        skill_dir = tmp_path / "minimal-ref"
        ref_dir = skill_dir / "references"
        ref_dir.mkdir(parents=True)
        (ref_dir / "SKILL.ja.md").write_text("# 日本語版\n", encoding="utf-8")
        skill_file = skill_dir / "SKILL.md"
        long_desc = (
            "Use when you need a skill with exactly one reference file. "
            "This tests the partial references scoring branch."
        )
        skill_file.write_text(_minimal_skill("minimal-ref", long_desc), encoding="utf-8")
        analyzer = GapAnalyzer(skill_file.read_text(encoding="utf-8"), str(skill_file))
        result = analyzer.analyze_progressive_disclosure()
        assert any("最低限" in d for d in result.details)

    def test_two_or_more_reference_files_full_bonus(self, tmp_path):
        skill_dir = tmp_path / "rich-ref"
        ref_dir = skill_dir / "references"
        ref_dir.mkdir(parents=True)
        (ref_dir / "SKILL.ja.md").write_text("# 日本語版\n", encoding="utf-8")
        (ref_dir / "deep-dive.md").write_text("# Deep dive\n", encoding="utf-8")
        skill_file = skill_dir / "SKILL.md"
        long_desc = (
            "Use when you need a skill with multiple reference files. "
            "Tests the full references bonus in progressive disclosure."
        )
        skill_file.write_text(_minimal_skill("rich-ref", long_desc), encoding="utf-8")
        analyzer = GapAnalyzer(skill_file.read_text(encoding="utf-8"), str(skill_file))
        result = analyzer.analyze_progressive_disclosure()
        assert any("活用あり" in d for d in result.details)


# ---------------------------------------------------------------------------
# 3. GapReport.compute_overall() — priority tiers
# ---------------------------------------------------------------------------


class TestGapReportPriority:
    def _make_report_with_score(self, score: float) -> GapReport:
        report = GapReport(skill_name="test", skill_path="/fake/SKILL.md")
        report.dimensions = [DimensionScore(name="dim", score=score, max_score=1.0)]
        report.compute_overall()
        return report

    def test_critical_priority_below_30_percent(self):
        report = self._make_report_with_score(0.25)
        assert report.priority == "critical"
        assert report.overall_score == pytest.approx(0.25)

    def test_high_priority_between_30_and_50(self):
        report = self._make_report_with_score(0.45)
        assert report.priority == "high"

    def test_medium_priority_between_50_and_70(self):
        report = self._make_report_with_score(0.60)
        assert report.priority == "medium"

    def test_low_priority_at_or_above_70(self):
        report = self._make_report_with_score(0.75)
        assert report.priority == "low"

    def test_empty_dimensions_leaves_zero_score(self):
        report = GapReport(skill_name="empty", skill_path="/fake/SKILL.md")
        report.compute_overall()
        assert report.overall_score == 0.0
        assert report.priority == "low"


# ---------------------------------------------------------------------------
# 4. Auto-detect skills/ directory (parent.parent.parent fix)
# ---------------------------------------------------------------------------


class TestAutoDetectSkillsDir:
    def test_script_resolves_to_skills_root(self):
        """
        analyze_skill_gaps.py lives at:
          skills/skill-quality-validation/scripts/analyze_skill_gaps.py

        main() uses:  script_dir = Path(__file__).resolve().parent  (= scripts/)
                      skills_dir = script_dir.parent.parent          (= skills/)

        This test verifies that 2 levels up from the resolved scripts/ dir
        gives the skills/ root.
        """
        analyzer_path = Path(_mod.__file__).resolve()
        script_dir = analyzer_path.parent          # scripts/
        auto_detected = script_dir.parent.parent   # skills/
        assert auto_detected.name == "skills", (
            f"Expected auto-detect to resolve to 'skills/', got '{auto_detected}'. "
            "Check the resolve().parent.parent path in main()."
        )

    def test_script_is_three_levels_deep_in_skills(self):
        """Verify the depth assumption: scripts/ dir is 2 levels below skills/ root."""
        analyzer_path = Path(_mod.__file__).resolve()
        # File is: skills/skill-quality-validation/scripts/analyze_skill_gaps.py
        # So going up from the FILE: scripts -> skill-quality-validation -> skills
        depth_names = [
            analyzer_path.parent.name,           # scripts
            analyzer_path.parent.parent.name,    # skill-quality-validation
            analyzer_path.parent.parent.parent.name,  # skills
        ]
        assert depth_names == ["scripts", "skill-quality-validation", "skills"]
