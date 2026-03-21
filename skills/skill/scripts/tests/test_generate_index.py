from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "generate_index.py"
    spec = importlib.util.spec_from_file_location("unified_generate_index", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_extract_frontmatter_supports_folded_description(tmp_path: Path):
    mod = load_module()
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(
        """---
name: folded-skill
description: >
  既存スキルを evidence ベースで改善する。こんなときに使う:
  公開済みスキルを見直したいとき。
compatibility: pytest
---
""",
        encoding="utf-8",
    )

    frontmatter = mod.extract_frontmatter(skill_path)

    assert frontmatter["description"] == (
        "既存スキルを evidence ベースで改善する。こんなときに使う: 公開済みスキルを見直したいとき。"
    )


def test_build_index_uses_folded_description_snippet(tmp_path: Path):
    mod = load_module()
    skill_dir = tmp_path / "folded-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: folded-skill
description: >
  既存スキルを evidence ベースで改善する。こんなときに使う:
  公開済みスキルを見直したいとき。
---

# Folded Skill
""",
        encoding="utf-8",
    )

    index = mod.build_index(tmp_path)

    assert "- `folded-skill`: 既存スキルを evidence ベースで改善する。こんなときに使う: 公開済みスキルを見直したいとき。" in index
