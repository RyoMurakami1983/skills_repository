<!-- 
このドキュメントは dotnet-slopwatch の日本語版です。
英語版: ../SKILL.md
-->

---
name: dotnet-slopwatch
description: >
  Detect LLM reward hacking in .NET code changes with Slopwatch.
  Use when validating LLM-generated C# code, running post-edit
  hooks, or integrating anti-slop quality gates into CI/CD.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, quality, llm, anti-cheat, slopwatch]
  invocable: true
---

# Slopwatch: .NET向けLLMアンチチート

Slopwatchをインストール・設定・使用して「スロップ」を検出するワークフロー。スロップとは、LLMがテストを通すためやビルドを成功させるために取る近道のことで、根本的な問題を解決していないパターンを指す。

## When to Use This Skill

このスキルを使用する場面：
- LLMが生成したC#コード変更をリワードハッキングパターンから検証する時
- Slopwatchを Claude Code のポストエディットフックとして設定する時
- GitHub ActionsやAzure Pipelinesにアンチスロップ品質ゲートを統合する時
- 既存の.NETプロジェクトにベースラインを確立する時
- 検出ルールやseverityレベルをチーム向けに設定する時
- Slopwatchが特定の変更をフラグした理由を調査する時

---

## Related Skills

- **`crap-analysis`** — 複雑性とカバレッジ不足が組み合わさったハイリスクコードの特定
- **`modern-csharp-coding-standards`** — Slopwatchが施行を助けるコーディング標準
- **`dotnet-local-tools`** — Slopwatchをバージョン管理されたローカルツールとして管理

---

## Core Principles

1. **新規スロップへのゼロトレランス** — 既存の問題はベースライン化し、新しい近道は無条件でブロック（基礎と型）
2. **抑制ではなく修正** — フラグされたパターンは全て適切な修正を要求する。回避策ではない（温故知新）
3. **LLMは特別ではない** — 人間とAIが生成したコードに同じ品質ルールを適用（ニュートラル）
4. **ベースラインがレガシーを分離** — 既存の技術的負債は認識しつつ、新規変更と分離（余白の設計）

---

## ワークフロー：Slopwatchのインストールと使用

### Step 1 — Slopwatchのインストール

`.config/dotnet-tools.json`にローカルツールとして追加する：

```json
{
  "version": 1,
  "isRoot": true,
  "tools": {
    "slopwatch.cmd": {
      "version": "0.2.0",
      "commands": ["slopwatch"],
      "rollForward": false
    }
  }
}
```

```bash
dotnet tool restore
```

**Why**: ツールのバージョンをリポジトリに固定することで、チーム全員が同じ検出ルールで作業できる。

> **Values**: 継続は力（ツールをバージョン管理し再現可能に）

### Step 2 — ベースラインの確立

プロジェクトでSlopwatchを使用する前に、既存の問題のベースラインを作成する：

```bash
slopwatch init
git add .slopwatch/baseline.json
git commit -m "chore: add slopwatch baseline"
```

**Why**: レガシーコードにはパターンが存在する場合がある。ベースラインにより**新しい**スロップのみが検出される。

> **Values**: 余白の設計（レガシーを認め、新規の品質を守る）

### Step 3 — コード変更のたびに実行

```bash
# 標準分析
slopwatch analyze

# 厳格モード — 警告でも失敗（LLMセッション推奨）
slopwatch analyze --fail-on warning
```

Slopwatchが問題をフラグした場合、**無視しない**：

1. LLMがなぜその近道を取ったか理解する
2. 適切な修正を要求する — 何が問題か具体的に伝える
3. 修正が別のスロップを導入していないか確認する

**Why**: 根本原因の修正が「型」。テストを通すための近道は、問題を先送りにしているだけ。

> **Values**: 基礎と型（根本原因の修正が型）

### Step 4 — Claude Code フックの設定

`.claude/settings.json`にポストエディットフックとしてSlopwatchを追加する：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "slopwatch analyze -d . --hook",
            "timeout": 60000
          }
        ]
      }
    ]
  }
}
```

**Why**: 自動ガードレールにより、LLMが編集するたびにスロップが即座にブロックされる。人間がレビューする前に品質が担保される。

> **Values**: 成長の複利（自動ガードレールで品質を仕組み化）

### Step 5 — CI/CDパイプラインへの追加

GitHub Actionsの品質ゲートとして使用する：

```yaml
jobs:
  slopwatch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'
      - run: dotnet tool install --global Slopwatch.Cmd
      - run: slopwatch analyze -d . --fail-on warning
