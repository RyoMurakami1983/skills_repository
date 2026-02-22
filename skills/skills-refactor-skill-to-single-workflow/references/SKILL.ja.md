<!-- 
このドキュメントは skills-refactor-skill-to-single-workflow の日本語版です。
英語版: ../SKILL.md
-->

---
name: skills-refactor-skill-to-single-workflow
description: >
  Convert a legacy multi-pattern skill into a single-workflow skill, or
  modernize a reference skill to production quality. Use when migrating
  existing skills during the repository-wide cosmos modernization effort.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, refactoring, migration, cosmos]
  invocable: false
---

# スキルを単一ワークフローにリファクタリングする

レガシーのSKILL.mdを「1スキル＝1パターン」原則に従った本番品質のスキルに変換するエンドツーエンドのワークフロー。マルチパターンの分割とリファレンスから本番への移行（コスモス化）の両方に対応。

## When to Use This Skill

このスキルを使用する場面：
- 既存のマルチパターンスキルを単一ワークフロー標準に変換する時
- リファレンススキル（フラットフロントマター、JA版なし、references/なし）を本番品質に移行する時
- リポジトリ全体のコスモス化（モダナイゼーション）作業でレガシースキルを移行する時
- どのパターンを統合し、どれを別スキルに分割するか判断する時
- 新しく分割されたワークフロースキルを指すルータースキルを作成する時

---

## Related Skills

- **`skills-author-skill`** — 新スキルをゼロから作成（分割後に使用）
- **`skills-validate-skill`** — リファクタリング結果の品質検証
- **`skills-revise-skill`** — リファクタリング後の命名・発見可能性の改善

---

## Core Principles

1. **1スキル＝1パターン** — スキルは1つの実行可能なパターン（ワークフロー/サイクル/ルーター/カスケード/パラレル/マルチMCP）を実装する。トピックダンプではない（基礎と型）
2. **まず統合** — 多数の小スキルに分割するより、関連パターンを1つのワークフローにまとめることを優先（ニュートラル）
3. **コンテキストを保持** — 各結果スキルは自己完結的でなければならない; 分割しすぎてコンテキストが失われることを避ける（成長の複利）
4. **互換性のためのルーター** — 参照切れを防ぐため、元のディレクトリをルータースキルとして維持（継続は力）
5. **構造的余白** — 将来の進化の余地を残す; 過度な仕様化や分割を避ける（余白の設計）

---

## ワークフロー：単一ワークフローへのリファクタリング

### ステップ0 — フロントマターのモダン化

フラットフロントマターをネストされた`metadata:`形式に変換する：

```yaml
# Before（レガシーフラット形式）
---
name: my-skill
description: Does something. Use when doing X.
invocable: false
---

# After（本番ネスト形式）
---
name: my-skill
description: >
  Does something specific. Use when doing X
  and needing to achieve Y.
metadata:
  author: RyoMurakami1983
  tags: [relevant, tags, here]
  invocable: false
---
```

**チェックリスト**：
- `description`に"Use when"トリガーフレーズを含む
- `metadata:`が`author`、`tags`、`invocable`をネストする
- トップレベルキーは`name`、`description`、`license`、`allowed-tools`、`metadata`、`compatibility`のみ

**Why**: フロントマターはスキル発動のトリガーです。descriptionフィールドがエージェントに「いつこのスキルを使うか」を伝えます。基礎と型 — 最小形式で最大可能性を生む設計の実践。

> **Values**: 基礎と型（最小形式で最大可能性を生む設計）

### ステップ1 — 既存スキルの監査

パターンを数え、それぞれを分類する：

**分類ルール**：
- **トピック/セクション**: 概念について教えている → 1つのスキルに**統合**
- **独立ワークフロー**: 単独で最初から最後まで実行できる → 新スキルに**分割**
- **バリアント**: 異なる入力での同じワークフロー → 1つのスキル内のオプションとして保持

**Why**: この分類が最も重要なステップです。「独立して実行可能かどうか」が判断基準。これが基礎と型 — 最小形式で最大可能性を生む設計思想の実践です。

> **Values**: 基礎と型（独立実行可能かどうかの判断基準が型）

### ステップ2 — ワークフローにグループ化

**分割の判断基準**：
- ✅ 分割する: ワークフローが独自のトリガー（"Use when..."）を持ち、独立実行可能
- ❌ 分割しない: パターンが大きなワークフローのコンテキスト内でのみ意味がある

**Why**: 過度な分割はコンテキストの喪失を招きます。ニュートラルな視点 — 誰もが使える普遍性を保つために、自己完結性を重視します。

> **Values**: ニュートラル（誰もが使える普遍性を保つ）

### ステップ3 — 新スキルを作成

`skills-author-skill`に従い、各ワークフローの新スキルディレクトリを作成。

> **Values**: 成長の複利（教えることが自律成長を生む）

### ステップ4 — 元スキルをルーターに変換

元のSKILL.mdを単一ワークフローのルータースキルとして書き換え。

