# Sub-agent Delegation Pattern（師範の委譲パターン）

> **Values**: 基礎と型の追求 / 成長の複利 / 余白の設計

## 概要

このドキュメントは、師範（Shihan）エージェントが特化型サブエージェントに作業を委譲する
パターンを定義する。「型」（kata）として機能し、将来のエージェント設計の一貫性を保証する。

---

## 二層構造の設計思想

```
┌─────────────────────────────────────────────────────────┐
│  師範レイヤー（Shihan Layer）                            │
│  人間向け・記憶に残る・ドメイン全体を統括                │
│                                                         │
│  @skill-shihan  @dotnet-shihan  @python-shihan          │
│  @typescript-shihan                                     │
└──────────────────┬──────────────────────────────────────┘
                   │ 委譲（Delegation）
                   ▼
┌─────────────────────────────────────────────────────────┐
│  機能レイヤー（Function Layer）                          │
│  自己文書化・特化・再利用可能                            │
│                                                         │
│  grader.md  reviewer.md  formatter.md  validator.md     │
└─────────────────────────────────────────────────────────┘
```

### なぜ二層構造か

| 観点 | 師範レイヤー | 機能レイヤー |
|------|------------|------------|
| 命名 | 記憶に残るメタファー | 機能を表す英語名 |
| スコープ | ドメイン全体（C#, Python, Skill） | 単一タスク（採点, レビュー, 整形） |
| 会話 | 人間との対話窓口 | 師範からの委譲先 |
| 進化 | 稀少性で価値を維持 | 必要に応じて追加可能 |

> **Values**: Progressive Disclosure — 公開層はメタファー、実装層は機能名。
> 師範が4つだから記憶に残る。機能エージェントが増えても師範の稀少性は維持される。

---

## 命名規則

### 師範（Shihan）エージェント

```
{domain}-shihan.agent.md
```

- `dotnet-shihan` — C#/.NET/WPF 全域
- `python-shihan` — Python エコシステム全域
- `skill-shihan` — スキル品質・メタスキル管理
- `typescript-shihan` — TypeScript/Node.js 全域

**原則**: 師範は原則として増やさない。ドメインが大きく変わるときのみ追加を検討する。

### 機能（Function）エージェント

```
{verb}-{noun}.agent.md  または  {role}.agent.md
```

**Good**（自己文書化）:
- `grader.agent.md` — スコアリング・採点
- `reviewer.agent.md` — コードレビュー
- `formatter.agent.md` — 整形・スタイル修正
- `validator.agent.md` — 検証・バリデーション
- `generator.agent.md` — コード生成

**Bad**（避けるべきパターン）:
- `門弟-採点.agent.md` — 空手用語。空手を知らない人に通じない
- `sub1.agent.md` — 無意味な番号
- `helper.agent.md` — 抽象的すぎる

> **Values**: ニュートラルな視点 — 誰もが使える普遍性を保つ。メタファーは師範レベルで十分。

---

## 委譲パターン

### パターン1: タスク特化委譲（Task-Specific Delegation）

師範が会話を受け取り、特定タスクを機能エージェントに渡す。

```markdown
<!-- skill-shihan.agent.md 内の委譲記述例 -->

## 委譲パターン

### バリデーション委譲

`validate_skill.py` を使った品質確認が必要な場合:

1. `validator.agent.md` を呼び出す
2. 結果を受け取り、先生モードの出力テンプレートで人間に報告する

### スコアリング委譲

複数スキルの一括採点が必要な場合:

1. `grader.agent.md` を呼び出す
2. スコア集計後、求道者モードで改善提案を生成する
```

### パターン2: パイプライン委譲（Pipeline Delegation）

タスクを順次複数の機能エージェントで処理する。

```
入力 → validator → grader → formatter → 出力
```

実装例（agent.md 記述スタイル）:

```markdown
## ワークフロー

### Step 1: 検証（validator へ委譲）
...

### Step 2: 採点（grader へ委譲）
...

### Step 3: 整形（formatter へ委譲）
...
```

### パターン3: コンテキスト保持委譲（Context-Preserving Delegation）

師範が文脈を保持しながら、判断ポイントごとに異なるエージェントを呼び出す。

```markdown
<!-- session-issue-autopilot のような長期セッション管理に適用 -->

## 委譲マップ

| フェーズ | 担当エージェント | 師範の役割 |
|--------|--------------|---------|
| Issue 解析 | `analyzer.agent.md` | 優先度判断 |
| 実装 | `{domain}-shihan` | 品質ゲート |
| PR 作成 | `github-pr-workflow` スキル | 承認確認 |
| ふりかえり | `furikaeri-practice` スキル | 知識捕捉 |
```

---

## 機能エージェントのテンプレート

新しい機能エージェントを作成する際は以下のテンプレートを使用する。

```markdown
---
name: "{role}"
description: "Use when {trigger context}. Handles {specific task}."
tools:
  - read
  - edit
  - shell
---

# {Role} Agent

## 責務

この エージェントが担当する単一の責務を1-2文で記述する。

## 入力

どのような入力を期待するか（ファイルパス、テキスト、構造など）。

## 出力

どのような形式で出力するか（レポート、変更済みファイル、スコアなど）。

## 処理ステップ

1. {Step 1}
2. {Step 2}
3. {Step 3}

## 品質基準

- この エージェントが「完了」と判断する条件

## 委譲元（親）

どの師範エージェントから呼び出されることを想定しているか。
```

---

## パイロット適用計画

### 適用候補1: skill-shihan への validator 委譲

現状: `skill-shihan.agent.md` が直接 `validate_skill.py` を実行している。
改善後: `validator.agent.md` が一括バリデーションを担当。skill-shihan は判断に集中。

```
@skill-shihan → validator.agent.md → validate_skill.py → 結果レポート
```

### 適用候補2: agent-batch-workflow への grader 委譲

現状: バッチ処理で個別進捗が混在している。
改善後: `grader.agent.md` が進捗スコアリングを担当。

---

## チェックリスト（新規機能エージェント作成時）

- [ ] ファイル名が機能を表す英語名（動詞-名詞 または 単一役割名）
- [ ] description に "Use when" トリガーフレーズあり
- [ ] 単一責務（ひとつのことだけを確実にやる）
- [ ] 入力・出力が明確に記述されている
- [ ] 委譲元（どの師範から呼び出されるか）が記述されている
- [ ] validate_skill.py に相当する品質基準が記述されている
