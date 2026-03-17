---
name: new
description: >
  新しいスキルやスキル群を要件から作成する。Use when:
  新規スキルの草案化、既存業務の skill 化、router + sub_skill 構成の雛形生成を進めたいとき。
compatibility: "_foundation/TEMPLATE.md, _foundation/ROUTER_TEMPLATE.md, _foundation/SUB_SKILL_TEMPLATE.md, _eval/scripts/validate_skill.py"
---

# Create a New Skill

新しい skill を flat workflow / orchestrator / router のどれで表現すべきかを見極め、雛形作成から初期検証まで進める sub-skill です。

## When to Use This Skill

Use this skill when:
- 新しいワークフローを skill として草案化したいとき
- router と sub_skill に分けるべきか判断したいとき
- suite をまとめて作り、命名と整合性をそろえたいとき

## Workflow

- 意図・トリガー・成功条件を先に整理する
- 類似 skill や制約を調べて重複を避ける
- 必要なら `create_skill.py --type router` で router 構造を生成する
- L1 validation を早期に実行して構造崩れを止める

## Notes

- 単一路線なら flat workflow、top-level skill 委譲中心なら orchestrator、内部モード分岐が必要なら router を選びます。
