<!-- 
このドキュメントは skills-author-skill の日本語版です。
英語版: ../SKILL.md
-->

---
name: skills-author-skill
description: >
  Write a new SKILL.md from scratch following Agent Skills best practices.
  Use when creating a new skill and deciding the right pattern (workflow,
  cycle, situational/router, cascade, parallel, or multi-MCP), defining
  trigger-focused frontmatter, and structuring bilingual documentation.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, authoring, documentation]
  invocable: false
---

# 新しいエージェントスキルを作成する

「1スキル＝1パターン」原則に従い、品質検証に合格し、開発憲法（PHILOSOPHY.md）と統合された高品質なSKILL.mdを一から書くためのワークフロー。

## When to Use This Skill

このスキルを使用する場面：
- GitHub Copilot / Claude / Codex エージェント用の新しいSKILL.mdを作成する時
- 単一ワークフロースキルに必要な構造とセクションを学ぶ時
- 明確な「When to Use」シナリオとCore Principlesを書く時
- 500行制限とreferences/オーバーフロー戦略への準拠を確保する時
- 開発Values（基礎と型、成長の複利など）をスキルに統合する時
- バイリンガル対応（英語SKILL.md + 日本語references/SKILL.ja.md）を設定する時

---

## Related Skills

- **`skills-validate-skill`** — 完成したスキルを品質基準で検証
- **`skills-refactor-skill-to-single-workflow`** — レガシーのマルチパターンスキルを変換
- **`skills-revise-skill`** — 公開後の改訂と発見性最適化

---

## Core Principles

1. **1スキル＝1パターン** — スキルはトピック集ではなく、1つの実行可能パターン（workflow/cycle/router等）を文書化する（基礎と型）
2. **簡潔さを最優先** — コンテキストは公共財。SKILL.mdは要点に絞り、詳細は`references/`へ（余白の設計）
3. **読者ファーストの設計** — 読者が5秒以内に関連性を判断できるようにする（ニュートラル）
4. **自由度を設計する** — 壊れやすい作業は厳密に、文脈依存作業は柔軟に設計する（基礎と型）
5. **Values統合** — すべてのスキルはPHILOSOPHY.mdのValuesと接続し、必要に応じて`余白の設計`も明示する（成長の複利）

---

## ワークフロー：新しいスキルを作成する

### ステップ1 — メタデータ定義（YAMLフロントマター）

`<コンテキスト>-<ワークフロー>`規約に従い名前を選択（kebab-case、動詞先導、≤64文字）。

```yaml
---
name: <context>-<verb>-<object>
description: <何をするか>. Use when <活性化シナリオ>. # ≤ 1024文字
metadata:
  author: RyoMurakami1983
  tags: [tag1, tag2, tag3]   # 3-5個の技術タグ
  invocable: false
---
```

**命名の考え方**：

| コンテキスト | ワークフロー | 完全名 | なぜこの名前か |
|------------|-----------|--------|-------------|
| `git` | `protect-main` | `git-protect-main` | mainブランチ保護という1つの作業 |
| `github` | `review-pr` | `github-review-pr` | PRレビューという1つのワークフロー |
| `skills` | `author-skill` | `skills-author-skill` | スキル作成という1つの作業 |

**Why**: 命名規約は「型」です。型があるから迷わず速く動ける。これが基礎と型の追求の実践です。

**補足ルール**:
- `description` は発動トリガー面なので、具体的な "Use when..." を含める（≤1024文字）
- トップレベルキーは `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility` に限定
- `author` / `tags` / `invocable` は `metadata` 配下に置く

### ステップ2 — 初期スケルトンを生成（統合）

執筆前に最小構造を作成します。

```
<skill-name>/
├── SKILL.md
└── references/
    └── SKILL.ja.md
```

方法:
- このスキルのセクション順テンプレートを手動で作成
- 環境にスクリプトがある場合はスクリプト生成
- AIで骨子生成後、プレースホルダーを即時置換

### ステップ3 — 「When to Use This Skill」を書く

タイトル後の**最初のH2セクション**でなければなりません。5〜8個の具体的で行動指向のシナリオを書きます。

**Why**: 「誰もが5秒で判断できる」ことがニュートラルな視点の実践。曖昧な表現は個人知のままです。

**重要**: スキル発動に使われるのは主に `description` であり、このセクションは発動後の実行ガイドです。

### ステップ4 — Core Principles定義（3〜5個）

各原則を最低1つのPHILOSOPHY Valueに接続します。

**Why**: Valuesとの接続が、このスキルを「ただのドキュメント」から「開発哲学の実践」に変えます。これが温故知新 — 過去の知恵と新しい技術を繋ぐことです。

