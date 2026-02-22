<!-- このドキュメントは dotnet-project-structure の日本語版です。英語版: ../SKILL.md -->

---
name: dotnet-project-structure
description: >
  モダン .NET プロジェクト構造（.slnx、Directory.Build.props、Central Package Management、
  SourceLink、バージョン管理、SDK固定）。.NETソリューションのセットアップ・近代化時に使用。
metadata:
  author: RyoMurakami1983
  tags: [dotnet, msbuild, nuget, slnx, sourcelink, project-structure]
  invocable: false
  version: 1.0.0
---

# .NET プロジェクト構造とビルド設定

モダン .NET ソリューションのセットアップに関するエンドツーエンドワークフロー：.slnx移行、ビルドプロパティの集約、Central Package Management (CPM)、SourceLinkデバッグ、RELEASE_NOTES駆動バージョニング、global.jsonによるSDK固定。

## When to Use This Skill

以下の場合にこのスキルを使用してください：

- モダンなプロジェクト構造規約で新しい .NET ソリューションをゼロから構築するとき
- 既存の .sln ソリューションファイルをモダンな XML ベースの .slnx 形式に移行するとき
- Directory.Build.props で複数プロジェクトのビルドプロパティを集約設定するとき
- Directory.Packages.props で NuGet パッケージバージョンの一元管理を導入するとき
- 公開 NuGet パッケージのステップスルーデバッグのため SourceLink を追加するとき
- ビルドプロセスで RELEASE_NOTES.md を解析してバージョン管理を自動化するとき
- すべての開発者マシンと CI/CD 環境で .NET SDK バージョンを固定するとき

---

## Related Skills

- **`dotnet-local-tools`** — dotnet-tools.json によるローカル .NET ツール管理
- **`microsoft-extensions-configuration`** — 設定バリデーションパターン
- **`git-commit-practices`** — 各ステップをアトミックな変更としてコミット
- **`tdd-standard-practice`** — Red-Green-Refactor で生成コードをテスト

---

## Core Principles

1. **Single Source of Truth（単一の信頼できる情報源）** — 各設定項目は1つのファイルにのみ存在し、プロジェクト間で重複しない（基礎と型）
2. **Reproducible Builds（再現可能なビルド）** — SDKバージョンとパッケージバージョンを固定し、すべての環境で同一の出力を生成（基礎と型）
3. **Human-Readable Configuration（人間が読める設定）** — .slnx XMLとDirectory.Build.propsが暗号的なGUIDや分散した設定を置き換える（温故知新）
4. **Progressive Modernization（段階的な近代化）** — ソリューション → ビルドプロパティ → パッケージ → SourceLink → バージョニング → SDKと一つずつ移行（継続は力）
5. **Debuggability by Default（デフォルトでデバッグ可能）** — SourceLinkとシンボルパッケージをすべてのNuGetパッケージに同梱しステップスルーデバッグを実現（成長の複利）

---

## Workflow: Set Up Modern .NET Project

### Step 1 — .slnx 形式への移行

.NET 9 で導入されたモダンな XML ベースの .slnx 形式に既存の .sln ソリューションを変換するときに使用します。

**バージョン要件:**

| ツール | 最低バージョン |
|--------|---------------|
| .NET SDK | 9.0.200 |
| Visual Studio | 17.13 |

**既存ソリューションの移行:**

```bash
# 特定のソリューションファイルを移行
dotnet sln MySolution.sln migrate

# ディレクトリに .sln が1つだけの場合
dotnet sln migrate
```

**新規 .slnx ソリューションの作成:**

```bash
# .NET 10+: デフォルトで .slnx を作成
dotnet new sln --name MySolution

# .NET 9: 形式を明示的に指定
dotnet new sln --name MySolution --format slnx

# プロジェクトを追加
dotnet sln add src/MyApp/MyApp.csproj
```

**.slnx ファイルの例:**

```xml
<Solution>
  <Folder Name="/build/">
    <File Path="Directory.Build.props" />
    <File Path="Directory.Packages.props" />
    <File Path="global.json" />
  </Folder>
  <Folder Name="/src/">
    <Project Path="src/MyApp/MyApp.csproj" />
  </Folder>
  <Folder Name="/tests/">
    <Project Path="tests/MyApp.Tests/MyApp.Tests.csproj" />
  </Folder>
</Solution>
```

**なぜ .slnx か**: ランダムなGUIDがなく、プルリクエストでクリーンなXML差分が可能。任意のテキストエディタで編集可能。.NET 10 からは `dotnet new sln` がデフォルトで `.slnx` を生成します。

