<!-- このドキュメントは dotnet-package-management の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-package-management
description: >
  NuGet パッケージを Central Package Management (CPM) と dotnet CLI コマンドで管理。
  .NET プロジェクト間でパッケージバージョンの追加・削除・更新・一元化を行うときに使用。
metadata:
  author: RyoMurakami1983
  tags: [dotnet, nuget, cpm, package-management, cli]
  invocable: false
  version: 1.0.0
---

# NuGet パッケージ管理

.NET ソリューションにおけるNuGetパッケージ管理のエンドツーエンドワークフロー：Central Package Management (CPM) セットアップ、dotnet CLI 操作、共有バージョン変数、パッケージソース設定、依存関係監査。

## When to Use This Skill

以下の場合にこのスキルを使用してください：

- dotnet CLI コマンドを使用して .NET プロジェクトに NuGet パッケージを追加または削除するとき
- Central Package Management (CPM) を設定してソリューション全体のバージョンを統一するとき
- 関連する NuGet パッケージを Directory.Packages.props の共有バージョン変数で整理するとき
- プライベート NuGet フィードやソリューション固有のパッケージソースを NuGet.Config で設定するとき
- dotnet list コマンドで古い・脆弱・非推奨のパッケージを監査するとき
- 個々の .csproj ファイルを編集せずに NuGet パッケージバージョンを一元的に更新するとき
- キャッシュクリアと依存関係ツリーの確認でパッケージ復元の失敗をトラブルシュートするとき

---

## Related Skills

- **`dotnet-project-structure`** — ソリューションレベルのビルド設定と Directory.Build.props のセットアップ
- **`dotnet-local-tools`** — dotnet-tools.json マニフェストによるローカル .NET ツール管理
- **`dotnet-slopwatch`** — 不要な VersionOverride 使用を含むスロップパターンの検出
- **`git-commit-practices`** — 各パッケージ変更をアトミックな Conventional Commit でコミット

---

## Core Principles

1. **CLI-First Operations（CLI ファースト操作）** — XML を手動編集する代わりに常に `dotnet add/remove/list` コマンドを使用する。CLI はパッケージの検証、バージョン解決、ロックファイル更新を行う（基礎と型）
2. **Single Source of Truth（単一の信頼できる情報源）** — すべてのパッケージバージョンを `Directory.Packages.props` に集約し、すべてのプロジェクトが一つの権威あるバージョンレジストリを参照する（基礎と型）
3. **Grouped Version Variables（グループ化されたバージョン変数）** — 関連パッケージは単一のバージョン変数を共有し、同期が必要なパッケージ間のバージョンドリフトを防止する（継続は力）
4. **Audit Before Deploy（デプロイ前の監査）** — `dotnet list package --outdated --vulnerable --deprecated` を定期的に実行し、セキュリティと互換性の問題を早期発見する（温故知新）
5. **Reproducible Restores（再現可能な復元）** — `NuGet.Config` で `<clear />` を使用してパッケージソースを固定し、ロックファイルですべての環境で同一の依存関係グラフを生成する（ニュートラル）

---

## Workflow: Manage NuGet Packages

### Step 1 — Central Package Management の有効化

すべての NuGet パッケージバージョンを単一の `Directory.Packages.props` ファイルに集約するときに使用します。

**前提条件：**

| 要件 | 最低バージョン |
|------|----------------|
| .NET SDK | 6.0.300 |
| NuGet | 6.2 |
| Visual Studio | 2022 17.2 |

ソリューションルートに `Directory.Packages.props` を作成します：

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <ItemGroup>
    <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageVersion Include="Serilog" Version="4.0.0" />
    <PackageVersion Include="xunit" Version="2.9.2" />
  </ItemGroup>
</Project>
```

**プロジェクトファイル**はバージョンなしでパッケージを参照します：

```xml
<!-- src/MyApp/MyApp.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" />
    <PackageReference Include="Serilog" />
  </ItemGroup>
</Project>
```

**なぜ CPM か**: プロジェクト間のバージョンドリフトを排除します。`Directory.Packages.props` の1行を更新するだけで、そのパッケージを使用するすべてのプロジェクトに伝播します。

> **Values**: 基礎と型（すべてのパッケージバージョンの単一の信頼できる情報源） / ニュートラル

### Step 2 — CLI によるパッケージの追加と削除

プロジェクトに NuGet パッケージをインストールまたはアンインストールするときに使用します。`.csproj` や `Directory.Packages.props` の XML を手動で編集しないでください。

**パッケージの追加：**

```bash
# 最新の安定版を追加
dotnet add package Serilog

