---
name: evaluate
description: >
  with-skill と baseline を比較し、skill の行動変化を測定する。Use when:
  trigger 精度、出力品質、回帰リスクを実証的に確認したいとき。
compatibility: "_eval/agents/, _eval/scripts/, _eval/schemas/"
---

# Evaluate a Skill

静的レビューだけでは足りないときに、skill が本当に挙動改善を生むかを比較評価する sub-skill です。

## When to Use This Skill

Use this skill when:
- should-trigger / near-miss ケースを設計したいとき
- with-skill と baseline の差分を比較したいとき
- benchmark と reviewer 向け artifact を生成したいとき

## Workflow

- 実際の依頼に近い eval ケースを作る
- with-skill / baseline を同条件で実行する
- 集計して差分を読む
- 採用、改訂、ケース追加の次アクションを決める
