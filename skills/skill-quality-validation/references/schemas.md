# Validation Schema Contract（バリデーション・スキーマ契約）

> **Values**: 基礎と型の追求 / 温故知新 / ニュートラルな視点

このドキュメントは `validate_skill.py` と SKILL.md 作成者の間の「契約」を定義する。
何が必須で、何が警告で、何が自由かを明文化する。

---

## SKILL.md フロントマター契約

### 必須フィールド（check 1.1〜1.4）

```yaml
---
name: "skill-name"        # 必須: kebab-case、スキルディレクトリ名と一致
description: "..."        # 必須: ≤1024文字、"use when" トリガーフレーズ含む（W7.1警告: 80文字未満は品質警告）
---
```

### 非推奨フィールド（top-level）

```yaml
# ⚠️ これらはトップレベルに置かない（validate_skill.py では fail にならないが非推奨）
version: "1.0.0"          # → git tag / CHANGELOG で管理
author: "name"            # → git blame で管理
tags: [...]               # → 現在どのシステムでも使用されていない
invocable: false          # → 未使用
tool_versions:            # → references/environment-notes.md で管理
  git: ">=2.30"
last_reviewed: "..."      # → git log で確認可能
```

> **背景（温故知新）**: metadata: ブロックは Tier 1 アップデート（2026-02）で廃止。
> 帰属・バージョン管理は git の責任領域。フロントマターは「発見」のためだけに使う。
> これらのフィールドが存在しても `validate_skill.py` は fail にしない（check 1.2b/1.2c は廃止済み）。

### description フォーマット推奨（W7 警告対象）

```yaml
# ✅ 推奨パターン: [What]+[When]+[Capabilities]
description: >
  {action_verb} {what} for {context}.
  Use when {trigger_1}, {trigger_2}, or {trigger_3}.
  Handles {capability_1}, {capability_2}, and {capability_3}.

# 例
description: >
  Validate SKILL.md quality against 58-check rubric covering structure, content,
  code quality, and language. Use when reviewing a new skill, before PR creation,
  or auditing existing skills. Handles frontmatter checks, bilingual parity,
  Values integration, and progressive disclosure scoring.
```

**W7 警告トリガー条件**:
| 警告 | 条件 | 改善方法 |
|------|------|---------|
| W7.1 | description < 80文字 | 目的・トリガー・主要機能を追加 |
| W7.2 | action verb なし | 冒頭に動詞（create/validate/run等）を追加 |
| W7.3 | comma-clause < 2 | カンマ区切りのユースケースを列挙 |

---

## SKILL.md 構造契約

### 必須セクション（check 1.5〜1.13）

| セクション | 要件 | チェックID |
|-----------|------|-----------|
| `## When to Use This Skill` | 最初のH2であること | 1.5 |
| `## Core Principles / The Philosophy` | 番号付きリスト形式 | 1.6 |
| `## Best Practices` | セクション存在 | 1.7 |
| `## Common Pitfalls` | セクション存在 | 1.8 |
| `## Anti-Patterns` | セクション存在 | 1.9 |
| `## Quick Reference / Decision Tree` | セクション存在 | 1.10 |
| `references/SKILL.ja.md` | 対応する日本語版（構造・内容パリティ） | 1.11〜1.13 |

### Core Principles フォーマット

```markdown
## Core Principles

1. **Principle Name** (Values名) — 説明
2. **Principle Name** (Values名) — 説明
```

**注意**: テーブル形式は不可。番号付きリスト形式のみ。

### Workflow セクション（ワークフロースキルのみ）

```markdown
## Workflow: {skill name}   ← コロン必須（is_workflow 検出に使用）

### Step 1: {Title}

...

> **Values**: {Value名} / {Value名}  ← 各Stepに必須（W2系）
```

---

## コード品質契約

### 必須（check 3.x）

