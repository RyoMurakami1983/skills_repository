<!-- このドキュメントは dotnet-local-tools の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-local-tools
description: >
  dotnet-tools.json によるローカル .NET ツールの管理。開発環境と CI/CD パイプライン全体で
  バージョン固定された一貫したツール環境を構築。リポジトリ単位の CLI ツール管理時に使用。
metadata:
  author: RyoMurakami1983
  tags: [dotnet, cli-tools, dotnet-tools-json, ci-cd, devops]
  invocable: false
  version: 1.0.0
---

# .NET ローカルツール

`.config/dotnet-tools.json` によるリポジトリ単位の CLI ツール管理：マニフェスト初期化、ツールインストール、バージョン固定、CI/CD 統合、ライフサイクル管理。

## When to Use This Skill

以下の場合にこのスキルを使用してください：

- 共有マニフェストで開発チーム全体に一貫した CLI ツール環境を構築するとき
- CI/CD パイプラインでローカル開発と同じツールバージョンを復元・使用するとき
- docfx、dotnet-ef、csharpier、reportgenerator などプロジェクト固有ツールをインストールするとき
- 1台のマシン上の複数プロジェクト間でグローバルツールのバージョン競合を回避するとき
- グローバルインストールされたツールからリポジトリ単位のローカルツール管理に移行するとき
- Dependabot や Renovate でローカルツールのバージョン更新を自動化するとき
- dotnet tool restore 実行後のツール未検出エラーをトラブルシューティングするとき

---

## Related Skills

- **`dotnet-project-structure`** — .slnx、Directory.Build.props、global.json によるソリューション構築
- **`git-commit-practices`** — 各ツール追加をアトミックな変更としてコミット
- **`tdd-standard-practice`** — ツール出力を自動テストで検証

---

## Core Principles

1. **Per-Repository Isolation（リポジトリ単位の分離）** — 各プロジェクトが独自のツールセットを所有し、グローバル状態がリポジトリ間で漏れない（基礎と型）
2. **Reproducible Tooling（再現可能なツール環境）** — マニフェストに正確なバージョンを固定し、すべての環境で同一のツールを復元（基礎と型）
3. **Single Restore Command（単一の復元コマンド）** — `dotnet tool restore` が CI/CD での個別インストールコマンドを置き換える（成長の複利）
4. **Progressive Adoption（段階的な採用）** — 1つのツールから始め、必要に応じて追加。マニフェストは漸進的に成長（継続は力）
5. **Transparent Configuration（透明な設定）** — `dotnet-tools.json` はソースコントロールにコミットされる人間が読める JSON（温故知新）

---

## Workflow: Manage .NET Local Tools

### Step 1 — ツールマニフェストの初期化

新しいリポジトリの作成時、または既存プロジェクトへのローカルツールサポートの追加時に使用します。

```bash
# .config/dotnet-tools.json を作成
dotnet new tool-manifest
```

マニフェストのディレクトリ構造が作成されます：

```
.config/
└── dotnet-tools.json
```

**初期マニフェスト内容:**

```json
{
  "version": 1,
  "isRoot": true,
  "tools": {}
}
```

| フィールド | 説明 | デフォルト |
|-----------|------|-----------|
| `version` | マニフェストスキーマバージョン | `1` |
| `isRoot` | 親ディレクトリへのマニフェスト検索を防止 | `true` |
| `tools` | ツール設定のディクショナリ | `{}` |

**なぜ `isRoot: true` か**: このフラグがないと、MSBuild がディレクトリツリーを上方に走査して追加のマニフェストを探し、予期しないツール解決が発生します。

> **Values**: 基礎と型（マニフェストがすべてのツール管理の構造的基盤を提供） / 余白の設計

### Step 2 — ツールのローカルインストール

リポジトリマニフェストにプロジェクト固有の CLI ツールを追加するときに使用します。

```bash
# ツールをローカルにインストール（最新バージョン）
dotnet tool install docfx

# 特定のバージョンをインストール
dotnet tool install docfx --version 2.78.3

# プライベートフィードからインストール
dotnet tool install MyTool --add-source https://pkgs.dev.azure.com/org/_packaging/feed/nuget/v3/index.json
```

**.NET プロジェクトで一般的なツール:**

| ツール | パッケージ名 | コマンド | 用途 |
|--------|-------------|---------|------|
| DocFX | `docfx` | `dotnet docfx` | API ドキュメント生成 |
| EF Core CLI | `dotnet-ef` | `dotnet ef` | データベースマイグレーション |
| ReportGenerator | `dotnet-reportgenerator-globaltool` | `dotnet reportgenerator` | コードカバレッジレポート |
| CSharpier | `csharpier` | `dotnet csharpier` | C# コードフォーマット |
| Incrementalist | `incrementalist.cmd` | `incrementalist` | 変更プロジェクトのみビルド |

各 `dotnet tool install` コマンドが `dotnet-tools.json` を自動的に更新します。