# 特定のバージョンを追加
dotnet add package Serilog --version 4.0.0

# プレリリースパッケージを追加
dotnet add package Serilog --prerelease

# 特定のプロジェクトに追加
dotnet add src/MyApp/MyApp.csproj package Serilog
```

**CPM 有効時**は、`dotnet add package` が `Directory.Packages.props` とプロジェクトファイルの両方を自動的に更新します。

**パッケージの削除：**

```bash
# 現在のプロジェクトから削除
dotnet remove package Serilog

# 特定のプロジェクトから削除
dotnet remove src/MyApp/MyApp.csproj package Serilog
```

**なぜ CLI ファーストか**: CLI はフィード上にパッケージが存在することを検証し、正しいバージョンを解決し、推移的依存関係を処理し、ロックファイルを更新します。手動の XML 編集ではタイポ、パッケージの欠落、不正なマークアップのリスクがあります。

> **Values**: 基礎と型（CLI は手動編集では検証できないことを検証する） / 温故知新

### Step 3 — 共有バージョン変数による整理

複数の関連パッケージが実行時の非互換性を避けるために同じバージョンに揃える必要があるときに使用します。

`Directory.Packages.props` でバージョンプロパティを定義して参照します：

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <!-- 共有バージョン変数 -->
  <PropertyGroup Label="SharedVersions">
    <AkkaVersion>1.5.59</AkkaVersion>
    <OpenTelemetryVersion>1.11.0</OpenTelemetryVersion>
    <XunitVersion>2.9.2</XunitVersion>
  </PropertyGroup>

  <!-- Akka.NET パッケージ — すべて同じバージョン -->
  <ItemGroup Label="Akka.NET">
    <PackageVersion Include="Akka" Version="$(AkkaVersion)" />
    <PackageVersion Include="Akka.Cluster" Version="$(AkkaVersion)" />
    <PackageVersion Include="Akka.Persistence" Version="$(AkkaVersion)" />
    <PackageVersion Include="Akka.Streams" Version="$(AkkaVersion)" />
  </ItemGroup>

  <!-- OpenTelemetry パッケージ -->
  <ItemGroup Label="OpenTelemetry">
    <PackageVersion Include="OpenTelemetry.Exporter.OpenTelemetryProtocol" Version="$(OpenTelemetryVersion)" />
    <PackageVersion Include="OpenTelemetry.Extensions.Hosting" Version="$(OpenTelemetryVersion)" />
    <PackageVersion Include="OpenTelemetry.Instrumentation.AspNetCore" Version="$(OpenTelemetryVersion)" />
  </ItemGroup>

  <!-- テスト -->
  <ItemGroup Label="Testing">
    <PackageVersion Include="xunit" Version="$(XunitVersion)" />
    <PackageVersion Include="xunit.runner.visualstudio" Version="$(XunitVersion)" />
    <PackageVersion Include="FluentAssertions" Version="6.12.0" />
  </ItemGroup>
</Project>
```

**なぜバージョン変数か**: 1行を変更するだけですべてのAkkaパッケージを更新できます。ラベル付きの `<ItemGroup>` 要素により明確な整理が可能になり、偶発的なバージョン不一致を防ぎます。

> **Values**: 継続は力（一貫したバージョンが長期的な信頼性を積み上げる） / 成長の複利

### Step 4 — パッケージソースの設定

プライベート NuGet フィードの追加や、マシン間で再現可能な復元を確保するときに使用します。

**現在のソースを確認：**

```bash
dotnet nuget list source
```

**プライベートフィードの追加：**

```bash
dotnet nuget add source https://pkgs.dev.azure.com/myorg/_packaging/myfeed/nuget/v3/index.json \
  --name MyFeed \
  --username az \
  --password $PAT \
  --store-password-in-clear-text
```

