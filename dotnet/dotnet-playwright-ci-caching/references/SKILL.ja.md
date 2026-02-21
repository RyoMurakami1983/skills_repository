---
name: dotnet-playwright-ci-caching
description: >
  CI/CD パイプライン（GitHub Actions、Azure DevOps）で Playwright ブラウザバイナリを
  キャッシュし、毎ビルド 1-2 分のダウンロードオーバーヘッドを排除する。Central Package
  Management (CPM) からバージョンベースのキャッシュキーを導出し自動無効化を実現。
  Use when .NET プロジェクトの Playwright E2E テスト用 CI/CD を構築・最適化する際に使用。
metadata:
  author: RyoMurakami1983
  tags: [playwright, ci-cd, caching, github-actions, azure-devops, dotnet, performance]
  invocable: false
---

<!-- このドキュメントは dotnet-playwright-ci-caching の日本語版です。英語版: ../SKILL.md -->

# Caching Playwright Browsers in CI/CD

CI/CD パイプラインで Playwright ブラウザバイナリ（~400MB）をキャッシュし、冗長なダウンロードを回避するための簡潔なガードレール。Central Package Management (CPM) を使用する .NET プロジェクトで GitHub Actions または Azure DevOps を対象とする。

**略語**: CI/CD（Continuous Integration/Continuous Delivery）、CPM（Central Package Management）、E2E（End-to-End）。

## When to Use This Skill

- .NET プロジェクトの Playwright エンドツーエンドテスト用 CI/CD パイプラインを構築する
- Playwright ブラウザの繰り返しダウンロード（~400MB）によるビルド時間の増大を削減する
- Playwright パッケージバージョン変更時の自動キャッシュ無効化を実装する
- GitHub Actions ワークフローで Playwright ブラウザバイナリを効率的にキャッシュ設定する
- Azure DevOps パイプラインで毎回のブラウザインストールを回避するよう適応する
- Linux、macOS、Windows ランナーで動作するクロスプラットフォーム CI キャッシュを作成する
- SDK とキャッシュされたブラウザ間のバージョン不一致によるキャッシュミスをデバッグする

## Related Skills

| Skill | Scope | When |
|-------|-------|------|
| `dotnet-playwright-blazor` | Blazor アプリの Playwright テスト作成 | このキャッシュが加速する E2E テストの作成時 |
| `dotnet-project-structure` | Central Package Management 設定 | バージョン抽出用 `Directory.Packages.props` の定義時 |

## Core Principles

1. **Version-Based Cache Keys** — `Directory.Packages.props` の Playwright NuGet バージョンをキャッシュキーとして使用する。パッケージアップグレード時に手動キー変更なしで自動無効化されるため。
2. **Conditional Install** — キャッシュミス時のみブラウザをダウンロードする。キャッシュヒット時にインストールをスキップすることで、ビルドあたり 1-2 分節約するため。
3. **OS-Aware Cache Paths** — ブラウザ保存にプラットフォーム固有のパスを使用する。各 OS が Playwright ブラウザを異なる場所に格納するため。
4. **Abstracted CLI Discovery** — ヘルパースクリプトで Playwright CLI を検出する。CLI パスがプロジェクト構造、.NET バージョン、OS によって異なるため。

> **Values**: 基礎と型の追求（バージョンキー・条件付きインストール・OS 別パスという「型」を守ることで、再現可能で高速な CI パイプラインの基盤を築く）, 継続は力（CI キャッシュの最適化をコツコツ積み重ね、毎ビルド 1-2 分の時間節約を複利的に積み上げる）

## Workflow: Cache Playwright Browsers in CI/CD

### Step 1: Extract Playwright Version from CPM

`Directory.Packages.props` から Playwright NuGet パッケージバージョンを読み取り、環境変数としてエクスポートする。このバージョンがキャッシュキーとなり、アップグレード時の自動無効化を保証するため。

**前提条件:**

- **Central Package Management (CPM)** が `Directory.Packages.props` で有効化されていること
- **PowerShell** が CI エージェントで使用可能であること（GitHub Actions と Azure DevOps にプリインストール済み）

```xml
<!-- Directory.Packages.props -->
<Project>
  <ItemGroup>
    <PackageVersion Include="Microsoft.Playwright" Version="1.40.0" />
  </ItemGroup>
</Project>
```

**GitHub Actions:**

```yaml
- name: Get Playwright Version
  shell: pwsh
  run: |
    # CPM からキャッシュキー用バージョンを抽出
    [xml]$props = Get-Content "Directory.Packages.props"
    $version = $props.Project.ItemGroup.PackageVersion |
      Where-Object { $_.Include -eq "Microsoft.Playwright" } |
      Select-Object -ExpandProperty Version
    echo "PlaywrightVersion=$version" >> $env:GITHUB_ENV
```

> **Values**: 基礎と型の追求（CPM からバージョンを自動取得する「型」を確立し、手動キー管理を不要にする）

### Step 2: Configure Cache Action

CI キャッシュアクションにバージョンをキーとして、OS に適したパスを設定する。バージョンベースのキーにより、Playwright アップグレード時の自動キャッシュ無効化を保証するため。

