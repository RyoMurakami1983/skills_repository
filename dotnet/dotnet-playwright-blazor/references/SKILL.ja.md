---
name: dotnet-playwright-blazor
description: >
  Blazor Server および WebAssembly アプリケーションのエンドツーエンド UI テストを
  Playwright で作成する。セットアップ、ナビゲーション、セレクタ、認証、エラー
  ハンドリング、CI 統合をカバー。
  Use when Blazor コンポーネント、フォーム、ユーザーワークフローを Playwright でテストする際に使用。
metadata:
  author: RyoMurakami1983
  tags: [playwright, blazor, testing, e2e, dotnet, ui-testing]
  invocable: false
---

<!-- このドキュメントは dotnet-playwright-blazor の日本語版です。英語版: ../SKILL.md -->

# Testing Blazor Applications with Playwright

Blazor Server および Blazor WebAssembly アプリケーションに対して Microsoft.Playwright を使用したエンドツーエンド UI テストを書くための簡潔なガードレール。.NET 8+ と xUnit または MSTest を対象とする。

**略語**: E2E（End-to-End）、SPA（Single-Page Application）、CI（Continuous Integration）。

## When to Use This Skill

- Blazor Server または WebAssembly アプリケーションページのエンドツーエンド UI テストを作成する
- インタラクティブな Blazor コンポーネント、EditForm、マルチステップユーザーワークフローをテストする
- Cookie ベースまたは OAuth 認証・認可リダイレクトフローを検証する
- ヘッドモードと Playwright Inspector ツールを使用して Blazor レンダリング問題をデバッグする
- デスクトップおよびモバイルビューポートでビジュアルリグレッションテスト用スクリーンショットを取得する
- Blazor アプリに対して Playwright テストを実行する GitHub Actions CI パイプラインを設定する
- エラーオーバーレイが表示されていないことをアサートして未処理の Blazor 例外を検出する

## Related Skills

| Skill | Scope | When |
|-------|-------|------|
| `dotnet-project-structure` | .NET ソリューションレイアウト、プロジェクト参照 | テストプロジェクトの配置を定義 |
| `dotnet-modern-csharp-coding-standards` | C# コーディングスタイル、async パターン | テストヘルパーコードを記述 |

## Core Principles

1. **Wait for DOM, Not Network** — Blazor はクライアントサイドルーティングで非同期レンダリングする。ネットワークアイドルではなく特定の DOM 要素を待機する。Blazor ナビゲーションは HTTP ロードを発生させないため。
2. **Use Test Attributes for Selectors** — Blazor コンポーネントに `data-test` または `data-testid` 属性を追加して安定したセレクタを確保する。CSS クラスや ID は UI リファクタリングで変更されるため。
3. **Always Check Blazor Error UI** — 重要なアクションの後は必ず `#blazor-error-ui` が表示されていないことをアサートする。未処理の例外はエラーオーバーレイでサイレントにレンダリングされるため。
4. **Headless by Default, Headed for Debug** — CI ではヘッドレスで実行し、ローカルデバッグでは SlowMo 付きのヘッドモードで実行する。ヘッドレスは高速で、ヘッドモードはタイミングとレンダリングの問題を明らかにするため。
5. **Pin Browser Channels** — 再現性のある結果のために特定のブラウザチャネル（msedge, chrome）を使用する。デフォルトの Chromium リビジョンは環境間で異なる可能性があるため。

> **Values**: 基礎と型の追求（DOM 待機・テスト属性・エラー UI チェックという「型」を守ることで、信頼性の高いテスト基盤を築く）, 温故知新（Playwright の最新 API を活かしつつ、Blazor の非同期レンダリングという基本特性を正しく理解する）

## Workflow: Test Blazor Applications with Playwright

### Step 1: Set Up Playwright Fixture

Playwright を初期化してブラウザを起動する共有テストフィクスチャを作成する。テスト全体で単一のブラウザインスタンスを再利用し、繰り返しの起動コストを回避するため。

**必要な NuGet パッケージ：**

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Playwright" Version="*" />
  <PackageReference Include="Microsoft.Playwright.MSTest" Version="*" />
  <!-- OR for xUnit -->
  <PackageReference Include="xunit" Version="*" />
  <PackageReference Include="xunit.runner.visualstudio" Version="*" />
</ItemGroup>
```

初回実行前にブラウザをインストール：

```bash
pwsh -Command "playwright install --with-deps"
```

**フィクスチャ実装：**

```csharp
using Microsoft.Playwright;

public class PlaywrightFixture : IAsyncLifetime
{
    private IPlaywright? _playwright;
    private IBrowser? _browser;

    public IBrowser Browser => _browser
        ?? throw new InvalidOperationException("Browser not initialized");