**ソリューション固有の NuGet.Config** — 再現可能な復元のためにソリューションルートに作成：

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <!-- 継承されたマシンレベルのソースをクリア -->
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="MyPrivateFeed" value="https://pkgs.dev.azure.com/myorg/_packaging/myfeed/nuget/v3/index.json" />
  </packageSources>
  <packageSourceCredentials>
    <MyPrivateFeed>
      <add key="Username" value="az" />
      <add key="ClearTextPassword" value="%NUGET_PAT%" />
    </MyPrivateFeed>
  </packageSourceCredentials>
</configuration>
```

**なぜ `<clear />` か**: 継承されたマシンレベルの NuGet ソースを除去し、開発者のマシン設定に関わらず復元が同一の結果を生成するようにします。

> **Values**: ニュートラル（環境に依存しない、再現可能な復元） / 基礎と型

### Step 5 — 依存関係の監査と更新

リリース前に古い・脆弱・非推奨のパッケージを確認するときに使用します。

**パッケージの一覧表示：**

```bash
# ソリューション内の全パッケージを表示
dotnet list package

# 古いパッケージを表示
dotnet list package --outdated

# 推移的依存関係を含めて表示
dotnet list package --include-transitive

# 脆弱なパッケージを表示
dotnet list package --vulnerable

# 非推奨パッケージを表示
dotnet list package --deprecated
```

**CPM でのパッケージ更新：**

```bash
# Directory.Packages.props のバージョンを編集後、復元を実行
dotnet restore

# または dotnet-outdated ツールで一括アップグレード
dotnet tool install --global dotnet-outdated-tool
dotnet outdated --upgrade
```

**復元失敗のトラブルシューティング：**

```bash
# すべてのローカルキャッシュをクリア
dotnet nuget locals all --clear

# 詳細ログで復元
dotnet restore --verbosity detailed

# キャッシュを無視して強制復元
dotnet restore --force
```

**ロックファイルの有効化**（再現可能なビルドのため）：

```xml
<!-- Directory.Build.props -->
<PropertyGroup>
  <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
</PropertyGroup>
```

`packages.lock.json` ファイルをソース管理にコミットしてください。

**なぜ定期的な監査か**: 古いパッケージは技術的負債を蓄積し、脆弱なパッケージはセキュリティリスクを露呈します。自動化された監査により、本番環境に到達する前に問題を発見できます。

> **Values**: 温故知新（エコシステムの更新から学びセキュアに保つ） / 余白の設計

---

## Good Practices

### 1. すべてのパッケージ操作に CLI を使用する

**何を**: XML 編集の代わりに `dotnet add package` と `dotnet remove package` を実行する。

**なぜ**: CLI はパッケージの存在を検証し、互換バージョンを解決し、ロックファイルを更新し、CPM との統合を自動的に処理する。

**Values**: 基礎と型（すべての操作の信頼できる基盤としての CLI）

### 2. ItemGroup にドメイン別のラベルを付ける

**何を**: `Directory.Packages.props` の `<ItemGroup>` 要素に `Label="Akka.NET"` や `Label="Testing"` を使用する。

**なぜ**: 明確なラベルにより大きな依存関係ファイルがスキャンしやすくなり、レビュアーがパッケージのグループ分けを一目で理解できる。

**Values**: 余白の設計（視覚的構造が理解のための余白を生む）

### 3. 再現可能なビルドのためにロックファイルをコミットする

**何を**: `<RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>` を有効にし、`packages.lock.json` をコミットする。

**なぜ**: ロックファイルにより、すべての開発者と CI 環境がまったく同じ依存関係グラフを復元できる。

**Values**: ニュートラル（環境に関わらず同一の結果）

---

## Common Pitfalls

### 1. CLI を使わずに .csproj XML を直接編集する

**問題**: CLI 検証なしで `<PackageReference>` 要素を手動追加すると、タイポ、パッケージの欠落、不正な XML が発生する。

**解決策**: 常に `dotnet add package <name>` を使用する — CLI はパッケージの存在を検証し、正しいバージョンを解決する。

```bash
# ❌ 悪い例 — 手動 XML 編集
# <PackageReference Include="Typo.Package" Version="1.0.0" />