**OS 別キャッシュパス:**

| OS | Path | Runner |
|----|------|--------|
| Linux | `~/.cache/ms-playwright` | `ubuntu-latest` |
| macOS | `~/Library/Caches/ms-playwright` | `macos-latest` |
| Windows | `%USERPROFILE%\AppData\Local\ms-playwright` | `windows-latest` |

**GitHub Actions（単一 OS）:**

```yaml
- name: Cache Playwright Browsers
  id: playwright-cache
  uses: actions/cache@v4
  with:
    path: ~/.cache/ms-playwright
    key: ${{ runner.os }}-playwright-${{ env.PlaywrightVersion }}
```

**GitHub Actions（マルチ OS マトリクス）:**

```yaml
- name: Cache Playwright Browsers
  id: playwright-cache
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/ms-playwright
      ~/Library/Caches/ms-playwright
      ~/AppData/Local/ms-playwright
    key: ${{ runner.os }}-playwright-${{ env.PlaywrightVersion }}
```

> **Values**: 温故知新（各 OS のキャッシュパスという基本知識を活かし、最新の actions/cache@v4 API と組み合わせる）

### Step 3: Conditional Browser Install

キャッシュがヒットしない場合のみブラウザをインストールする。冗長なダウンロードをスキップすることで ~1-2 分を節約し、一時的なネットワーク障害を回避するため。

**GitHub Actions:**

```yaml
- name: Install Playwright Browsers
  if: steps.playwright-cache.outputs.cache-hit != 'true'
  shell: pwsh
  run: ./build/playwright.ps1 install --with-deps
```

**Azure DevOps:**

```yaml
- task: PowerShell@2
  displayName: 'Install Playwright Browsers'
  condition: ne(variables['PlaywrightCacheHit'], 'true')
  inputs:
    filePath: 'build/playwright.ps1'
    arguments: 'install --with-deps'
```

> **Values**: 余白の設計（キャッシュヒット時にインストールをスキップすることで、ビルド時間に余白を生み出す）

### Step 4: Create Playwright Helper Script

Playwright CLI を検出・実行する `build/playwright.ps1` を作成する。CLI の場所がプロジェクト構造、.NET バージョン、OS によって異なるため。

```powershell
# build/playwright.ps1
# Microsoft.Playwright.dll を検出し、バンドルされた CLI を実行

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

# dotnet build/restore 後に DLL を検索
$playwrightDll = Get-ChildItem -Path . -Recurse `
    -Filter "Microsoft.Playwright.dll" -ErrorAction SilentlyContinue |
    Select-Object -First 1

if (-not $playwrightDll) {
    Write-Error "Microsoft.Playwright.dll not found. Run 'dotnet build' first."
    exit 1
}

$playwrightDir = $playwrightDll.DirectoryName

# CLI 検索 — Windows .cmd を優先、次に Unix 実行ファイル
$playwrightCmd = Get-ChildItem -Path "$playwrightDir/.playwright/node" `
    -Recurse -Filter "playwright.cmd" -ErrorAction SilentlyContinue |
    Select-Object -First 1

if (-not $playwrightCmd) {
    $playwrightCmd = Get-ChildItem -Path "$playwrightDir/.playwright/node" `
        -Recurse -Filter "playwright" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq "playwright" } |
        Select-Object -First 1
}

if (-not $playwrightCmd) {
    Write-Error "Playwright CLI not found in $playwrightDir/.playwright/node"
    exit 1
}

Write-Host "Using Playwright CLI: $($playwrightCmd.FullName)"
& $playwrightCmd.FullName @Arguments
```

**使用例:**

```bash
# 全ブラウザと依存関係をインストール
./build/playwright.ps1 install --with-deps

# 特定のブラウザのみインストール
./build/playwright.ps1 install chromium

# ドライランでインストール済みブラウザを確認
./build/playwright.ps1 install --dry-run
```

> **Values**: 成長の複利（ヘルパースクリプトという再利用可能な型を一度作成することで、全プロジェクトの CI 設定が加速する）

### Step 5: Adapt for Azure DevOps

`task` YAML 構文を使用してパターンを Azure DevOps に適用する。Azure DevOps は GitHub Actions と異なるキャッシュおよびスクリプトタスク形式を使用するため。

```yaml
- task: PowerShell@2
  displayName: 'Get Playwright Version'
  inputs:
    targetType: 'inline'
    script: |
      # キャッシュキー用バージョンを抽出
      [xml]$props = Get-Content "Directory.Packages.props"
      $version = $props.Project.ItemGroup.PackageVersion |
        Where-Object { $_.Include -eq "Microsoft.Playwright" } |
        Select-Object -ExpandProperty Version
      Write-Host "##vso[task.setvariable variable=PlaywrightVersion]$version"

- task: Cache@2
  displayName: 'Cache Playwright Browsers'
  inputs:
    key: 'playwright | "$(Agent.OS)" | $(PlaywrightVersion)'
    path: '$(HOME)/.cache/ms-playwright'
    cacheHitVar: 'PlaywrightCacheHit'
