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


def test_create_router_creates_expected_structure(tmp_path: Path):
    mod = load_module()
    template_root = Path(__file__).resolve().parents[2] / "_foundation"
    workflow_template = (template_root / "TEMPLATE.md").read_text(encoding="utf-8")
    router_template = (template_root / "ROUTER_TEMPLATE.md").read_text(encoding="utf-8")
    sub_skill_template = (template_root / "SUB_SKILL_TEMPLATE.md").read_text(encoding="utf-8")
    output_root = tmp_path / "skills"

    created = mod.create_skill(
        output_root,
        workflow_template,
        {
            "name": "sample-router",
            "type": "router",
            "description": "Route sample flows. Use when choosing between sample modes.",
            "title": "Sample Router",
        },
        router_template=router_template,
        sub_skill_template=sub_skill_template,
    )

    assert created == output_root / "sample-router"
    assert (created / "SKILL.md").exists()
    assert (created / "references" / "SKILL.ja.md").exists()
    assert (created / "scripts").is_dir()
    assert (created / "assets").is_dir()
    assert (created / "_foundation").is_dir()
    assert (created / "sub_skills").is_dir()


def test_create_router_with_sub_skills(tmp_path: Path):
    mod = load_module()
    template_root = Path(__file__).resolve().parents[2] / "_foundation"
    workflow_template = (template_root / "TEMPLATE.md").read_text(encoding="utf-8")
    router_template = (template_root / "ROUTER_TEMPLATE.md").read_text(encoding="utf-8")
    sub_skill_template = (template_root / "SUB_SKILL_TEMPLATE.md").read_text(encoding="utf-8")
    output_root = tmp_path / "skills"

    created = mod.create_skill(
        output_root,
        workflow_template,
        {
            "name": "sample-router",
            "type": "router",
            "description": "Route sample flows. Use when choosing between sample modes.",
            "title": "Sample Router",
            "sub_skills": [
                {
                    "name": "draft",
                    "description": "Draft sample content. Use when starting a draft route.",
                    "intent": "Draft a sample route",
                    "summary": "Route the user into the draft sub-skill.",
                },
                {
                    "name": "review",
                    "description": "Review sample content. Use when checking a review route.",
                },
            ],
        },
        router_template=router_template,
        sub_skill_template=sub_skill_template,
    )

    assert (created / "sub_skills" / "draft" / "SKILL.md").exists()
    assert (created / "sub_skills" / "draft" / "references" / "SKILL.ja.md").exists()
    assert (created / "sub_skills" / "review" / "SKILL.md").exists()
    assert (created / "sub_skills" / "review" / "references" / "SKILL.ja.md").exists()
    router_skill = (created / "SKILL.md").read_text(encoding="utf-8")
    assert "`sub_skills/draft/`" in router_skill
    assert "`sub_skills/review/`" in router_skill
    assert "Draft a sample route" in router_skill


def test_add_sub_skill_to_existing_router(tmp_path: Path):
    mod = load_module()
    template_root = Path(__file__).resolve().parents[2] / "_foundation"
    workflow_template = (template_root / "TEMPLATE.md").read_text(encoding="utf-8")
    router_template = (template_root / "ROUTER_TEMPLATE.md").read_text(encoding="utf-8")
    sub_skill_template = (template_root / "SUB_SKILL_TEMPLATE.md").read_text(encoding="utf-8")
    output_root = tmp_path / "skills"

    created = mod.create_skill(
        output_root,
        workflow_template,
        {
            "name": "sample-router",
            "type": "router",
            "description": "Route sample flows. Use when choosing between sample modes.",
            "title": "Sample Router",
        },
        router_template=router_template,
        sub_skill_template=sub_skill_template,
    )

    added = mod.add_sub_skill(
        created,
        sub_skill_template,
        {
            "name": "review",
            "description": "Review sample content. Use when checking a review route.",
            "intent": "Review a sample route",
            "summary": "Route the user into the review sub-skill.",
        },
    )

    assert added == created / "sub_skills" / "review"
    assert (added / "SKILL.md").exists()
    assert (added / "references" / "SKILL.ja.md").exists()
    router_skill = (created / "SKILL.md").read_text(encoding="utf-8")
    assert "`sub_skills/review/`" in router_skill
    assert "Review a sample route" in router_skill


def test_suite_with_router_type(tmp_path: Path):
    mod = load_module()
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(
        """
        {
          "skills": [
            {
              "name": "sample-router",
              "type": "router",
              "description": "Route sample flows. Use when choosing between sample modes.",
              "sub_skills": [
                {
                  "name": "draft",
                  "description": "Draft sample content. Use when starting a draft route."
                }
              ]
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    items = mod.load_suite(suite_path)

    assert items[0]["type"] == "router"
    assert items[0]["sub_skills"][0]["name"] == "draft"