# ✅ 良い例 — CLI がパッケージを検証
dotnet add package Newtonsoft.Json
```

### 2. CPM 有効時に .csproj でバージョンを指定する

**問題**: CPM がアクティブな状態で `<PackageReference>` に `Version="x.y.z"` を追加すると、ビルドエラーが発生するか、一元管理を暗黙的にバイパスする。

**解決策**: すべての `.csproj` の `<PackageReference>` 要素から `Version` 属性を削除する。

```xml
<!-- ❌ 悪い例 — CPM と競合する -->
<PackageReference Include="Serilog" Version="4.0.0" />

<!-- ✅ 良い例 — バージョンは一元管理 -->
<PackageReference Include="Serilog" />
```

### 3. 推移的依存関係の競合を無視する

**問題**: 2つのパッケージが共有する推移的依存関係の異なるバージョンを取り込み、実行時の障害を引き起こす。

**解決策**: 完全な依存関係ツリーを検査し、競合するパッケージを明示的に固定する。

```bash
# 競合を特定
dotnet list package --include-transitive

# Directory.Packages.props で明示的なバージョンを追加して修正
```

---

## Anti-Patterns

### バージョン管理戦略の混在

**何を**: 一部のパッケージは `Directory.Packages.props` の CPM バージョンを使用し、他は `.csproj` ファイルにインラインバージョンを持つ。

**なぜ悪いか**: どのファイルがどのパッケージバージョンを制御しているか混乱を招く。開発者は単一の信頼できる情報源に依存できず、バージョン更新に複数のファイルタイプを検索する必要がある。

**より良いアプローチ**: ソリューション全体で CPM を採用する。単一プロジェクトが異なるバージョンを必要とする場合、`VersionOverride` を控えめに使用し、理由を文書化する。

### VersionOverride のデフォルト使用

**何を**: 中央バージョンを更新する代わりに CPM 制約を回避するために `VersionOverride="x.y.z"` を日常的に追加する。

**なぜ悪いか**: 一元管理の目的を損なう。各オーバーライドはアーキテクチャの一貫性を侵食する設計判断であり、依存関係の監査を信頼できなくする。

**より良いアプローチ**: `Directory.Packages.props` の中央バージョンを更新する。`VersionOverride` は文書化された一時的な例外にのみ使用する。

---

## Quick Reference

| タスク | コマンド |
|--------|----------|
| パッケージ追加 | `dotnet add package <name>` |
| 特定バージョン追加 | `dotnet add package <name> --version <ver>` |
| プレリリース追加 | `dotnet add package <name> --prerelease` |
| パッケージ削除 | `dotnet remove package <name>` |
| 全パッケージ表示 | `dotnet list package` |
| 古いパッケージ表示 | `dotnet list package --outdated` |
| 脆弱なパッケージ表示 | `dotnet list package --vulnerable` |
| 非推奨パッケージ表示 | `dotnet list package --deprecated` |
| 推移的依存関係表示 | `dotnet list package --include-transitive` |
| パッケージ復元 | `dotnet restore` |
| キャッシュクリア | `dotnet nuget locals all --clear` |
| 強制復元 | `dotnet restore --force` |
| ソース一覧 | `dotnet nuget list source` |

### CPM を使わない場合 — 判断テーブル

| シナリオ | CPM 使用？ | 理由 |
|----------|------------|------|
| 2プロジェクト以上の新規ソリューション | ✅ はい | 最初からバージョンドリフトを防止 |
| 単一プロジェクトのソリューション | ✅ 任意 | 低オーバーヘッド、成長に備える |
| 競合の多いレガシーソリューション | ⚠️ 段階的 | ビッグバンリスクを避けプロジェクト単位で移行 |
| バージョン範囲が必要 | ❌ いいえ | CPM は正確なバージョンが必要 |
| .NET SDK < 6.0.300 | ❌ いいえ | 古い SDK では CPM 非対応 |
| マルチリポの独立ビルド | ❌ リポ単位 | 各リポジトリに独自の Directory.Packages.props が必要 |

---

## Resources

- [Central Package Management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management) — NuGet CPM 公式ドキュメント
- [dotnet CLI リファレンス](https://learn.microsoft.com/en-us/dotnet/core/tools/) — dotnet コマンドの完全なリファレンス
- [NuGet.Config リファレンス](https://learn.microsoft.com/en-us/nuget/reference/nuget-config-file) — パッケージソース設定
- [dotnet-outdated ツール](https://github.com/dotnet-outdated/dotnet-outdated) — 一括パッケージ更新ツール