```

> **Values**: ニュートラルな視点（GitHub Actions と Azure DevOps の両方をカバーし、偏りのない普遍的なパターンを提供する）

## Good Practices

- Use Central Package Management (CPM) で Playwright バージョンを単一の信頼できる情報源に保つ
- Implement ヘルパースクリプトでプラットフォームと .NET バージョン間の CLI 検出を抽象化する
- Consider マルチ OS マトリクスビルドで OS 固有のキャッシュパスを使い包括的なカバレッジを確保する
- Apply キャッシュキー命名規約: `<runner-os>-playwright-<version>` で明確性を確保する
- Use `--with-deps` フラグでブラウザと共にシステムレベルの依存関係をインストールする
- Implement `playwright.ps1` 実行前に `dotnet build` を行い DLL の存在を保証する
- Use `actions/cache@v4`（最新版）で改善されたパフォーマンスと信頼性を確保する

## Common Pitfalls

1. **Hardcoded Cache Key** — バージョンベースキーの代わりに `playwright-browsers-v1` を使用。Fix: アップグレード時の自動無効化のため、Playwright NuGet バージョンをキャッシュキーに含める。
2. **Missing DLL on First Run** — `dotnet build` 前に `playwright.ps1` を実行。Fix: DLL の存在を保証するため、ヘルパースクリプト前に必ず `dotnet restore` または `dotnet build` を実行する。
3. **Wrong Cache Path for OS** — Windows ランナーで Linux パスを使用、またはその逆。Fix: マルチパスキャッシュ設定を実装するか、ランナー OS ごとに正しいパスを選択する。
4. **Silent Version Extraction Failure** — PowerShell スクリプトは成功するが空のバージョンを出力。Fix: キャッシュキー設定前に抽出されたバージョンが空でないことを検証するエラーチェックを追加する。
5. **Stale Browser Binaries After Upgrade** — キャッシュヒットが新しい SDK と一致しない古いブラウザを返す。Fix: 静的文字列ではなく Playwright NuGet バージョンをキャッシュキーに含めることを確認する。

## Anti-Patterns

### ❌ Hardcoded Cache Key → ✅ Version-Based Key

```yaml
# ❌ BAD — Playwright アップグレードのたびに手動変更が必要
key: playwright-browsers-v1

# ✅ GOOD — バージョン変更時に自動無効化
key: ${{ runner.os }}-playwright-${{ env.PlaywrightVersion }}
```

### ❌ Always Install Browsers → ✅ Conditional Install

```yaml
# ❌ BAD — 毎ビルドで 400MB をダウンロード
- name: Install Playwright Browsers
  run: ./build/playwright.ps1 install --with-deps

# ✅ GOOD — キャッシュヒット時はダウンロードをスキップ
- name: Install Playwright Browsers
  if: steps.playwright-cache.outputs.cache-hit != 'true'
  run: ./build/playwright.ps1 install --with-deps
```

### ❌ Fixed Cache Path → ✅ OS-Aware Path

```yaml
# ❌ BAD — macOS と Windows ランナーで失敗
path: ~/.cache/ms-playwright

# ✅ GOOD — マトリクスビルドで全 OS バリアントをカバー
path: |
  ~/.cache/ms-playwright
  ~/Library/Caches/ms-playwright
  ~/AppData/Local/ms-playwright
```

## Quick Reference

### Cache Configuration Decision Table

| Scenario | Cache Key | Path | Condition |
|----------|-----------|------|-----------|
| 単一 Linux ランナー | `Linux-playwright-1.40.0` | `~/.cache/ms-playwright` | `cache-hit != 'true'` |
| マルチ OS マトリクス | `<OS>-playwright-<ver>` | 全 3 OS パス | `cache-hit != 'true'` |
| Azure DevOps Linux | `playwright \| "Linux" \| 1.40.0` | `$(HOME)/.cache/ms-playwright` | `PlaywrightCacheHit != 'true'` |

### Troubleshooting Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| キャッシュが使われない | バージョン抽出がサイレントに失敗 | PowerShell が正しいバージョンを出力するか確認 |
| キャッシュヒット後にブラウザが見つからない | 古いバージョンのキャッシュが残存 | バージョンがキャッシュキーに含まれていることを確認 |
| playwright.ps1 が DLL を見つけられない | ビルドステップがスキップされた | playwright.ps1 前に `dotnet build` を実行 |
| 実行間でキャッシュキーが不一致 | `Directory.Packages.props` が欠落 | CPM ファイルがリポジトリルートに存在することを確認 |
| マルチ OS キャッシュ衝突 | 異なる OS に同じキー | キャッシュキーに `runner.os` を含める |

## Resources

- [actions/cache documentation](https://github.com/actions/cache)
- [Playwright .NET Documentation](https://playwright.dev/dotnet/)
- [Azure DevOps Pipeline Caching](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/caching)
- [Central Package Management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management)
- [petabridge/geekedin](https://github.com/petabridge/geekedin) — 本番リファレンス実装
- [petabridge/DrawTogether.NET](https://github.com/petabridge/DrawTogether.NET) — 本番リファレンス実装