⚠️ **重要**: 移行後は古い `.sln` を削除してください。両方を残すとソリューション自動検出に問題が発生します。

> **Values**: 温故知新（モダンな形式がレガシー規約を置き換える） / 基礎と型

### Step 2 — Directory.Build.props の設定

ソリューションツリー内のすべてのプロジェクトに適用されるビルドプロパティを集約するときに使用します。

`Directory.Build.props` をソリューションルートに配置します。すべてのプロジェクトがこれらの設定を自動的に継承します。

```xml
<Project>
  <!-- メタデータ -->
  <PropertyGroup>
    <Authors>Your Team</Authors>
    <Company>Your Company</Company>
    <!-- 動的著作権年 — ビルド時に自動更新 -->
    <Copyright>Copyright © 2020-$([System.DateTime]::Now.Year) Your Company</Copyright>
    <RepositoryUrl>https://github.com/yourorg/yourrepo</RepositoryUrl>
    <PackageLicenseExpression>Apache-2.0</PackageLicenseExpression>
  </PropertyGroup>

  <!-- C# 言語設定 -->
  <PropertyGroup>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>

  <!-- バージョン管理 -->
  <PropertyGroup>
    <VersionPrefix>1.0.0</VersionPrefix>
    <PackageReleaseNotes>See RELEASE_NOTES.md</PackageReleaseNotes>
  </PropertyGroup>

  <!-- 再利用可能なターゲットフレームワークプロパティ -->
  <PropertyGroup>
    <NetLibVersion>net8.0</NetLibVersion>
    <NetTestVersion>net9.0</NetTestVersion>
  </PropertyGroup>
</Project>
```

**再利用可能なフレームワークプロパティの理由**: `<NetLibVersion>` を一度定義し、すべての `.csproj` で `$(NetLibVersion)` を参照します。ターゲットフレームワークのアップグレードは1行の変更で完了します。

**動的著作権の理由**: `$([System.DateTime]::Now.Year)` がビルド時に現在の年を挿入 — 手動更新は不要です。

> **Values**: 基礎と型（一度集約し、どこからでも参照） / 成長の複利

### Step 3 — Central Package Management のセットアップ

すべての NuGet パッケージバージョンを単一の Directory.Packages.props ファイルに統合するときに使用します。

ソリューションルートに `Directory.Packages.props` を作成：

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <PropertyGroup>
    <AkkaVersion>1.5.35</AkkaVersion>
  </PropertyGroup>

  <ItemGroup Label="App Dependencies">
    <PackageVersion Include="Akka" Version="$(AkkaVersion)" />
    <PackageVersion Include="Akka.Cluster" Version="$(AkkaVersion)" />
    <PackageVersion Include="Microsoft.Extensions.Hosting" Version="9.0.0" />
  </ItemGroup>

  <ItemGroup Label="Test Dependencies">
    <PackageVersion Include="xunit" Version="2.9.3" />
    <PackageVersion Include="FluentAssertions" Version="7.0.0" />
    <PackageVersion Include="Microsoft.NET.Test.Sdk" Version="17.12.0" />
  </ItemGroup>
</Project>
```

**パッケージの使用** — `.csproj` にバージョン属性は不要：

```xml
<!-- MyApp.csproj 内 -->
<ItemGroup>
  <PackageReference Include="Akka" />
  <PackageReference Include="Microsoft.Extensions.Hosting" />
</ItemGroup>
```

**なぜ CPM か**: プロジェクト間のバージョンドリフトを排除し、関連パッケージをバージョン変数でグループ化し、依存関係の更新を1行の変更にします。

> **Values**: 基礎と型（バージョンの単一の信頼できる情報源） / ニュートラル

### Step 4 — SourceLink の設定

公開 NuGet パッケージのステップスルーデバッグを有効にするときに使用します。

`Directory.Build.props` に SourceLink 設定を追加：

```xml
<!-- SourceLink 設定 -->
<PropertyGroup>
  <PublishRepositoryUrl>true</PublishRepositoryUrl>
  <EmbedUntrackedSources>true</EmbedUntrackedSources>
  <IncludeSymbols>true</IncludeSymbols>
  <SymbolPackageFormat>snupkg</SymbolPackageFormat>
</PropertyGroup>

<ItemGroup>
  <!-- ソースコントロールに合ったプロバイダーを選択 -->
  <PackageReference Include="Microsoft.SourceLink.GitHub" PrivateAssets="All" />
  <!-- または: Microsoft.SourceLink.AzureRepos.Git -->
  <!-- または: Microsoft.SourceLink.GitLab -->
