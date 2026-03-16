from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "package_skill.py"
    spec = importlib.util.spec_from_file_location("unified_package_skill", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_package_skill_excludes_output_archive_and_pycache(tmp_path: Path):
    mod = load_module()
    skill_dir = tmp_path / "sample-skill"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "__pycache__").mkdir()
    (skill_dir / "SKILL.md").write_text("# Sample Skill\n", encoding="utf-8")
    (skill_dir / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
    (skill_dir / "__pycache__" / "module.pyc").write_bytes(b"pyc")

    output = skill_dir / "dist" / "sample.skill"
    output.parent.mkdir()

    mod.package_skill(skill_dir, output)

    with zipfile.ZipFile(output) as archive:
        names = sorted(archive.namelist())

    assert names == ["SKILL.md", "references/guide.md"]
