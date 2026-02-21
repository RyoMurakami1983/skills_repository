---
name: dotnet-playwright-ci-caching
description: >
  Cache Playwright browser binaries in CI/CD pipelines (GitHub Actions, Azure DevOps)
  to eliminate 1-2 minute download overhead on every build. Uses version-based cache keys
  derived from Central Package Management (CPM) for automatic invalidation.
  Use when setting up or optimizing CI/CD for .NET projects with Playwright E2E tests.
metadata:
  author: RyoMurakami1983
  tags: [playwright, ci-cd, caching, github-actions, azure-devops, dotnet, performance]
  invocable: false
---

# Caching Playwright Browsers in CI/CD

A concise guardrail for caching Playwright browser binaries (~400MB) in CI/CD pipelines to avoid redundant downloads. Targets .NET projects using Central Package Management (CPM) with GitHub Actions or Azure DevOps.

**Acronyms**: CI/CD (Continuous Integration/Continuous Delivery), CPM (Central Package Management), E2E (End-to-End).

## When to Use This Skill

- Setting up CI/CD pipelines for .NET projects with Playwright end-to-end tests
- Reducing build times caused by repeated Playwright browser downloads (~400MB)
- Implementing automatic cache invalidation when Playwright package version changes
- Configuring GitHub Actions workflows to cache Playwright browser binaries efficiently
- Adapting Azure DevOps pipelines to avoid redundant browser installation on every run
- Creating cross-platform CI caching that works on Linux, macOS, and Windows runners
- Debugging cache misses caused by version mismatch between SDK and cached browsers

## Related Skills

| Skill | Scope | When |
|-------|-------|------|
| `dotnet-playwright-blazor` | Writing Playwright tests for Blazor apps | Creating E2E tests that this caching accelerates |
| `dotnet-project-structure` | Central Package Management setup | Defining `Directory.Packages.props` for version extraction |

## Core Principles

1. **Version-Based Cache Keys** — Use the Playwright NuGet version from `Directory.Packages.props` as cache key. Why: automatic invalidation on package upgrade without manual key bumping.
2. **Conditional Install** — Only download browsers on cache miss. Why: skipping install on cache hit saves 1-2 minutes per build.
3. **OS-Aware Cache Paths** — Use platform-specific paths for browser storage. Why: each OS stores Playwright browsers in a different location.
4. **Abstracted CLI Discovery** — Use a helper script to locate the Playwright CLI. Why: the CLI path varies by project structure, .NET version, and OS.

> **Values**: 基礎と型の追求（バージョンキー・条件付きインストール・OS 別パスという「型」を守ることで、再現可能で高速な CI パイプラインの基盤を築く）, 継続は力（CI キャッシュの最適化をコツコツ積み重ね、毎ビルド 1-2 分の時間節約を複利的に積み上げる）

## Workflow: Cache Playwright Browsers in CI/CD

### Step 1: Extract Playwright Version from CPM

Read the Playwright NuGet package version from `Directory.Packages.props` and export it as an environment variable. Why: this version becomes the cache key, ensuring automatic invalidation on upgrades.

**Prerequisites:**

- **Central Package Management (CPM)** enabled with `Directory.Packages.props`
- **PowerShell** available on CI agents (pre-installed on GitHub Actions and Azure DevOps)

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
    # Extract version from CPM for cache key
    [xml]$props = Get-Content "Directory.Packages.props"
    $version = $props.Project.ItemGroup.PackageVersion |
      Where-Object { $_.Include -eq "Microsoft.Playwright" } |
      Select-Object -ExpandProperty Version
    echo "PlaywrightVersion=$version" >> $env:GITHUB_ENV
```

> **Values**: 基礎と型の追求（CPM からバージョンを自動取得する「型」を確立し、手動キー管理を不要にする）

### Step 2: Configure Cache Action

Configure the CI cache action with the Playwright version in the key and OS-appropriate paths. Why: version-based keys ensure automatic cache invalidation on Playwright upgrades.

**Cache paths by OS:**

| OS | Path | Runner |
|----|------|--------|
| Linux | `~/.cache/ms-playwright` | `ubuntu-latest` |
| macOS | `~/Library/Caches/ms-playwright` | `macos-latest` |
| Windows | `%USERPROFILE%\AppData\Local\ms-playwright` | `windows-latest` |

**GitHub Actions (single OS):**

```yaml
- name: Cache Playwright Browsers
  id: playwright-cache
  uses: actions/cache@v4
  with:
    path: ~/.cache/ms-playwright
    key: ${{ runner.os }}-playwright-${{ env.PlaywrightVersion }}
```

**GitHub Actions (multi-OS matrix):**

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

Install browsers only when the cache is not hit. Why: skipping redundant downloads saves ~1-2 minutes and avoids transient network failures.

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

Create `build/playwright.ps1` to discover and run the Playwright CLI. Why: the CLI location varies by project structure, .NET version, and operating system.

```powershell
# build/playwright.ps1
# Discovers Microsoft.Playwright.dll and runs the bundled CLI

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

