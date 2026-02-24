<!-- 
このドキュメントは dotnet-slopwatch の日本語版です。
英語版: ../SKILL.md
-->

---
name: dotnet-slopwatch
description: >
  Two-layer slop prevention for .NET: code-level detection via Slopwatch CLI (SW-xxx)
  and architectural anti-pattern catalog (SLOP-xxx).
  Use when validating LLM-generated C# code, checking for layer boundary violations,
  or integrating anti-slop quality gates into CI/CD.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, quality, llm, anti-cheat, slopwatch]
  invocable: false
---

# Slopwatch: .NET向けLLMアンチチート

.NETプロジェクト向けの2層スロップ予防システム：

- **コードレベル (SW-xxx)** — Slopwatch CLIツールによる自動検出（テスト無効化、空catch、警告抑制）
- **アーキテクチャレベル (SLOP-xxx)** — 人間/LLMの判断が必要なアンチパターンカタログ（層境界違反、責務漏洩）

## When to Use This Skill

このスキルを使用する場面：
- LLMが生成したC#コード変更をリワードハッキングパターンから検証する時
- Presentation層のコードにApplication/Domain層に属するドメインロジックが含まれていないかチェックする時
- Slopwatchを Claude Code のポストエディットフックとして設定する時
- GitHub ActionsやAzure Pipelinesにアンチスロップ品質ゲートを統合する時
- 既存の.NETプロジェクトにベースラインを確立する時
- DDD/クリーンアーキテクチャにおけるアーキテクチャ判断をレビューする時

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
      "version": "0.3.4",  // check latest: dotnet tool search slopwatch
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

### Step 4 — AIコーディングアシスタントとの統合

#### 4a: 自動フック（Claude Code）

`.claude/settings.json`にポストエディットフックとしてSlopwatchを追加する。`--hook` フラグはgit dirty filesのみを解析し、stderrにエラーを出力し、デフォルトで警告時に失敗する：

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

#### 4b: オンデマンド（Copilot CLI）

`@dotnet-shihan` にslopwatch実行を依頼する。agentが `slopwatch analyze` をshell経由で実行し、結果を解釈する：

```
@dotnet-shihan slopwatch を実行して
@dotnet-shihan 近道してないかチェックして
```

agentはコードレビュー時にこのスキルとSLOP-xxxカタログを自動的に参照する。

**Why**: 自動ガードレール（Claude Code）またはオンデマンド検査（Copilot CLI）により、LLMのスロップが人間のレビュー前に検出される。

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

## コードレベル検出ルール (SW-xxx)

Slopwatch CLIツールが自動で適用するルール。

| ルール | 重大度 | パターン | 例 |
|--------|--------|---------|-----|
| SW001 | Error | テスト無効化 | `[Fact(Skip="flaky")]`, `#if false` |
| SW002 | Warning | 警告抑制 | `#pragma warning disable CS8618` |
| SW003 | Error | 空catchブロック | `catch (Exception) { }` |
| SW004 | Warning | 恣意的な遅延 | テスト内の`await Task.Delay(1000);` |
| SW005 | Warning | プロジェクトファイルスロップ | `<NoWarn>CS1591</NoWarn>` |
| SW006 | Error | パッケージバージョンオーバーライド | CPMバイパスのインライン`Version="1.0.0"` |

---

## アーキテクチャレベルスロップパターン (SLOP-xxx)

設計レベルのアンチパターン。人間またはLLMの判断が必要で、静的解析だけでは検出できない — アーキテクチャの意図を理解する必要がある。

### SLOP-001: Layer Boundary Violation（層境界違反）

**重大度**: Error

**症状**: 上位層（Presentation/ViewModel）が、下位層から受け取った結合文字列を `string.Split`、`Substring`、`Regex` 等で再解釈し、ドメイン値を再構築している。

**なぜ危険か**:
- 文字列フォーマットの暗黙的な前提に依存する（区切り文字、順序、エスケープ）
- ドメイン知識がPresentation層に漏洩する（「鋼種名にハイフンが含まれうる」）
- 変更に脆い：フォーマット変更時にPresentation層も壊れる

**Why（深掘り）**: この違反が起きる根本的な理由は「データが足りないから手元で作る」というLLMのSlop傾向にある。Application層のレスポンスに必要なフィールドが無い → 上位層でパースして補う — これは「最短距離の誘惑」であり、層構造という「型」を破壊する。型を破ると一見動くが、ドメインの構造を知らないとバグが見えない（鋼種名のハイフン問題）。

**実例** (MillScanSplitter PR#20):

```csharp
// ❌ SLOP-001: Presentation層でドメイン値をパース
// OcrValue = "25_10_29-394R072-9#SUH3-AIS-X578D"
var parts = ocrValue.Split('-');
var steelType = parts[2]; // "9#SUH3" を返す — 誤り（正解: "9#SUH3-AIS"）
```

鋼種名 `9#SUH3-AIS` にハイフンが含まれるため、単純な分割では値が破壊される。

```csharp
// ✅ 修正: Application層のレスポンスに構造化フィールドを追加
record ProcessDocumentComparisonRow(
    // ... 既存フィールド ...
    string ManufacturingNumber,  // Domain層の ExtractedItem から直接セット
    string SteelType,
    string HeatNo
);
```

**処方**: 上位層に必要なデータがレスポンスに無いなら、**下位層のレスポンスを拡張**せよ — 文字列パースでドメイン値を再構築するな。

**チェックポイント**:
- [ ] 新機能で必要なデータがApplication層レスポンスに構造化されているか？
- [ ] 構造化フィールドはDomain層のEntity/ValueObjectから直接マッピングされているか？
- [ ] Presentation層にドメイン文字列の `Split`/`Substring`/`Regex` が無いか？

**判断基準**: 「その `Split` は、ドメインの構造を知らないと書けないか？」 → Yes なら SLOP-001 違反。No なら正当な UI フォーマット処理。

> **Values**: 基礎と型（DDD層構造は「型」。型を破ると一見動くが、ドメイン知識の漏洩で脆くなる）

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

- [Slopwatch GitHub](https://github.com/Aaronontheweb/dotnet-slopwatch) — ソースコードとドキュメント
- [Slopwatch NuGet Package](https://www.nuget.org/packages/Slopwatch.Cmd)
- [dotnet-local-tools](../dotnet-local-tools/SKILL.md) — .NETローカルツールの管理
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — 開発憲法

---
