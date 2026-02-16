<!-- 
このドキュメントは skills-generate-skill-template の日本語版です。
英語版: ../SKILL.md
-->

---
name: skills-generate-skill-template
description: Generate a single-workflow skill skeleton with bilingual support. Use when starting a new skill.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, generator, scaffolding]
  invocable: false
---

# スキルテンプレートを生成する

単一ワークフロースキルのスケルトン（SKILL.md + references/SKILL.ja.md + ディレクトリ構造）を生成し、基本的な構造検証に最初からパスするワークフロー。

## When to Use This Skill

このスキルを使用する場面：
- 新しいスキルを開始し、すぐに埋められるスケルトンが欲しい時
- 必要なファイルを含む正しいディレクトリ構造を生成する時
- バイリンガルスキルの雛形（英語+日本語）を作成する時
- 「1スキル＝1ワークフロー」標準に従ったスケルトンを確保する時

---

## Core Principles

1. **基礎と型** — テンプレートに標準構造を埋め込み、著者が正しい基礎から始められるように
2. **成長の複利** — スケルトンがコンテンツの段階的な追加を容易にする; スケルトンが完全なスキルに成長
3. **継続は力** — バイリンガル生成（EN + JA）がデフォルト。初日から習慣に
4. **ニュートラル** — テンプレートは明確なプレースホルダーと案内を使用し、どのドメインにも適用可能

---

## ワークフロー：スキルテンプレートを生成する

### ステップ1 — メタデータ定義

必要な情報を収集：名前（`<context>-<workflow>`形式）、説明（≤100文字、"Use when..."含む）、タグ（3〜5個）。

**Why**: メタデータはスキルの「型」。最初に正しく定義することで、後の修正コストを大幅に削減します。

### ステップ2 — 生成方法を選択

| 方法 | いつ使うか | 速度 |
|------|----------|------|
| 手動コピー | 構造を学ぶ時 | 遅いが教育的 |
| スクリプト | バッチ生成 | 速く一貫性あり |
| AI支援 | クイックプロトタイプ | 最速 |

### ステップ3 — テンプレート構造

生成されるスケルトンのディレクトリ構造:
```
<skill-name>/
├── SKILL.md                    # 英語（プライマリ）
└── references/
    └── SKILL.ja.md             # 日本語版
```

テンプレートには以下が含まれる:
- 完全なYAMLフロントマター（name, description, author, tags, invocable）
- 全必須セクション（When to Use, Core Principles, Workflow, Good Practices, etc.）
- プレースホルダーテキスト（`<placeholder>`形式）

### ステップ4 — 日本語版を生成

`references/SKILL.ja.md`を同じ構造で作成。日本語版の特徴:
- "When to Use"項目をコンテキスト付きで翻訳
- Core Principlesに日本語のValue名を自然に含む
- ワークフローステップに哲学的根拠の"**Why**:"セクションを含む

### ステップ5 — プレースホルダーを埋める

`<placeholder>`テキストをすべて実際のコンテンツに置換。

### ステップ6 — 結果を検証

`skills-validate-skill`を実行して合格を確認。

---

## Good Practices

### 1. 最初からバイリンガルで生成

**What**: 常にSKILL.mdとreferences/SKILL.ja.mdを同時に作成。
**Why**: 後から日本語を追加するのは、両方のテンプレートを同時に埋めるよりずっと難しい。
**Values**: 継続は力

### 2. 生成後すぐに埋める

**What**: 生成されたスケルトンを1つの作業セッション以上放置しない。
**Why**: スキルの目的に関するコンテキストが薄れ、プレースホルダーが永続化する。
**Values**: 継続は力（「いつかやる」ではなく「今日やる」）

---

## Common Pitfalls

### 1. プレースホルダーを残す

**Problem**: `<placeholder>`テキストが残ったままコミット。
**Solution**: コミット前にファイル内の`<`を検索し、すべて置換。

### 2. 命名規約の間違い

**Problem**: `skill-my-thing`を使用（正しくは`<context>-<workflow>`）。
**Solution**: 生成前に`skills-optimize-skill-discoverability`の命名ルールを確認。

---

## Quick Reference

### 生成ワークフロー

```
1. メタデータ定義（名前、説明、タグ）
2. スケルトン生成（手動/スクリプト/AI）
3. 空スケルトンを検証（構造チェック）
4. プレースホルダーを埋める
5. 日本語版を作成
6. 埋めたスキルを検証
7. コミット
```

---

## Resources

- [skills-author-skill](../skills-author-skill/SKILL.md) — テンプレートの埋め方
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — 検証
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — 開発憲法とValues
- 生成スクリプト: `../skill-template-generator/scripts/generate_template.py`
- テンプレートアセット: `../skill-template-generator/assets/`

---
