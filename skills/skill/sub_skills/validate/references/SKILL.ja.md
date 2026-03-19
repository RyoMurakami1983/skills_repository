---
name: validate
description: >
  スキルの構造品質と出荷可否を段階的に検証する。Use when:
  draft の最低基準確認、公開前レビュー、rollout 可否の判断をしたいとき。
compatibility: "_foundation/QUALITY.md, _eval/scripts/validate_skill.py"
---

# Validate a Skill

最小の構造検証から始めて、必要に応じて enterprise review や behavioral eval まで段階的に進める sub-skill です。

## When to Use This Skill

Use this skill when:
- 新規 skill が最低限の構造を満たすか確認したいとき
- 編集後の skill を公開前に見直したいとき
- 行動評価へ進むべきか判断したいとき

## Workflow

- まず L1 Critical checks を通す
- Recommended checks で readability / reuse を確認する
- rollout 対象なら L3 を検討する
- 振る舞い差分が焦点なら `evaluate` へ回す
