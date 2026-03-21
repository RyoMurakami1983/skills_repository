---
name: skill
description: >
  スキルの作成・改善・検証・評価を 1 つの入口にまとめる。Use when:
  新しいスキルを作りたいとき、公開済みスキルを改善したいとき、品質や効果を確認したいとき、関連スキル群をまとめて設計したいとき。
compatibility: GitHub Copilot Agent, Claude Code, Codex
---

# スキルルーター

スキルそのものを作る・直す・確かめる・測る話題を、1 本の入口から適切な sub-skill へ案内します。単一入口にする理由は、会話の途中で「作成 → 検証 → 改善」のように論点が切り替わっても、同じ文脈のまま扱えるようにするためです。

## こんなときに使う

- 新しいスキルをアイデアや仕様から作り始めたいとき
- 既存スキルをレビュー結果や利用時の違和感に基づいて改善したいとき
- スキルの構造や説明品質を広く使う前に確認したいとき
- スキルが本当に挙動を改善するか比較評価したいとき
- 関連する複数スキルをまとめて設計したいとき

## 判断表

| やりたいこと | ルート | 次にやること |
| --- | --- | --- |
| 新しいスキルを作る | `sub_skills/new/` | 意図整理、制約調査、雛形作成、初期検証まで進める。 |
| 既存スキルを改善する | `sub_skills/improve/` | 変更の種類を見極め、弱い guidance を削り、説明と metadata を磨く。 |
| 品質を確認する | `sub_skills/validate/` | L1-L4 の順で検証し、どこが出荷の妨げかを明確にする。 |
| 効果を測定する | `sub_skills/evaluate/` | ケース設計、baseline / legacy / current 比較、集計、次アクション判定を行う。 |
| スキル群をまとめて作る | `sub_skills/new/` | バッチモードで命名と相互参照をそろえる。 |

## 共通リソース

- `_foundation/TEMPLATE.md` — 最小の hot path を保つ workflow template
- `_foundation/ROUTER_TEMPLATE.md` — 親 router 用 template
- `_foundation/SUB_SKILL_TEMPLATE.md` — nested sub-skill 用 template
- `_foundation/QUALITY.md` — Critical / Recommended checks の基準
- `_foundation/CONVENTIONS.md` — naming、frontmatter、書き方の約束
- `_eval/` — behavioral evaluation assets と validation scripts
- `scripts/` — generator、packaging、index maintenance の再利用コード

## ルーティングメモ

- ユーザーの現在地点から最短で役立つ sub-skill に飛び込む。
- 用語は相手の literacy に合わせ、必要なら専門語を説明する。
- この repo では Python helper script を bare `python` ではなく `uv run python ...` で実行する。
- 実行ロジックは router に書かず、sub-skill や script に委譲する。

## 注意点

- **router に実行詳細を書き込みすぎない**: 親が重くなると route 判断より説明の重複が増え、sub-skill の役割がぼやける。
- **route 粒度を細かくしすぎない**: 似た route を増やすと判断表がノイズになり、かえって到達性が落ちる。