# Find DLL after dotnet build/restore
$playwrightDll = Get-ChildItem -Path . -Recurse `
    -Filter "Microsoft.Playwright.dll" -ErrorAction SilentlyContinue |
    Select-Object -First 1

if (-not $playwrightDll) {
    Write-Error "Microsoft.Playwright.dll not found. Run 'dotnet build' first."
    exit 1
}

$playwrightDir = $playwrightDll.DirectoryName

# Find CLI — try Windows .cmd first, then Unix executable
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

**Usage examples:**

```bash
# Install all browsers with dependencies
./build/playwright.ps1 install --with-deps

# Install specific browser only
./build/playwright.ps1 install chromium

# Dry run to check installed browsers
./build/playwright.ps1 install --dry-run
```

> **Values**: 成長の複利（ヘルパースクリプトという再利用可能な型を一度作成することで、全プロジェクトの CI 設定が加速する）

### Step 5: Adapt for Azure DevOps

Translate the pattern to Azure DevOps using `task` YAML syntax. Why: Azure DevOps uses different cache and script task formats than GitHub Actions.

```yaml
- task: PowerShell@2
  displayName: 'Get Playwright Version'
  inputs:
    targetType: 'inline'
    script: |
      # Extract version for cache key
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

- Use Central Package Management (CPM) to keep Playwright version in a single source of truth
- Implement the helper script to abstract CLI discovery across platforms and .NET versions
- Consider multi-OS matrix builds with OS-specific cache paths for comprehensive coverage
- Apply cache key naming convention: `<runner-os>-playwright-<version>` for clarity
- Use `--with-deps` flag to install system-level dependencies alongside browsers
- Implement `dotnet build` before running `playwright.ps1` to ensure DLLs exist
- Use `actions/cache@v4` (latest) for improved performance and reliability

## Common Pitfalls

1. **Hardcoded Cache Key** — Using `playwright-browsers-v1` instead of version-based key. Fix: include the Playwright NuGet version in the cache key for automatic invalidation on upgrades.
2. **Missing DLL on First Run** — Running `playwright.ps1` before `dotnet build`. Fix: always run `dotnet restore` or `dotnet build` before the helper script to ensure the DLL exists.
3. **Wrong Cache Path for OS** — Using Linux path on Windows runner or vice versa. Fix: implement multi-path cache configuration or select the correct path per runner OS.
4. **Silent Version Extraction Failure** — PowerShell script succeeds but outputs empty version. Fix: add error checking to verify the extracted version is not empty before setting the cache key.
5. **Stale Browser Binaries After Upgrade** — Cache hit returns old browsers that don't match the new SDK version. Fix: ensure the Playwright NuGet version is in the cache key, not a static string.

## Anti-Patterns

### ❌ Hardcoded Cache Key → ✅ Version-Based Key

```yaml
# ❌ BAD — requires manual bump on every Playwright upgrade
key: playwright-browsers-v1

# ✅ GOOD — automatic invalidation on version change
key: ${{ runner.os }}-playwright-${{ env.PlaywrightVersion }}
```

### ❌ Always Install Browsers → ✅ Conditional Install

```yaml
# ❌ BAD — downloads 400MB on every build
- name: Install Playwright Browsers
  run: ./build/playwright.ps1 install --with-deps

# ✅ GOOD — skips download when cache hit
- name: Install Playwright Browsers
  if: steps.playwright-cache.outputs.cache-hit != 'true'
  run: ./build/playwright.ps1 install --with-deps
```

### ❌ Fixed Cache Path → ✅ OS-Aware Path

```yaml
# ❌ BAD — fails on macOS and Windows runners
path: ~/.cache/ms-playwright

# ✅ GOOD — covers all OS variants in matrix builds
path: |
  ~/.cache/ms-playwright
  ~/Library/Caches/ms-playwright
  ~/AppData/Local/ms-playwright
```

## Quick Reference

### Cache Configuration Decision Table

| Scenario | Cache Key | Path | Condition |
|----------|-----------|------|-----------|
| Single Linux runner | `Linux-playwright-1.40.0` | `~/.cache/ms-playwright` | `cache-hit != 'true'` |
| Multi-OS matrix | `<OS>-playwright-<ver>` | All three OS paths | `cache-hit != 'true'` |
| Azure DevOps Linux | `playwright \| "Linux" \| 1.40.0` | `$(HOME)/.cache/ms-playwright` | `PlaywrightCacheHit != 'true'` |

### Troubleshooting Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Cache never used | Version extraction failed silently | Verify PowerShell outputs correct version |
| Browser not found after cache hit | Stale cache from old version | Ensure version is in cache key |
| playwright.ps1 can't find DLL | Build step skipped | Run `dotnet build` before playwright.ps1 |
| Cache key mismatch across runs | `Directory.Packages.props` missing | Ensure CPM file exists at repo root |
| Multi-OS cache collision | Same key for different OS | Include `runner.os` in cache key |

## Resources

- [actions/cache documentation](https://github.com/actions/cache)
- [Playwright .NET Documentation](https://playwright.dev/dotnet/)
- [Azure DevOps Pipeline Caching](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/caching)
- [Central Package Management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management)
- [petabridge/geekedin](https://github.com/petabridge/geekedin) — Production reference implementation
- [petabridge/DrawTogether.NET](https://github.com/petabridge/DrawTogether.NET) — Production reference implementation
