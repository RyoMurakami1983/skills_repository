<!-- 
このドキュメントは skills-optimize-skill-discoverability の日本語版です。
英語版: ../SKILL.md
-->

---
name: skills-optimize-skill-discoverability
description: Improve skill name, description, and tags for better agent activation. Use when skills are not being found.
author: RyoMurakami1983
tags: [copilot, agent-skills, discoverability, naming]
invocable: false
---

# スキルの発見性を最適化する

AIエージェント（Copilot、Claude、Codex）がスキルを確実に見つけて活性化できるよう、スキルのname、description、tags、"When to Use"セクションを改善するワークフロー。

## When to Use This Skill

このスキルを使用する場面：
- 既存のスキルが関連性があるのにエージェントに活性化されない時
- 新しいスキルの名前を選び、最大の発見性を求める時
- description長、タグカバレッジ、活性化キーワードをレビューする時
- スキルファミリー全体の命名を標準化する時
- リポジトリ全体の命名一貫性とギャップを監査する時

---

## Core Principles

1. **名前＝意図** — スキル名はどのワークフローを実行するかを即座に伝えるべき（基礎と型）
2. **説明＝活性化** — descriptionはエージェントがマッチングに使う主要シグナル; "Use when..."を含む（ニュートラル）
3. **タグ＝発見面** — タグはnameとdescriptionを超えて検索面を拡張する（成長の複利）
4. **一貫性＝信頼** — スキルファミリー全体の一貫した命名が予測可能性を構築（継続は力）

---

## ワークフロー：発見性の最適化

### ステップ1 — 現在のメタデータ監査

フロントマターを抽出してルールと照合する。

### ステップ2 — 命名規約の適用

`<コンテキスト>-<ワークフロー>`形式に変換する。

**Why**: 命名規約は「型」です。一貫した型があるから、エージェントも人間も迷わず速く見つけられる。これが基礎と型の追求の実践です。

**コンテキスト例**：
- `skills` — スキルシステムのワークフロー
- `git` — ローカルGit操作
- `github` — GitHub操作
- `dotnet` / `python` — 技術実装

**ワークフロー命名ルール**：
- 動詞で始める: `author-`, `validate-`, `generate-`, `review-`
- 汎用動詞を単独で使わない: `do`, `fix` → 目的語と組み合わせ: `validate-structure`

### ステップ3 — description最適化

活性化コンテキストを含むよう書き直す。

**公式**: `<何をするか>. Use when <具体的トリガー>.`

### ステップ4 — タグ最適化

タグはnameを補完し（重複しない）、技術焦点を持つ。

### ステップ5 — "When to Use"セクション最適化

活性化に適した言語でシナリオを記述。

### ステップ6 — 活性化テスト

エージェントがスキルを見つけられるかテストし、必要に応じてキーワードを調整。

---

## Quick Reference

### 命名クイックリファレンス

| コンテキスト | ワークフロー例 |
|------------|-------------|
| `skills` | `author-skill`, `validate-skill`, `generate-skill-template` |
| `git` | `protect-main`, `commit-practices`, `setup-hooks` |
| `github` | `review-pr`, `create-pr`, `manage-issues` |
| `dotnet` | `apply-mvvm`, `configure-di`, `setup-testing` |

### 発見性チェックリスト

- [ ] 名前が`<context>-<workflow>`に従う（動詞先導、kebab-case、≤64文字）
- [ ] description ≤ 100文字、"Use when..."句を含む
- [ ] 3〜5個の技術焦点タグ（name語との重複なし）
- [ ] "When to Use"に5〜8個の具体的、動詞先導シナリオ

---

## Changelog

### Version 1.0.0 (2026-02-13)
- 初版リリース：発見性最適化ワークフロー
- 命名規約リファレンス（`<context>-<workflow>`）