> **Values**: 継続は力（ツールを1つずつ追加し、マニフェストを漸進的に構築） / 基礎と型

### Step 3 — バージョン固定の設定

すべての環境で再現可能なツールバージョンを保証するときに使用します。

**バージョン固定されたマニフェストの例:**

```json
{
  "version": 1,
  "isRoot": true,
  "tools": {
    "docfx": {
      "version": "2.78.3",
      "commands": ["docfx"],
      "rollForward": false
    },
    "dotnet-ef": {
      "version": "9.0.0",
      "commands": ["dotnet-ef"],
      "rollForward": false
    },
    "dotnet-reportgenerator-globaltool": {
      "version": "5.4.1",
      "commands": ["reportgenerator"],
      "rollForward": false
    },
    "csharpier": {
      "version": "0.30.3",
      "commands": ["dotnet-csharpier"],
      "rollForward": false
    }
  }
}
```

| フィールド | 説明 | 推奨 |
|-----------|------|------|
| `tools.<name>.version` | インストールする正確なバージョン | 明示的に固定 |
| `tools.<name>.commands` | ツールが提供する CLI コマンド | NuGet から取得 |
| `tools.<name>.rollForward` | 新しいバージョンを許可 | `false` |

**なぜ `rollForward: false` か**: すべての開発者と CI エージェントが完全に同じツールバージョンを使用し、「自分のマシンでは動く」問題を防止します。

> **Values**: 基礎と型（バージョン固定が環境ドリフトを排除） / ニュートラルな視点

### Step 4 — CI/CD との統合

自動化パイプラインでローカルツールを復元・使用するように設定するときに使用します。

**GitHub Actions:**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          global-json-file: global.json

      - name: Restore tools
        run: dotnet tool restore

      - name: Format check
        run: dotnet csharpier --check .

      - name: Build and test
        run: dotnet build && dotnet test --collect:"XPlat Code Coverage"

      - name: Generate coverage report
        run: dotnet reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coveragereport
```

**Azure Pipelines:**

```yaml
steps:
  - task: UseDotNet@2
    inputs:
      useGlobalJson: true

  - script: dotnet tool restore
    displayName: 'Restore .NET tools'

  - script: dotnet csharpier --check .
    displayName: 'Format check'

  - script: dotnet build -c Release && dotnet test -c Release --collect:"XPlat Code Coverage"
    displayName: 'Build and test'
```

**なぜ使用前に復元するのか**: ローカルツールは `dotnet tool restore` を実行するまで使用できません。このステップを省略すると CI で「コマンドが見つかりません」エラーが発生します。

> **Values**: 成長の複利（CI 自動化がすべてのビルドで品質を複利的に向上） / 基礎と型

### Step 5 — ツールバージョンの管理

リポジトリマニフェストのツールを更新、一覧表示、または削除するときに使用します。

**ツールの更新:**

```bash
# 最新バージョンに更新
dotnet tool update docfx

# 特定のバージョンに更新
dotnet tool update docfx --version 2.79.0
```

**インストール済みツールの一覧:**

```bash
# ローカルツールとバージョンを一覧
dotnet tool list

# 更新可能なツールをチェック
dotnet tool list --outdated
```

**ツールの削除:**

```bash
dotnet tool uninstall docfx
```

**Dependabot で更新を自動化:**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "nuget"
    directory: "/"
    schedule:
      interval: "weekly"
```

Dependabot が `.config/dotnet-tools.json` を自動検出し、ツールバージョン更新のプルリクエストを作成します。

> **Values**: 継続は力（定期的な更新でツールを最新に保つ） / 余白の設計

---

## Good Practices

### 1. CI の最初のステップでツールを復元

**What**: SDK セットアップ直後、ビルドやテストステップの前に `dotnet tool restore` を実行します。

- Use `dotnet tool restore` を SDK セットアップ後の最初のステップとして使用
- Avoid ツール復元完了前のツール呼び出しを避ける

**Why**: ローカルツールは復元されるまで使用不可。後続のツール呼び出しステップがサイレントに失敗するか、分かりにくいエラーが発生します。

**Values**: 基礎と型（信頼性の高い CI は完全な環境から始まる）

### 2. CI でフォーマットチェックを実行

**What**: CI で `dotnet csharpier --check .` を使用して、ファイルを変更せずに一貫したフォーマットを強制します。

- Apply マージ前に CI でフォーマットチェックを適用
- Consider パイプラインでファイル変更を避ける `--check` モードを検討

**Why**: フォーマットのドリフトを早期にキャッチし、コードレビューをスタイルではなくロジックに集中させます。

**Values**: 成長の複利（自動フォーマットがコードの一貫性を複利的に向上）

### 3. README にツール要件を記載

**What**: 「開発セットアップ」セクションに `dotnet tool restore` を前提条件として記載します。