### ステップ5 — 1つのパターンを選び、記述する

タスクに合うパターンを1つ選んで、そのパターン中心でスキルを構成します。

| パターン | 使う場面 | 典型構造 |
|---|---|---|
| Sequential Workflow | 順序固定の実行手順 | `## Workflow:` + `### Step N` |
| Cycle/Loop | 改善→検証→修正を反復 | ループ段階 + 終了条件 |
| Situational/Router | 状況で分岐判断が必要 | Decision Table + 分岐先 |
| Cascade | 段階的に精度を上げる | ステージ別の精錬 |
| Parallel | 独立タスクを並列処理できる | 分割/統合フロー |
| Multi-MCP | 複数システム/エージェント連携 | オーケストレーション + 契約 |

**Why**: 「1スキル＝1パターン」の原則は、最小形式で最大可能性を生む設計思想（基礎と型）から来ています。複数パターンを詰め込むと、AIのコンテキストを無駄に消費し、人間の読み手も迷います。

### ステップ6 — Good PracticesとPitfallsを追加

各Good PracticeにはValuesリンクを含めます。各PitfallにはProblem/Solutionの構造を使用します。

### ステップ7 — Quick ReferenceとResourcesを追加

チェックリスト、デシジョンツリー、またはサマリーテーブルを提供します。

### ステップ8 — ファイルサイズ管理

SKILL.mdが〜450行を超えたら、積極的にコンテンツを`references/`に移動します。

**Why**: 500行制限はAIエージェントのコンテキストウィンドウ効率のため。基礎と型 — 最小形式で最大可能性を解放する設計思想です。

### ステップ9 — 日本語版作成

`references/SKILL.ja.md`を同一構造で作成。日本語版ではより深い「なぜ」の説明を含められます。

**Why**: 継続は力 — バイリンガル対応を最初から習慣にすることで、後からの対応コストを削減します。

### ステップ10 — 検証

`skills-validate-skill`を実行して品質基準をチェック。全体≥80%、カテゴリごと≥80%を目標にします。

---

## Good Practices

### 1. 「When to Use」で素早い発見を実現

**What**: 「When to Use This Skill」を最初のH2に配置し、5〜8個の具体的シナリオを記載。

**Why**: 5秒の関連性チェックを可能にし、AIエージェントの発見性を向上。

**Values**: ニュートラル（形式知化で誰もが理解可能）

### 2. ✅/❌マーカーを一貫して使用

**What**: コードに`// ✅ CORRECT - 理由`または`// ❌ WRONG - 理由`をプレフィックス。

**Why**: 曖昧さを排除し、対比学習を可能にする。

**Values**: 基礎と型（明確なパターン）/ 成長の複利（対比学習）

### 3. コメントでWHYを説明

**What**: コメントは構文ではなく根拠を説明。

**Why**: 暗黙知を形式知に変換し、複利的な学習成長を支援。

**Values**: 成長の複利（学習資産化）/ ニュートラル（形式知化）

---

## Common Pitfalls

### 1. 複数ワークフローを1つのスキルに詰め込む

**Problem**: 7〜10個の番号付き`## Pattern N:`セクションが実際には別々のワークフロー。

**Solution**: 1スキル＝1パターン。独立したパターンは別のスキルに分割。

### 2. 曖昧な「When to Use」シナリオ

**Problem**: 「良いコード品質が欲しい時」のような抽象的なシナリオ。

**Solution**: 具体的かつ動詞先導：「SKILL.mdの構造を64項目チェックリストで検証する時」

### 3. Values統合の欠落

**Problem**: Core PrinciplesがPHILOSOPHY.mdと接続していない。

**Solution**: 各原則が括弧内で最低1つのValueを引用。

---

## Quick Reference

### スキル作成チェックリスト

- [ ] YAMLフロントマター: name, description（"Use when..."含む）, metadata(author/tags/invocable)
- [ ] `name`がディレクトリ名と一致、`<context>-<workflow>`規約に従う
- [ ] 「When to Use This Skill」が最初のH2（5〜8個の動詞先導シナリオ）
- [ ] Core Principles（3〜5個）に≥2個のValues参照
- [ ] 単一ワークフローセクション（順序立てたステップ）
- [ ] コード例に✅/❌マーカー、WHYを説明
- [ ] Good PracticesセクションにValuesリンク
- [ ] Common Pitfalls（3〜5項目）
- [ ] SKILL.md ≤ 500行
- [ ] `references/SKILL.ja.md`が存在（日本語版）
- [ ] `skills-validate-skill`で検証済み

---

## Resources

- [PHILOSOPHY.md](../../PHILOSOPHY.md) — 開発憲法とValues
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — 品質検証

---