| 要件 | チェックID |
|------|-----------|
| コードブロックに言語指定（```bash, ```python 等） | 3.1 |
| Bash コマンドは実行可能（`&&` チェーンOK） | 3.3 |
| PowerShell コマンドは実行可能 | 3.4 |
| ハードコードされた絶対パス禁止（環境依存回避） | 3.8 |
| シークレット・トークン・パスワードのプレースホルダーは `<PLACEHOLDER>` 形式 | 3.9 |

### 推奨（W系 警告）

```bash
# ✅ PowerShell + Bash の両方を提供（W3.1 対策）
git commit -m "message"   # 共通

# PowerShell 専用の場合
$result = gh pr list --json state | ConvertFrom-Json
```

---

## Language 品質契約

### 4.1〜4.4 の基準（設計意図・未実装）

> **NOTE**: 現在の `validate_skill.py` の `LanguageValidator` は 4.1.1〜4.3.3（受動態比率 / 長文 / 命令形 / 曖昧語 / 定義 / 頭字語 / 見出し数 / 表の可読性 / 強調）のみを実装しており、以下のチェックは**設計意図（未実装）**である。将来の実装時の目標値として扱い、現時点の pass/fail 判定には影響しない。

| チェック | 閾値 | 測定方法 | 実装状況 |
|---------|------|---------|----------|
| 能動態比率 | passive < 20% | passive 表現のカウント | 未実装（設計意図） |
| "should" 乱用回避 | < 5回 | 文書内出現回数 | 未実装（設計意図） |
| Headers に be 動詞禁止 | 0件 | 見出し内の be 動詞チェック | 未実装（設計意図） |
| ファイルサイズ | ≤ 500行 | 行数カウント（現状は check 1.13 で管理） | 未実装（設計意図） |

---

## 警告一覧（pass/fail に影響しない）

| 警告ID | 意味 | 修正方法 |
|--------|------|---------|
| W1.1-1.4 | EN/JA 構造不一致 | JA版の構造をEN版に合わせる |
| W2.x | Workflow Step に Values blockquote なし | 各Stepに `> **Values**: ...` を追加 |
| W3.1 | JA版に安全リスク用語（`sudo`, `rm -rf` 等） | EN版と意味が一致しているか確認 |
| W3.2 | JA版に否定パターン | 意味の逆転がないか確認 |
| W4 | Glossary 日付が古い | `.github/copilot-instructions.md` の更新日を確認 |
| W5 | EN SKILL.md に日本語テキスト | JA版に移動、または意図的なら維持 |
| W7.1 | description < 80文字 | description を充実させる |
| W7.2 | [What] 動詞なし | action verb を冒頭に追加 |
| W7.3 | capability 列挙 < 2 | ユースケースをカンマ区切りで列挙 |

---

## スコアリング契約

```
総合スコア ≥ 85% AND 全カテゴリ ≥ 80% → PASS
```

| カテゴリ | 最大スコア | 80%ライン |
|---------|----------|---------|
| Structure | 13 | 10.4 (11以上) |
| Content | 20 | 16以上 |
| Code Quality | 15 | 12以上 |
| Language | 10 | 8以上 |
| **総合** | **58** | **49.3 (50以上で85%)** |

> **注意**: スコアはルーター/ワークフロータイプによって動的に変わる場合がある。
> `is_router: true` のスキルは一部チェックをスキップする。
> `## Workflow:` 見出し（コロン必須）がある場合 `is_workflow=True` として扱う。

---

## バリデーション実行契約

```bash
# 標準実行
uv run python skills/skill-quality-validation/scripts/validate_skill.py <SKILL.md path>

# JSON出力（CI/プログラム連携用）
uv run python skills/skill-quality-validation/scripts/validate_skill.py <path> --json

# ギャップ分析（全スキル一括）
uv run python skills/skill-quality-validation/scripts/analyze_skill_gaps.py
```

**前提条件**: 検証したい SKILL.md へのパスを正しく指定すること（カレントディレクトリには依存しない）。
`validate_skill.py` は与えられた SKILL.md の場所から上方向に `.github/copilot-instructions.md` を探索し、その位置をリポジトリルートとして扱う。