    public async Task InitializeAsync()
    {
        _playwright = await Playwright.CreateAsync();
        _browser = await _playwright.Chromium.LaunchAsync(new()
        {
            Headless = true,
            // SlowMo = 100 // デバッグ時にコメント解除
        });
    }

    public async Task DisposeAsync()
    {
        if (_browser is not null)
            await _browser.DisposeAsync();
        _playwright?.Dispose();
    }
}
```

> **Values**: 基礎と型の追求（Fixture という「型」でブラウザのライフサイクル管理を標準化し、テスト全体の安定性を確保する）

### Step 2: Navigate and Wait for Blazor Rendering

ネットワークアイドルの代わりに DOM ベースの待機戦略を使用する。Blazor SPA ナビゲーションはクライアントサイドであり、ページリロードを発生させないため。

```csharp
[Fact]
public async Task NavigateToCounter()
{
    var page = await _fixture.Browser.NewPageAsync();

    // 初回ロード — 通常の HTTP ナビゲーション
    await page.GotoAsync("https://localhost:5001");
    await page.WaitForSelectorAsync("h1:has-text('Welcome')");

    // アプリ内ナビゲーション — ページリロードなし
    await page.GetByRole(AriaRole.Link, new() { Name = "Counter" })
        .ClickAsync();
    await page.WaitForSelectorAsync("h1:has-text('Counter')");
}
```

**待機戦略の判断テーブル：**

| 戦略 | 使用場面 | 理由 |
|------|---------|------|
| `WaitForSelectorAsync` | 特定の要素の出現を待つ | Blazor に最も信頼性が高い |
| `WaitForURLAsync` | ナビゲーション後のルート変更を確認 | URL はレンダリング前に変更される |
| `Locator.WaitForAsync` | 要素の表示状態を待つ | きめ細かな制御が可能 |
| ~~`WaitForLoadStateAsync`~~ | ~~Blazor アプリ内ナビゲーションには使わない~~ | Blazor はページをリロードしない |

```csharp
// ❌ NG: ネットワークアイドルを待つ（Blazor はページをリロードしない）
await page.WaitForLoadStateAsync(LoadState.NetworkIdle);

// ✅ OK: 特定の DOM 要素を待つ
await page.WaitForSelectorAsync("h1:has-text('My Page')");

// ✅ OK: 要素の表示を待つ
await page.Locator("[data-test='content']").WaitForAsync();
```

> **Values**: 温故知新（SPA の基本的なルーティング原理を理解した上で、Playwright の最新待機 API を正しく選択する）

### Step 3: Use Stable Selectors and Handle Forms

Blazor コンポーネントに `data-test` 属性を追加し、セマンティックセレクタを使用する。CSS クラスに結びついたセレクタは UI デザイン変更時に壊れるため。

**Blazor コンポーネント側：**

```razor
<button data-test="submit-button" @onclick="HandleSubmit">Submit</button>
<input data-test="username-input" @bind="Username" />
<div data-test="result-container">@Result</div>
```

**テストコード側：**

```csharp
[Fact]
public async Task FormSubmission()
{
    var page = await _fixture.Browser.NewPageAsync();
    await page.GotoAsync(baseUrl);

    // data-test 属性を持つ要素には GetByTestId を使用
    await page.GetByTestId("username-input").FillAsync("testuser");
    await page.GetByTestId("password-input").FillAsync("password123");
    await page.GetByTestId("submit-button").ClickAsync();

    var result = await page.GetByTestId("result-container").TextContentAsync();
    Assert.Contains("Success", result);
}
```

**セレクタ優先順位（上が優先）：**

| セレクタ | 例 | 安定性 |
|---------|-----|--------|
| Role | `GetByRole(AriaRole.Button, new() { Name = "Submit" })` | 高 |
| Test ID | `GetByTestId("user-profile")` | 高 |
| Label | `GetByLabel("Email Address")` | 中 |
| Text | `GetByText("Hello, World!")` | 中 |
| CSS | `Locator(".mud-button-primary")` | 低 |

> **Values**: 基礎と型の追求（data-test 属性という「型」をコンポーネントに埋め込むことで、UI 変更に強い安定したテストを実現する）

### Step 4: Test Authentication Flows

インタラクティブログインをテストし、保護ページへのアクセスを検証する。認証はエンドツーエンドで動作しなければならない重要なパスのため。

```csharp
[Fact]
public async Task LoginFlow()
{
    var page = await _fixture.Browser.NewPageAsync();
    await page.GotoAsync($"{baseUrl}/login");

    await page.FillAsync("input[name='username']", "alice");
    await page.FillAsync("input[name='password']", "P@ssw0rd");
    await page.ClickAsync("button[type='submit']");

    // ダッシュボードへのリダイレクトを待機
    await page.WaitForURLAsync("**/dashboard");

    var username = await page.TextContentAsync("[data-test='user-name']");
    Assert.Equal("alice", username);
}
```

より高速なテストのために、UI ログインの代わりに Cookie を注入する方法がある。Cookie 注入と OAuth モッキングパターンは [references/detailed-patterns.md](references/detailed-patterns.md) を参照。

> **Values**: 成長の複利（認証テストの型を習得することで、すべてのプロテクトページのテスト設計が加速する）

### Step 5: Assert No Blazor Errors and Debug Failures

アクション後は常に Blazor エラーオーバーレイをチェックする。Blazor の未処理例外は `#blazor-error-ui` にレンダリングされ、テストを失敗させないため。