**Why**: 継続は力 — 既存の参照を壊さないことで、段階的な移行を可能にします。

> **Values**: 継続は力（既存参照を壊さない段階的移行）

### ステップ5 — オーバーフローコンテンツの移動

元スキルの参照資料を適切な新スキルに移動。

> **Values**: 余白の設計（コンテンツを適切な場所へ再配置）

### ステップ6 — クロスリファレンスの更新

リポジトリ全体で旧スキル名への参照を検索・更新。

> **Values**: 温故知新（過去の参照を新しい構造に繋ぐ）

### ステップ7 — 全結果を検証

各新スキルとルーターに対して`skills-validate-skill`を実行。

> **Values**: 基礎と型（品質基準による検証）

---

## Good Practices

### 1. 分割前にまず統合

**What**: すべてのパターンを1つのワークフローにまとめることから始め、結果が500行を超えるか本当に独立したワークフローを含む場合のみ分割。

**Why**: 過度な分割はコンテキスト喪失とメンテナンス負担の増加を招く。

**Values**: 基礎と型（最小形式で最大可能性）

### 2. ルータースキルは最小限に

**What**: ルーターSKILL.mdは100行未満 — フロントマター、"When to Use"、デシジョンテーブルのみ。

**Why**: ルーターは後方互換性のために存在し、コンテンツリポジトリではない。

**Values**: 継続は力

### 3. 著者とValuesを保持

**What**: すべての新スキルに`author: RyoMurakami1983`と憲法Values統合を保持。

**Values**: 成長の複利

---

## Common Pitfalls

### 1. すべてのパターンを個別スキルに分割

**Problem**: 8つのパターンから8つのマイクロスキルを作成し、各々が単独では小さすぎて役に立たない。

**Solution**: パターンが独自の"When to Use"を持つ独立実行可能なワークフローの場合のみ分割。

### 2. 分割でコンテキストを失う

**Problem**: 分割後、各新スキルが他のスキルで説明された概念を参照している。

**Solution**: 各スキルは自己完結的であるべき。広範なクロスリファレンスよりも必要なコンテキストを複製。

### 3. ルーターを忘れる

**Problem**: 元のディレクトリを削除し、すべての既存参照を壊す。

**Solution**: 常に元をルータースキルに変換; 移行中は削除しない。

---

## Anti-Patterns

### セクションレベルの分割

**What**: "When to Use"をスキルに、"Core Principles"を別のスキルにするなど。

**Why It's Wrong**: これらはスキルのセクションであり、独立したワークフローではない。分割は各部分の理解に必要なコンテキストを破壊する。

**Better Approach**: すべての標準セクションを各ワークフロースキル内に保持する。

### Big-Bang移行

**What**: すべてのスキルを一度に1つのPRで移行しようとする。

**Why It's Wrong**: リスクが高く、レビューが困難で、参照が壊れる可能性が高い。

**Better Approach**: 一度に1つのスキルファミリーを移行し、検証してから次へ進む。

---

## Quick Reference

### コスモス化チェックリスト（1スキルあたり）

- [ ] フロントマター: ネスト`metadata:`形式、`author`、descriptionに"Use when"
- [ ] 構造: H1 → When to Use → Related Skills → Core Principles → Workflow → Good Practices → Common Pitfalls → Anti-Patterns → Quick Reference
- [ ] 行数: SKILL.md ≤ 500行; 超過分は`references/`へ
- [ ] Values: 2つ以上のValues引用（関連する場合は余白の設計を含む）
- [ ] バイリンガル: `references/SKILL.ja.md`（英語H2見出し + 日本語コンテンツ）
- [ ] バリデーション: `skills-validate-skill` PASS

### リファクタリング判断ツリー

```
リファレンススキル（local_reference_skills/）か？
├─ YES → まずステップ0（フロントマター）を実行、その後監査
└─ NO  → ステップ1から開始

レガシースキルの各パターンについて：
│
├─ 独立して実行可能なワークフローか？
│  ├─ YES → 独自の"When to Use"があるか？
│  │  ├─ YES → 新スキルに分割
│  │  └─ NO  → 親ワークフローに統合
│  └─ NO  → 親ワークフローに統合
│
統合後：
├─ 結果 ≤ 500行？ → 完了
└─ 結果 > 500行？ → 詳細をreferences/へ移動
```

### リファクタリングチェックリスト

- [ ] 監査: パターンを数え、各々を分類
- [ ] グループ化: パターンをエンドツーエンドワークフローにマッピング
- [ ] 作成: `skills-author-skill`に従い新スキルを作成
- [ ] ルーター: 元をルータースキルに変換
- [ ] 移動: references/assetsを新スキルディレクトリに再配置
- [ ] 更新: リポジトリ全体のクロスリファレンスを修正
- [ ] 検証: 全結果に`skills-validate-skill`を実行

---

## Resources

- [skills-author-skill](../skills-author-skill/SKILL.md) — 新スキルの作成方法
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — 品質検証
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — 開発憲法

---
