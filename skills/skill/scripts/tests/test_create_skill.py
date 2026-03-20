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
            "description": "サンプルを作成する。こんなときに使う: template 生成を試したいとき。",
            "title": "サンプルスキル",
            "compatibility": "pytest",
        },
    )

    assert created == output_root / "sample-skill"
    assert (created / "SKILL.md").exists()
    assert not (created / "references" / "SKILL.ja.md").exists()
    assert (created / "scripts").is_dir()
    assert (created / "assets").is_dir()
    skill_md = (created / "SKILL.md").read_text(encoding="utf-8")
    assert "<What this skill does>" not in skill_md
    assert "<scenario 1>" not in skill_md
    assert "サンプルを作成する。こんなときに使う: template 生成を試したいとき。" in skill_md
    assert "## こんなときに使う" in skill_md
    assert "## ワークフロー:" in skill_md
    assert 'compatibility: "pytest"' in skill_md


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
            "description": "サンプルの流れを振り分ける。こんなときに使う: mode を選び分けたいとき。",
            "title": "サンプルルーター",
        },
        router_template=router_template,
        sub_skill_template=sub_skill_template,
    )

    assert created == output_root / "sample-router"
    assert (created / "SKILL.md").exists()
    assert not (created / "references" / "SKILL.ja.md").exists()
    assert (created / "scripts").is_dir()
    assert (created / "assets").is_dir()
    assert (created / "_foundation").is_dir()
    assert (created / "sub_skills").is_dir()
    skill_md = (created / "SKILL.md").read_text(encoding="utf-8")
    assert "<What this router does>" not in skill_md
    assert "<scenario 1>" not in skill_md
    assert "サンプルの流れを振り分ける。こんなときに使う: mode を選び分けたいとき。" in skill_md
    assert "## 判断表" in skill_md


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
            "description": "サンプルの流れを振り分ける。こんなときに使う: mode を選び分けたいとき。",
            "title": "サンプルルーター",
            "sub_skills": [
                {
                    "name": "draft",
                    "description": "サンプル下書きを作る。こんなときに使う: draft ルートを始めたいとき。",
                    "intent": "下書きルートへ進める",
                    "summary": "ユーザーを draft sub-skill へ案内する。",
                },
                {
                    "name": "review",
                    "description": "サンプル内容を見直す。こんなときに使う: review ルートを確認したいとき。",
                },
            ],
        },
        router_template=router_template,
        sub_skill_template=sub_skill_template,
    )

    assert (created / "sub_skills" / "draft" / "SKILL.md").exists()
    assert not (created / "sub_skills" / "draft" / "references" / "SKILL.ja.md").exists()
    assert (created / "sub_skills" / "review" / "SKILL.md").exists()
    assert not (created / "sub_skills" / "review" / "references" / "SKILL.ja.md").exists()
    router_skill = (created / "SKILL.md").read_text(encoding="utf-8")
    assert "`sub_skills/draft/`" in router_skill
    assert "`sub_skills/review/`" in router_skill
    assert "下書きルートへ進める" in router_skill
    draft_skill = (created / "sub_skills" / "draft" / "SKILL.md").read_text(encoding="utf-8")
    assert "<What this sub-skill does>" not in draft_skill
    assert "<scenario 1>" not in draft_skill
    assert "サンプル下書きを作る。こんなときに使う: draft ルートを始めたいとき。" in draft_skill
    assert 'compatibility: "_foundation/"' in draft_skill
    assert "## こんなときに使う" in draft_skill


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
            "description": "サンプルの流れを振り分ける。こんなときに使う: mode を選び分けたいとき。",
            "title": "サンプルルーター",
        },
        router_template=router_template,
        sub_skill_template=sub_skill_template,
    )

    added = mod.add_sub_skill(
        created,
        sub_skill_template,
        {
            "name": "review",
            "description": "サンプル内容を見直す。こんなときに使う: review ルートを確認したいとき。",
            "intent": "見直しルートへ進める",
            "summary": "ユーザーを review sub-skill へ案内する。",
        },
    )

    assert added == created / "sub_skills" / "review"
    assert (added / "SKILL.md").exists()
    assert not (added / "references" / "SKILL.ja.md").exists()
    router_skill = (created / "SKILL.md").read_text(encoding="utf-8")
    assert "`sub_skills/review/`" in router_skill
    assert "見直しルートへ進める" in router_skill


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
              "description": "サンプルの流れを振り分ける。こんなときに使う: mode を選び分けたいとき。",
              "sub_skills": [
                {
                  "name": "draft",
                  "description": "サンプル下書きを作る。こんなときに使う: draft ルートを始めたいとき。"
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


def test_build_frontmatter_uses_folded_description_for_yaml_sensitive_text():
    mod = load_module()

    frontmatter = mod.build_frontmatter(
        "sample-skill",
        '作成: sample #1。こんなときに使う: "quoted" text を含む説明が必要なとき。',
        'tool:>=1.0',
    )

    assert "description: >" in frontmatter
    assert '作成: sample #1。こんなときに使う: "quoted" text を含む説明が必要なとき。' in frontmatter
    assert 'compatibility: "tool:>=1.0"' in frontmatter
