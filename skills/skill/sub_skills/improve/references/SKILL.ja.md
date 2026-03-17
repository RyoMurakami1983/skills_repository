---
name: improve
description: >
  既存スキルを evidence ベースで改善する。Use when:
  trigger 精度、説明の冗長さ、関連資料の同期ずれを直したいとき。
compatibility: "_foundation/CONVENTIONS.md, _eval/scripts/validate_skill.py"
---

# Improve a Skill

既存 skill の弱い説明や過剰な文言を整理し、一般化された guidance に磨き直すための sub-skill です。

## When to Use This Skill

Use this skill when:
- レビューや eval 結果を受けて改善したいとき
- metadata や trigger 文を見直したいとき
- 英日ドキュメントや references を同期したいとき

## Workflow

- 変更が構造変更か wording 修正かを分類する
- 根拠となるレビュー、transcript、eval を読む
- 個別最適でなく再利用可能な説明へ書き換える
- 関連資料を同期し、L2 まで再検証する