</ItemGroup>

<!-- NuGet パッケージアセット -->
<ItemGroup>
  <None Include="$(MSBuildThisFileDirectory)README.md" Pack="true" PackagePath="\" />
</ItemGroup>

<PropertyGroup>
  <PackageReadmeFile>README.md</PackageReadmeFile>
</PropertyGroup>
```

**なぜ SourceLink か**: 利用者がリポジトリをダウンロードせずにライブラリのソースコードにステップインしてデバッグできます。シンボルパッケージ（`.snupkg`）は NuGet.org に自動的にアップロードされます。

> **Values**: 成長の複利（デバッグ体験が利用者全体に複利的に波及） / 基礎と型

### Step 5 — バージョン管理のセットアップ

ビルドプロセスで RELEASE_NOTES.md を解析してバージョン更新を自動化するときに使用します。

**RELEASE_NOTES.md 形式:**

```markdown
#### 1.2.0 January 15th 2025 ####

- Added new feature X
- Fixed bug in Y

#### 1.1.0 December 10th 2024 ####

- Initial release
```

**ビルドスクリプト**が最新バージョンを解析し `Directory.Build.props` を更新：

```powershell
# build.ps1 — リリースノートを解析してVersionPrefixを更新
$content = Get-Content -Path "RELEASE_NOTES.md" -Raw
$sections = $content -split "####"
$version = ($sections[1].Trim() -split " ", 2)[0]

$xml = New-Object XML
$xml.Load("Directory.Build.props")
$xml.SelectSingleNode("//VersionPrefix").InnerText = $version
$xml.Save("Directory.Build.props")
Write-Output "Updated to version $version"
```

**CI/CD 統合**（GitHub Actions）:

```yaml
- name: Update version
  shell: pwsh
  run: ./build.ps1

- name: Pack
  run: dotnet pack -c Release /p:PackageVersion=${{ github.ref_name }}
```

**なぜ RELEASE_NOTES.md か**: バージョンソースを兼ねる人間が読める変更履歴。開発者がMarkdownファイルを1つ更新すれば、ビルドスクリプトが残りを処理します。

完全なモジュール化された PowerShell スクリプト（`getReleaseNotes.ps1`、`bumpVersion.ps1`）は `references/advanced-examples.md` を参照してください。

> **Values**: 継続は力（リリースノートがプロジェクト履歴を蓄積） / 余白の設計

### Step 6 — global.json で SDK を固定

すべての開発者と CI 環境が同じ .NET SDK バージョンを使用することを保証するときに使用します。

```json
{
  "sdk": {
    "version": "9.0.200",
    "rollForward": "latestFeature"
  }
}
```

**ロールフォワードポリシー:**

| ポリシー | 動作 | ユースケース |
|----------|------|-------------|
| `disable` | 正確なバージョンが必要 | 厳密な再現性 |
| `patch` | 同じmajor.minor、最新パッチ | セキュリティ修正のみ |
| `latestFeature` | 同じmajor、最新フィーチャーバンド | ✅ 推奨デフォルト |
| `major` | 利用可能な最新SDK | 非推奨 |

**なぜ `latestFeature` か**: メジャーSDKアップグレードによる破壊的変更を防ぎつつ、セキュリティ修正のための自動パッチ更新を許可します。

> **Values**: 基礎と型（SDK固定が環境ドリフトを防止） / ニュートラル

---

## Good Practices

### 1. 関連パッケージにバージョン変数を使用

**What**: `Directory.Packages.props` で関連する NuGet パッケージを単一のバージョン変数でグループ化します。

**Why**: 同期を保つ必要があるパッケージ間のバージョン不一致を防ぎます（例：すべての Akka パッケージを同じバージョンに）。

**Values**: 基礎と型（構造的制約としてのバージョン整合性）

### 2. NuGet.Config でパッケージソースをクリア

**What**: パッケージソースを定義する前に `<clear />` を使用して継承されたデフォルトを削除します。

**Why**: マシンレベルの NuGet 設定に関係なく、再現可能なリストアを保証します。

**Values**: ニュートラル（環境に依存しないビルド）

### 3. 再利用可能なターゲットフレームワークプロパティを定義

**What**: `<NetLibVersion>net8.0</NetLibVersion>` のようなプロパティを作成し、`.csproj` ファイルで `$(NetLibVersion)` を参照します。

**Why**: すべてのプロジェクトのターゲットフレームワークのアップグレードが `Directory.Build.props` の1行変更で済みます。

**Values**: 成長の複利（1つの変更がすべてのプロジェクトに伝播）

---

## Common Pitfalls

### 1. .sln と .slnx の両方を残す

**Problem**: 移行後にリポジトリに両方のファイルが存在し、ツールの混乱を招きます。

**Solution**: `dotnet sln migrate` 実行後、直ちに古い `.sln` ファイルを削除してください。

```bash
# ❌ WRONG — 両方のファイルが共存
# MySolution.sln + MySolution.slnx が同じディレクトリに