```

**Why**: CIに組み込むことで、PRレビュー前にスロップが自動検出される。

> **Values**: 基礎と型（品質ゲートを基盤に組み込む）

---

## Detection Rules

| ルール | 重大度 | パターン | 例 |
|--------|--------|---------|-----|
| SW001 | Error | テスト無効化 | `[Fact(Skip="flaky")]`, `#if false` |
| SW002 | Warning | 警告抑制 | `#pragma warning disable CS8618` |
| SW003 | Error | 空catchブロック | `catch (Exception) { }` |
| SW004 | Warning | 恣意的な遅延 | テスト内の`await Task.Delay(1000);` |
| SW005 | Warning | プロジェクトファイルスロップ | `<NoWarn>CS1591</NoWarn>` |
| SW006 | Warning | CPMバイパス | インライン`Version="1.0.0"` |

---

## Good Practices

### 1. LLMセッション時の厳格モード

**What**: AI支援コーディング中にすべてのルールをerror severityに引き上げる。

**Why**: LLMは人間よりもスロップを導入しやすい — より高いガードレールが正当化される。

**Values**: 基礎と型（厳格な型でスロップを排除）

### 2. 初回使用時のベースライン

**What**: 既存プロジェクトでの初回`analyze`前に必ず`slopwatch init`を実行。

**Why**: ベースラインなしでは、すべてのレガシー問題が偽陽性を引き起こし、ツールへの信頼が損なわれる。

**Values**: 余白の設計（既存の技術的負債を認識して分離）

---

## Common Pitfalls

### 1. 警告を黙らせるためにベースラインを更新

**Problem**: Slopwatchが問題をフラグするたびに`--update-baseline`を実行する。

**Solution**: 正当に例外とされる場合のみベースラインを更新（サードパーティ制約、生成コード）。理由をコードコメントに記録。

### 2. コードを修正する代わりにルールを無効化

**Problem**: ノイジーなルールに`"enabled": false`を設定。

**Solution**: 根本のコードを修正する。ルールが偽陽性を生む場合、アップストリームに報告する。ガードレールを無効にしない。

---

## Anti-Patterns

### 「後で直す」

**What**: 後でリビジットする計画でスロップを受け入れる。

**Why It's Wrong**: 「後で」は来ない。近道が永久的な技術的負債になる。

**Better Approach**: 実際の問題を今修正する。時間制約がある場合、追跡issueを作成しガードレールは有効のまま保つ。

### スロップをスロップで修正

**What**: 無効化されたテストを`Task.Delay(2000)`の追加で修正し、レースコンディションは放置。

**Why It's Wrong**: 1つのスロップパターン（SW001）を別のパターン（SW004）に置き換えているだけ。

**Better Approach**: 根本原因を特定して修正する（レースコンディション、タイミング依存、共有状態）。

---

## Quick Reference

```bash
# 初回セットアップ
slopwatch init
git add .slopwatch/baseline.json

# LLMコード変更後に毎回
slopwatch analyze

# 厳格モード（推奨）
slopwatch analyze --fail-on warning

# フックモード（git dirty filesのみ）
slopwatch analyze -d . --hook

# ベースライン更新（稀、理由を記録）
slopwatch analyze --update-baseline
```

### オーバーライド判断テーブル

| シナリオ | アクション | 要件 |
|----------|---------|------|
| サードパーティがパターンを強制 | ベースライン更新 | 理由のコードコメント |
| 生成コード（編集不可） | 除外リストに追加 | 設定に記録 |
| 意図的なレート制限 | ベースライン更新 | コードコメント、テスト外 |
| 「テストが不安定」 | ❌ オーバーライドしない | 不安定さを修正 |
| 「警告がうるさい」 | ❌ オーバーライドしない | コードを修正 |

---

## Resources

- [Slopwatch NuGet Package](https://www.nuget.org/packages/Slopwatch.Cmd)
- [dotnet-local-tools](../dotnet-local-tools/SKILL.md) — .NETローカルツールの管理
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — 開発憲法

---