- Define 新しいコントリビューター向けにセットアップ手順を README に定義
- Use 単一の復元コマンドでオンボーディングを簡素化

**Why**: 新しいチームメンバーがツールインストール手順を探す代わりに、単一のコマンドで環境を構築できます。

**Values**: ニュートラルな視点（誰でもアクセスできるオンボーディング）

---

## Common Pitfalls

### 1. サブディレクトリからのツール実行

**Problem**: マニフェストが見つからないサブディレクトリからローカルツールを呼び出す。

**Solution**: `.config/dotnet-tools.json` が存在するリポジトリルートからツールコマンドを実行してください。

```bash
# ❌ WRONG — サブディレクトリから実行
cd src/MyApp
dotnet docfx  # エラー: ツールが見つかりません

# ✅ CORRECT — ソリューションルートから実行
cd ../..
dotnet docfx docs/docfx.json
```

### 2. グローバルツールとのバージョン競合

**Problem**: グローバルにインストールされたツールがローカルバージョンを隠蔽し、予期しない動作を引き起こす。

**Solution**: `dotnet tool list -g` でグローバルツールの競合を確認し、グローバルバージョンをアンインストールしてください。

```bash
# ❌ WRONG — グローバルとローカルのバージョンが共存
dotnet tool install -g docfx           # グローバル v2.77.0
dotnet tool install docfx --version 2.78.3  # ローカル v2.78.3

# ✅ CORRECT — グローバルを削除し、ローカルのみ使用
dotnet tool uninstall -g docfx
dotnet tool restore
```

### 3. CI でのツール復元の忘れ

**Problem**: CI パイプラインがツールを復元せずに呼び出し、「コマンドが見つかりません」エラーが発生。

**Solution**: ツール使用前に `dotnet tool restore` を明示的なステップとして追加してください。

---

## Anti-Patterns

### プロジェクト固有ツールにグローバルツールを使用

**What**: ローカルマニフェストの代わりに `dotnet tool install -g` ですべての CLI ツールをグローバルにインストール。

**Why It's Wrong**: グローバルツールはプロジェクト間でバージョン競合を生み、バージョン管理ができず、すべての開発者マシンと CI エージェントで手動インストールが必要。

**Better Approach**: `dotnet new tool-manifest` と `dotnet tool install`（`-g` なし）を使用して、ソースコントロールにコミットされるリポジトリ単位のマニフェストを作成。

### バージョンのロールフォワードを許可

**What**: `"rollForward": true` に設定するかフィールドを省略して、自動バージョンアップグレードを許可。

**Why It's Wrong**: 異なる環境で異なるツールバージョンが解決され、ビルドの再現性が損なわれ、断続的な CI 障害の原因に。

**Better Approach**: 常に `"rollForward": false` を設定し、`dotnet tool update` で明示的にバージョンを更新。

---

## Quick Reference

### ローカルツール vs グローバルツール判断テーブル

| 観点 | グローバルツール | ローカルツール |
|------|-----------------|---------------|
| インストール | `dotnet tool install -g` | `dotnet tool restore` |
| スコープ | マシン全体 | リポジトリ単位 |
| バージョン管理 | 手動追跡 | `.config/dotnet-tools.json` |
| CI/CD セットアップ | 各ツールを個別にインストール | 単一の `dotnet tool restore` |
| バージョン競合 | プロジェクト間で発生の可能性 | プロジェクトごとに分離 |
| 推奨 | プロジェクトには避ける | ✅ すべてのプロジェクトツールに使用 |

### よく使うコマンド

| コマンド | 用途 | 使用タイミング |
|---------|------|---------------|
| `dotnet new tool-manifest` | マニフェストの初期化 | 新リポジトリのセットアップ |
| `dotnet tool install <name>` | マニフェストにツールを追加 | 新しいツールの追加 |
| `dotnet tool restore` | マニフェストからすべてのツールを復元 | クローン後または CI 開始時 |
| `dotnet tool update <name>` | ツールバージョンの更新 | バージョン更新が必要な時 |
| `dotnet tool list` | インストール済みツールの一覧 | 現在のツールの監査 |
| `dotnet tool list --outdated` | 更新可能なツールのチェック | 定期的なメンテナンス |
| `dotnet tool uninstall <name>` | マニフェストからツールを削除 | ツールが不要になった時 |

---

## Resources

- [.NET ローカルツール概要](https://learn.microsoft.com/ja-jp/dotnet/core/tools/local-tools-how-to-use) — 公式ローカルツールドキュメント
- [dotnet tool install](https://learn.microsoft.com/ja-jp/dotnet/core/tools/dotnet-tool-install) — ツールインストールリファレンス
- [dotnet-tools.json スキーマ](https://learn.microsoft.com/ja-jp/dotnet/core/tools/local-tools-how-to-use#tool-manifest-file) — マニフェストファイル形式
- [Dependabot for .NET](https://docs.github.com/ja/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file) — ツールバージョン自動更新