# ✅ CORRECT — .slnx のみが残る
dotnet sln MySolution.sln migrate
Remove-Item MySolution.sln
```

### 2. CPM 有効時に .csproj でバージョンを指定

**Problem**: Central Package Management が有効なときに `<PackageReference>` に `Version="x.y.z"` を追加するとビルドエラーになります。

**Solution**: すべての `.csproj` の `<PackageReference>` 要素から `Version` 属性を削除してください。

```xml
<!-- ❌ WRONG — バージョンが CPM と競合 -->
<PackageReference Include="Akka" Version="1.5.35" />

<!-- ✅ CORRECT — バージョンは一元管理 -->
<PackageReference Include="Akka" />
```

### 3. リポジトリルートに global.json がない

**Problem**: 異なる開発者が異なるSDKバージョンを使用し、ビルド動作が不整合になります。

**Solution**: 固定SDKバージョンと `rollForward` ポリシーを持つ `global.json` を常にリポジトリルートにコミットしてください。

---

## Anti-Patterns

### ビルドプロパティを .csproj ファイルに分散

**What**: `<LangVersion>`、`<Nullable>`、メタデータをすべての `.csproj` ファイルに複製。

**Why It's Wrong**: 変更にすべてのプロジェクトファイルの編集が必要。プロパティが時間とともに乖離。マージコンフリクトの表面積が増加。

**Better Approach**: ソリューションルートの `Directory.Build.props` で共有プロパティを一度だけ定義。

### Directory.Build.props にバージョン番号をハードコーディング

**What**: RELEASE_NOTES.md からの自動化ではなく、リリースごとに `<VersionPrefix>` を手動編集。

**Why It's Wrong**: エラーが起きやすく、忘れやすい。バージョンとチェンジログが非同期になる可能性。

**Better Approach**: `RELEASE_NOTES.md` を解析して `Directory.Build.props` を自動更新するビルドスクリプトを使用。

---

## Quick Reference

### プロジェクト構造概要

```
MySolution/
├── Directory.Build.props           # 集約ビルド設定
├── Directory.Packages.props        # 一元パッケージバージョン
├── MySolution.slnx                 # モダンソリューションファイル
├── global.json                     # SDKバージョン固定
├── NuGet.Config                    # パッケージソース設定
├── build.ps1                       # ビルドオーケストレーション
├── RELEASE_NOTES.md                # バージョン履歴
├── src/
│   └── MyApp/MyApp.csproj
└── tests/
    └── MyApp.Tests/MyApp.Tests.csproj
```

### ファイル判断テーブル

| ファイル | 目的 | 作成タイミング |
|----------|------|---------------|
| `MySolution.slnx` | モダンXMLソリューションファイル | 常に — .sln を置き換え |
| `Directory.Build.props` | 共有ビルドプロパティ | 常に — メタデータと設定を集約 |
| `Directory.Packages.props` | 一元NuGetバージョン | 2つ以上のプロジェクトがパッケージ共有時 |
| `global.json` | SDKバージョン固定 | 常に — 再現可能なビルドを保証 |
| `NuGet.Config` | パッケージソース設定 | `<clear />` またはプライベートフィード使用時 |
| `RELEASE_NOTES.md` | バージョン変更履歴 | NuGetパッケージ公開時 |

---

## Resources

- [.slnx 形式ドキュメント](https://learn.microsoft.com/ja-jp/visualstudio/ide/solution-file) — モダンソリューション形式リファレンス
- [Central Package Management](https://learn.microsoft.com/ja-jp/nuget/consume-packages/central-package-management) — NuGet CPM ドキュメント
- [SourceLink](https://learn.microsoft.com/ja-jp/dotnet/standard/library-guidance/sourcelink) — ソースデバッグ設定
- [global.json 概要](https://learn.microsoft.com/ja-jp/dotnet/core/tools/global-json) — SDKバージョン固定リファレンス
- 完全な PowerShell バージョン管理スクリプトと NuGet.Config テンプレートは `references/advanced-examples.md` を参照

<!-- 英語版は ../SKILL.md を参照してください -->
