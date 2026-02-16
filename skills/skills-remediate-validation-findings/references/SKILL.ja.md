<!-- 
このドキュメントは skills-remediate-validation-findings の日本語版です。
英語版: ../SKILL.md
-->

---
name: skills-remediate-validation-findings
description: Fix validation failures systematically from a quality report. Use when a skill fails validation.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, remediation, quality]
  invocable: false
---

# 検証結果の修復

品質レポートの不合格項目を体系的に修正し、スキルを合格品質（全体≥80%、各カテゴリ≥80%）に引き上げるワークフロー。

## When to Use This Skill

このスキルを使用する場面：
- スキルが品質検証に不合格で、具体的な指摘を含むレポートがある時
- どの検証不合格を最初に修正すべきか優先順位を付ける時
- 退行を導入せずに構造化された修正を適用する時
- 80%の初回スコアから90%+の目標品質に向けて反復する時

---

## Core Principles

1. **重要度順に修正** — Critical不合格を最初に、次にError、次にWarning（基礎と型）
2. **一度に1つの修正** — 新しい問題の導入を避けるため原子的な変更を行う（継続は力）
3. **各修正後に再検証** — 修正が機能し退行がないことを確認（成長の複利）
4. **症状ではなく根本原因を修正** — 表面的な対応ではなく、根本的な問題を解決（ニュートラル）

---

## ワークフロー：指摘事項の修復

### ステップ1 — 品質レポートを読む

レポートを解析し、指摘事項を重要度別に分類。

**Why**: トリアージが最初。すべてを一度に修正しようとすると混乱します。基礎と型 — 優先順位という「型」があるから効率的に動ける。

### ステップ2 — Critical項目を修正

Critical項目はすべてをブロック。YAML frontmatter欠損、name不一致など。

### ステップ3 — Error項目を修正

品質に大きく影響する項目。一般的な修正:
- 複数Pattern → 単一Workflow（`## Pattern N:` → `## Workflow:` + Steps）
- Values統合不足（Core Principlesに≥2個のValues参照を追加）
- description に "Use when..." を追加

### ステップ4 — Warning項目を修正

全Errorが解決した後:
- ファイル長 > 500行 → 詳細を`references/`に移動
- 文長 → 長い文を分割

### ステップ5 — Bonus項目を追加

全カテゴリ80%+合格後:
- 日本語版 `references/SKILL.ja.md` を作成

### ステップ6 — 最終再検証

`skills-validate-skill`を最終実行して確認。

---

## Good Practices

### 1. 構造をコンテンツより先に修正

**What**: 構造不合格を常に最初に解決。
**Why**: 構造は基礎。壊れた構造の上でコンテンツを修正しても無駄。
**Values**: 基礎と型

### 2. 原子的な修正を行う

**What**: 1回の編集で1つの修正。
**Why**: 複合修正で退行が発生した場合、原因を特定できない。
**Values**: 継続は力

### 3. 英語版を修正の起点にし、日本語版は構造を同期

**What**: 修復作業は `SKILL.md` を起点に行い、同じ構造変更を `references/SKILL.ja.md` に同期する。
**Why**: 主レビュー対象を固定し、英日ドリフトを防げる。
**Values**: 基礎と型 / ニュートラル

---

## Quick Reference

### 修復優先順序

```
1. Critical項目  → 必須修正（公開をブロック）
2. Error項目     → 公開前に修正
3. Warning項目   → 90%+品質のために修正
4. Bonus項目     → あれば良い
5. 再検証        → 全修正を確認、退行なし
```

### よくある修正クイックリファレンス

| 指摘 | クイック修正 |
|------|-----------|
| "Use when..."なし | descriptionに追加: `. Use when <シナリオ>.` |
| 複数Pattern | `## Workflow:`にマージ、ステップに変換 |
| Values不足 | Core Principlesに括弧でValue名を追加 |
| ファイル長超過 | 詳細を`references/`に移動 |
| 日本語版なし | `references/SKILL.ja.md`を作成 |

---
