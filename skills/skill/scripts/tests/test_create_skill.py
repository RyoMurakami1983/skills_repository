from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "create_skill.py"
    spec = importlib.util.spec_from_file_location("unified_create_skill", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_create_skill_creates_expected_structure(tmp_path: Path):
    mod = load_module()
    template = (Path(__file__).resolve().parents[2] / "_foundation" / "TEMPLATE.md").read_text(encoding="utf-8")
    output_root = tmp_path / "skills"

    created = mod.create_skill(
        output_root,
        template,
        {
            "name": "sample-skill",
            "description": "Create a sample. Use when testing template generation.",
            "title": "Sample Skill",
            "compatibility": "pytest",
        },
    )

    assert created == output_root / "sample-skill"
    assert (created / "SKILL.md").exists()
    assert (created / "references" / "SKILL.ja.md").exists()
    assert (created / "scripts").is_dir()
    assert (created / "assets").is_dir()


def test_build_ja_stub_uses_folded_description_and_omits_empty_compatibility():
    mod = load_module()

    stub = mod.build_ja_stub(
        "sample-skill",
        'Handle YAML-sensitive text like ":" "#" "[" and quotes safely. Use when drafting metadata.',
        "Sample Skill",
        "",
    )

    assert "description: >\n" in stub
    assert (
        '  Handle YAML-sensitive text like ":" "#" "[" and quotes safely. Use when drafting metadata.\n'
        in stub
    )
    assert "compatibility:" not in stub
