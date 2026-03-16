---
name: skill
description: >
  スキルの作成・改善・検証・評価を 1 つの入口で案内する。Use when:
  新しいスキルを作りたいとき、既存スキルを改善したいとき、品質を確認したいとき、
  効果を測定したいとき。明示的に「スキル」と言っていない場合も含む。
compatibility: GitHub Copilot Agent, Claude Code, Codex
---

# Skill Router

スキルそのものを作る・直す・確かめる・測る話題を、1 本の入口から適切な sub-skill へ案内します。

## When to Use This Skill

Use this skill when:
- 新しいスキルをアイデアや仕様から作り始めるとき
- 既存スキルをレビュー結果や利用時の違和感に基づいて改善するとき
- スキルの構造や説明品質を出荷前に確認するとき
- スキルが本当に挙動を改善するか比較評価したいとき
- 関連する複数スキルをまとめて設計したいとき
- 旧メタスキル群を統合構造へ置き換えたいとき

## Decision Table

| 意図 | ルート | 何をするか |
| --- | --- | --- |
| 新しいスキルを作る | `sub_skills/new/` | 意図整理、調査、雛形作成、初期検証まで進める。 |
| 既存スキルを改善する | `sub_skills/improve/` | 変更の種類を見極め、不要な記述を削り、説明とメタデータを磨く。 |
| 品質を確認する | `sub_skills/validate/` | L1-L4 の順で検証し、どこが出荷の妨げかを明確にする。 |
| 効果を測定する | `sub_skills/evaluate/` | テスト設計、with-skill / baseline 比較、集計、次アクション判定を行う。 |
| スキル群をまとめて作る | `sub_skills/new/` | バッチモードで命名と相互参照を揃える。 |

## Shared Resources

- `_foundation/TEMPLATE.md`：最小テンプレート
- `_foundation/QUALITY.md`：品質基準
- `_foundation/CONVENTIONS.md`：命名・frontmatter・書き方
- `_eval/`：行動評価と validator
- `scripts/`：生成、索引更新、配布パッケージ化

## Routing Notes

- ユーザーの現在地点から最短で役立つ sub-skill に飛び込む。
- 用語は相手に合わせて説明し、専門語を押し付けない。
- 実行ロジックは router に書かず、sub-skill や script に委譲する。