```csharp
public static async Task AssertNoBlazorErrors(this IPage page)
{
    var errorUi = page.Locator("#blazor-error-ui");
    if (await errorUi.IsVisibleAsync())
    {
        var errorText = await errorUi.InnerTextAsync();
        Assert.Fail($"Blazor error occurred: {errorText}");
    }
}

[Fact]
public async Task Page_ShouldNotHaveErrors()
{
    var page = await _fixture.Browser.NewPageAsync();
    await page.GotoAsync(baseUrl);

    await page.ClickAsync("[data-test='action-button']");
    await page.AssertNoBlazorErrors();
}
```

**デバッグテクニック：**

| テクニック | 方法 | 使用場面 |
|-----------|------|---------|
| ヘッドモード | `Headless = false` | テスト実行を視覚的に確認 |
| スローモーション | `SlowMo = 500` | タイミング関連の失敗を特定 |
| インスペクタ | `await page.PauseAsync()` | アクションをインタラクティブにステップ実行 |
| コンソールキャプチャ | `page.Console += (_, msg) => ...` | JavaScript や Blazor エラーを診断 |
| 失敗時スクリーンショット | catch 内で `page.ScreenshotAsync(...)` | CI 限定の失敗をデバッグ |

スクリーンショットテストとカスタム待機ヘルパーは [references/detailed-patterns.md](references/detailed-patterns.md) を参照。

> **Values**: 余白の設計（エラー UI チェックという安全ネットを設けることで、見逃しやすい例外を検出する余白を確保する）

### Step 6: Configure CI with GitHub Actions

ブラウザインストールとアーティファクト取得を含む CI で Playwright テストを実行する。自動回帰テストはマージ前に UI の破損を検出するため。

```yaml
name: Playwright Tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup .NET
      uses: actions/setup-dotnet@v3
      with:
        dotnet-version: 9.0.x
    - name: Install Playwright Browsers
      run: pwsh -Command "playwright install --with-deps"
    - name: Build
      run: dotnet build -c Release
    - name: Run Playwright Tests
      run: |
        dotnet test tests/YourApp.UITests \
          --no-build -c Release --logger trx
    - name: Upload Screenshots
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: playwright-screenshots
        path: "**/screenshots/"
    - name: Upload Test Results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: "**/TestResults/*.trx"
```

> **Values**: 継続は力（CI パイプラインでテストをコツコツ実行し続けることで、品質の複利を積み上げる）

## Good Practices

- ✅ UI リファクタリングに強い安定したセレクタとして `data-test` 属性を使用する
- ✅ CSS セレクタよりセマンティックセレクタ（`GetByRole`、`GetByLabel`）を優先する
- ✅ ブランケット遅延やネットワークアイドルの代わりに特定の DOM 要素を待機する
- ✅ 重要なユーザーアクションの後は `#blazor-error-ui` の表示をチェックする
- ✅ レスポンシブデザインの動作を検証するために複数のビューポートでテストする
- ✅ 高速実行のためにテスト間でブラウザコンテキストを再利用する
- ✅ CI 限定の問題をデバッグするためにテスト失敗時にスクリーンショットを取得する
- ✅ Blazor Server SignalR テストには `[Collection]` で並列スレッドを制限する
- ✅ `IAsyncLifetime` パターンでページとブラウザを適切に破棄する
- ✅ 環境間で再現性のある結果のためにブラウザチャネルを固定する

## Common Pitfalls

1. **Waiting for NetworkIdle in Blazor** — Blazor SPA ナビゲーションはページリロードを発生させないため、`WaitForLoadStateAsync(NetworkIdle)` はハングする。Fix: `WaitForSelectorAsync` を使用して特定の DOM 要素を待機する。
2. **Selectors Tied to CSS Classes** — UI フレームワークやデザインが変更されると `.btn-primary` や `.mud-button` は壊れる。Fix: `data-test` 属性を追加して `GetByTestId` を使用する。
3. **Missing Blazor Error Check** — 未処理の例外が `#blazor-error-ui` にレンダリングされてもテストは通過する。Fix: 重要なアクションの後に `AssertNoBlazorErrors()` を呼び出す。
4. **SignalR Connection Saturation** — Blazor Server に対して多くの並列テストを実行すると SignalR 接続が枯渇する。Fix: `[Collection]` と `MaxParallelThreads = 2` を使用する。
5. **Ignoring Browser Disposal** — ブラウザの破棄を忘れるとリソースリークとポート枯渇を引き起こす。Fix: 適切な `DisposeAsync` を持つ `IAsyncLifetime` を実装する。

