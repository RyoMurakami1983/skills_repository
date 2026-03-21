from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "validate_skill.py"
    spec = importlib.util.spec_from_file_location("unified_validate_skill", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_skill(
    tmp_path: Path,
    folder: str,
    content: str,
    *,
    with_references_dir: bool = True,
) -> Path:
    skill_dir = tmp_path / folder
    if with_references_dir:
        (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    else:
        skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return skill_dir / "SKILL.md"


def test_l1_passes_for_japanese_router_style_skill(tmp_path: Path):
    mod = load_module()
    skill_path = write_skill(
        tmp_path,
        "router-skill",
        """---
name: router-skill
description: >
  スキル運用を整理するルーター。Use when: 新しいスキルを
  作るとき、品質を確認するとき、既存 guidance を改善するとき。
compatibility: test
---

# スキルルーター

## こんなときに使う

- 新しいスキルの流れを整理したいとき
- 品質チェックの入口を決めたいとき
- 既存 guidance を evidence ベースで改善したいとき

## 判断表

| やりたいこと | ルート |
| --- | --- |
| 作成 | new |
| 改善 | improve |
""",
    )
    report = mod.validate(skill_path, "L1")
    assert report.critical_passed is True
    assert len(report.critical) == 5


def test_l1_passes_for_english_router_style_skill_without_translation_pair(tmp_path: Path):
    mod = load_module()
    skill_path = write_skill(
        tmp_path,
        "legacy-router-skill",
        """---
name: legacy-router-skill
description: >
  Route skill operations. Use when: creating skills, validating drafts, or
  improving published guidance.
---

# Router Skill

## When to Use This Skill

Use this skill when:
- Creating router logic for skill workflows
- Validating critical checks before rollout
- Improving bundled skill guidance with evidence

## Decision Table

| Intent | Route |
| --- | --- |
| Create | new |
| Improve | improve |
        """,
    )
    report = mod.validate(skill_path, "L1")
    assert report.critical_passed is True


def test_l2_can_pass_without_references_dir_when_skill_is_compact(tmp_path: Path):
    mod = load_module()
    skill_path = write_skill(
        tmp_path,
        "compact-skill",
        """---
name: compact-skill
description: >
  小さな skill を検証する。Use when: 最小構成で L2 を確認したいとき。
---

# Compact Skill

理由を短く説明する。

## こんなときに使う

- 最小構成の skill を確認したいとき
- references なしの評価を見たいとき
- 軽量な draft を素早く見直したいとき

## ワークフロー: Minimal

### ステップ 1 — 確認する
次の行動と理由を短く説明する。

## 注意点

- **詰め込みすぎない**: 本文が短いなら references なしでもよい。
""",
        with_references_dir=False,
    )
    report = mod.validate(skill_path, "L2")
    assert report.critical_passed is True
    assert all(check.passed for check in report.recommended if check.id in {"R5", "R6"})


def test_l1_fails_without_trigger_phrase(tmp_path: Path):
    mod = load_module()
    skill_path = write_skill(
        tmp_path,
        "bad-skill",
        """---
name: bad-skill
description: トリガー表現がない説明。
---

# Bad Skill

## こんなときに使う

- 文書を作りたいとき
- 文書を更新したいとき
- 文書を見直したいとき

## ワークフロー: Minimal

### ステップ 1 — 進める
なぜ必要かを書く。
""",
    )
    report = mod.validate(skill_path, "L1")
    assert report.critical_passed is False
    failed_ids = {check.id for check in report.critical if not check.passed}
    assert "C3" in failed_ids