## Anti-Patterns

### ❌ Network Wait for SPA Navigation → ✅ DOM Wait

```csharp
// ❌ BAD — Blazor はページをリロードしないためハングする
await page.WaitForLoadStateAsync(LoadState.NetworkIdle);
await page.ClickAsync("[data-test='nav-link']");

// ✅ GOOD — レンダリングされた要素を待機する
await page.ClickAsync("[data-test='nav-link']");
await page.WaitForSelectorAsync("h1:has-text('Target Page')");
```

### ❌ Fragile CSS Selectors → ✅ Test Attributes

```csharp
// ❌ BAD — デザイン変更で壊れる
await page.ClickAsync(".mud-button-primary.submit-btn");

// ✅ GOOD — UI リファクタリング全体で安定
await page.GetByTestId("submit-button").ClickAsync();
```

### ❌ Ignoring Error Overlay → ✅ Explicit Assert

```csharp
// ❌ BAD — Blazor が例外を投げてもテストは通過する
await page.ClickAsync("[data-test='action']");
Assert.True(await page.IsVisibleAsync("[data-test='result']"));

// ✅ GOOD — 未処理の例外を検出する
await page.ClickAsync("[data-test='action']");
await page.AssertNoBlazorErrors();
Assert.True(await page.IsVisibleAsync("[data-test='result']"));
```

### ❌ Hardcoded Delays → ✅ Element Waits

```csharp
// ❌ BAD — 任意の遅延、CI でフレーキー
await Task.Delay(3000);
var text = await page.TextContentAsync("[data-test='result']");

// ✅ GOOD — 要素が表示されるまで待機
await page.Locator("[data-test='result']").WaitForAsync();
var text = await page.Locator("[data-test='result']").TextContentAsync();
```

## Quick Reference

### Selector Strategy Decision Table

| 用途 | セレクタ | 例 |
|------|---------|-----|
| アクセシブルなボタン | `GetByRole` | `GetByRole(AriaRole.Button, new() { Name = "Save" })` |
| テスト専用要素 | `GetByTestId` | `GetByTestId("user-profile")` |
| ラベル付きフォーム入力 | `GetByLabel` | `GetByLabel("Email Address")` |
| テキストコンテンツ | `GetByText` | `GetByText("Welcome back")` |
| CSS（最後の手段） | `Locator` | `Locator("#login-form")` |

### Blazor Wait Strategy Cheat Sheet

| シナリオ | メソッド | 理由 |
|---------|--------|------|
| 初回ページロード | `GotoAsync` + `WaitForSelectorAsync` | HTTP ナビゲーション + Blazor 初期化 |
| アプリ内ナビゲーション | Click + `WaitForSelectorAsync` | クライアントサイドルーティング、リロードなし |
| ルート確認 | `WaitForURLAsync("**/path")` | URL は DOM より先に更新される |
| 要素出現 | `Locator.WaitForAsync()` | きめ細かな状態制御 |
| Blazor エラーチェック | `Locator("#blazor-error-ui").IsVisibleAsync()` | サイレント例外を検出 |

### Debugging Checklist

| 症状 | 原因の可能性 | 修正 |
|------|------------|------|
| テストがハングする | `WaitForLoadStateAsync(NetworkIdle)` | `WaitForSelectorAsync` に変更 |
| フレーキーなセレクタ | CSS クラスが変更された | `data-test` 属性を使用 |
| サイレント失敗 | 未処理の Blazor 例外 | `AssertNoBlazorErrors()` を追加 |
| CI 限定の失敗 | タイミングの差異 | 明示的な要素待機を追加 |
| 接続拒否 | ブラウザ未インストール | `playwright install --with-deps` を実行 |

## Resources

- [Playwright .NET Documentation](https://playwright.dev/dotnet/)
- [Blazor Testing Guidance](https://learn.microsoft.com/en-us/aspnet/core/blazor/test)
- [Playwright Locators](https://playwright.dev/dotnet/docs/locators)
- [Blazor Server SignalR](https://learn.microsoft.com/en-us/aspnet/core/blazor/fundamentals/signalr)
- [references/detailed-patterns.md](references/detailed-patterns.md) — Cookie 認証、OAuth モッキング、SignalR テスト、スクリーンショット、カスタム待機ヘルパー
