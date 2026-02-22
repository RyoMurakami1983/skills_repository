---
name: dotnet-playwright-blazor
description: >
  Write end-to-end UI tests for Blazor Server and WebAssembly applications
  using Playwright. Covers setup, navigation, selectors, authentication, error
  handling, and CI integration.
  Use when testing Blazor components, forms, or user workflows with Playwright.
metadata:
  author: RyoMurakami1983
  tags: [playwright, blazor, testing, e2e, dotnet, ui-testing]
  invocable: false
---

# Testing Blazor Applications with Playwright

A concise guardrail for writing end-to-end UI tests against Blazor Server and Blazor WebAssembly applications using Microsoft.Playwright. Targets .NET 8+ with xUnit or MSTest.

**Acronyms**: E2E (End-to-End), SPA (Single-Page Application), CI (Continuous Integration).

## When to Use This Skill

- Writing end-to-end UI tests for Blazor Server or WebAssembly application pages
- Testing interactive Blazor components, EditForms, and multi-step user workflows
- Verifying cookie-based or OAuth authentication and authorization redirect flows
- Debugging Blazor rendering issues using headed mode and Playwright Inspector tools
- Capturing screenshots for visual regression testing across desktop and mobile viewports
- Configuring GitHub Actions CI pipelines to run Playwright tests against Blazor apps
- Detecting unhandled Blazor exceptions by asserting the error overlay is not visible

## Related Skills

| Skill | Scope | When |
|-------|-------|------|
| `dotnet-project-structure` | .NET solution layout, project references | Defining test project location |
| `dotnet-modern-csharp-coding-standards` | C# coding style, async patterns | Writing test helper code |

## Core Principles

1. **Wait for DOM, Not Network** — Blazor renders asynchronously via client-side routing; wait for specific DOM elements instead of network idle. Why: Blazor navigation doesn't trigger HTTP loads.
2. **Use Test Attributes for Selectors** — Add `data-test` or `data-testid` attributes to Blazor components for stable selectors. Why: CSS classes and IDs change with UI refactoring.
3. **Always Check Blazor Error UI** — Assert `#blazor-error-ui` is not visible after every significant action. Why: unhandled exceptions render silently in the error overlay.
4. **Headless by Default, Headed for Debug** — Run tests headless in CI and headed locally with SlowMo for debugging. Why: headless is fast; headed reveals timing and rendering issues.
5. **Pin Browser Channels** — Use specific browser channels (msedge, chrome) for reproducible results. Why: default Chromium revisions may differ across environments.

> **Values**: 基礎と型の追求（DOM 待機・テスト属性・エラー UI チェックという「型」を守ることで、信頼性の高いテスト基盤を築く）, 温故知新（Playwright の最新 API を活かしつつ、Blazor の非同期レンダリングという基本特性を正しく理解する）

## Workflow: Test Blazor Applications with Playwright

### Step 1: Set Up Playwright Fixture

Create a shared test fixture that initializes Playwright and launches a browser. Why: reusing a single browser instance across tests avoids repeated startup cost.

**Required NuGet packages:**

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Playwright" Version="*" />
  <PackageReference Include="Microsoft.Playwright.MSTest" Version="*" />
  <!-- OR for xUnit -->
  <PackageReference Include="xunit" Version="*" />
  <PackageReference Include="xunit.runner.visualstudio" Version="*" />
</ItemGroup>
```

Install browsers before first run:

```bash
pwsh -Command "playwright install --with-deps"
```

**Fixture implementation:**

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
            // SlowMo = 100 // Uncomment for debugging
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

Use DOM-based wait strategies instead of network idle. Why: Blazor SPA navigation is client-side and does not trigger page reloads.

```csharp
[Fact]
public async Task NavigateToCounter()
{
    var page = await _fixture.Browser.NewPageAsync();

    // Initial load — classic HTTP navigation
    await page.GotoAsync("https://localhost:5001");
    await page.WaitForSelectorAsync("h1:has-text('Welcome')");

    // In-app navigation — no page reload
    await page.GetByRole(AriaRole.Link, new() { Name = "Counter" })
        .ClickAsync();
    await page.WaitForSelectorAsync("h1:has-text('Counter')");
}
```

**Wait strategy decision table:**

| Strategy | Use When | Why |
|----------|----------|-----|
| `WaitForSelectorAsync` | Waiting for a specific element to appear | Most reliable for Blazor |
| `WaitForURLAsync` | Confirming route change after navigation | URL changes before render |
| `Locator.WaitForAsync` | Waiting for element visibility or state | Fine-grained control |
| ~~`WaitForLoadStateAsync`~~ | ~~Never for Blazor in-app navigation~~ | Blazor doesn't reload pages |

```csharp
// ❌ DON'T: Wait for network idle (Blazor doesn't reload pages)
await page.WaitForLoadStateAsync(LoadState.NetworkIdle);

// ✅ DO: Wait for specific DOM elements
await page.WaitForSelectorAsync("h1:has-text('My Page')");

// ✅ DO: Wait for element visibility
await page.Locator("[data-test='content']").WaitForAsync();
```

> **Values**: 温故知新（SPA の基本的なルーティング原理を理解した上で、Playwright の最新待機 API を正しく選択する）

### Step 3: Use Stable Selectors and Handle Forms

Add `data-test` attributes to Blazor components and use semantic selectors. Why: selectors tied to CSS classes break when the UI design changes.

**In Blazor components:**

```razor
<button data-test="submit-button" @onclick="HandleSubmit">Submit</button>
<input data-test="username-input" @bind="Username" />
<div data-test="result-container">@Result</div>
```

**In test code:**

```csharp
[Fact]
public async Task FormSubmission()
{
    var page = await _fixture.Browser.NewPageAsync();
    await page.GotoAsync(baseUrl);

    // Use GetByTestId for elements with data-test attributes
    await page.GetByTestId("username-input").FillAsync("testuser");
    await page.GetByTestId("password-input").FillAsync("password123");
    await page.GetByTestId("submit-button").ClickAsync();

    var result = await page.GetByTestId("result-container").TextContentAsync();
    Assert.Contains("Success", result);
}
```

**Selector priority (prefer top):**

| Selector | Example | Stability |
|----------|---------|-----------|
| Role | `GetByRole(AriaRole.Button, new() { Name = "Submit" })` | High |
| Test ID | `GetByTestId("user-profile")` | High |
| Label | `GetByLabel("Email Address")` | Medium |
| Text | `GetByText("Hello, World!")` | Medium |
| CSS | `Locator(".mud-button-primary")` | Low |

> **Values**: 基礎と型の追求（data-test 属性という「型」をコンポーネントに埋め込むことで、UI 変更に強い安定したテストを実現する）

### Step 4: Test Authentication Flows

Test interactive login and verify protected page access. Why: authentication is a critical path that must work end-to-end.

```csharp
[Fact]
public async Task LoginFlow()
{
    var page = await _fixture.Browser.NewPageAsync();
    await page.GotoAsync($"{baseUrl}/login");

    await page.FillAsync("input[name='username']", "alice");
    await page.FillAsync("input[name='password']", "P@ssw0rd");
    await page.ClickAsync("button[type='submit']");

    // Wait for redirect to dashboard
    await page.WaitForURLAsync("**/dashboard");

    var username = await page.TextContentAsync("[data-test='user-name']");
    Assert.Equal("alice", username);
}
```

For faster tests, inject cookies instead of logging in through the UI. See [references/detailed-patterns.md](references/detailed-patterns.md) for cookie injection and OAuth mocking patterns.

> **Values**: 成長の複利（認証テストの型を習得することで、すべてのプロテクトページのテスト設計が加速する）

### Step 5: Assert No Blazor Errors and Debug Failures

Always check for the Blazor error overlay after actions. Why: unhandled exceptions in Blazor are rendered in `#blazor-error-ui` without failing the test.

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

**Debugging tips:**

| Technique | How | Use When |
|-----------|-----|----------|
| Headed mode | `Headless = false` | Watching test execution visually |
| Slow motion | `SlowMo = 500` | Identifying timing-related failures |
| Inspector | `await page.PauseAsync()` | Stepping through actions interactively |
| Console capture | `page.Console += (_, msg) => ...` | Diagnosing JavaScript or Blazor errors |
| Screenshot on failure | `page.ScreenshotAsync(...)` in catch | Debugging CI-only failures |

See [references/detailed-patterns.md](references/detailed-patterns.md) for screenshot testing and custom wait helpers.

> **Values**: 余白の設計（エラー UI チェックという安全ネットを設けることで、見逃しやすい例外を検出する余白を確保する）

### Step 6: Configure CI with GitHub Actions

Run Playwright tests in CI with browser installation and artifact capture. Why: automated regression testing catches UI breakages before merge.

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

- Use `data-test` attributes for stable selectors resistant to UI refactoring
- Avoid CSS selectors; prefer semantic selectors (`GetByRole`, `GetByLabel`)
- Use `WaitForSelectorAsync` for specific DOM elements instead of blanket delays
- Apply `AssertNoBlazorErrors()` after every significant user action
- Consider multiple viewports to verify responsive design behavior
- Use browser context reuse across tests for faster execution
- Implement screenshot capture on test failure for debugging CI-only issues
- Use `[Collection]` to limit parallel threads for Blazor Server SignalR tests
- Implement `IAsyncLifetime` to dispose pages and browsers properly
- Use pinned browser channels for reproducible results across environments

## Common Pitfalls

1. **Waiting for NetworkIdle in Blazor** — Using `WaitForLoadStateAsync(NetworkIdle)` hangs because Blazor SPA navigation doesn't trigger page reloads. Fix: use `WaitForSelectorAsync` to wait for specific DOM elements.
2. **Selectors Tied to CSS Classes** — Using `.btn-primary` or `.mud-button` breaks when the UI framework or design changes. Fix: add `data-test` attributes and use `GetByTestId`.
3. **Missing Blazor Error Check** — Tests pass while unhandled exceptions render in `#blazor-error-ui`. Fix: call `AssertNoBlazorErrors()` after every significant action.
4. **SignalR Connection Saturation** — Running many parallel tests against Blazor Server exhausts SignalR connections. Fix: use `[Collection]` with `MaxParallelThreads = 2`.
5. **Ignoring Browser Disposal** — Forgetting to dispose browsers causes resource leaks and port exhaustion. Fix: implement `IAsyncLifetime` with proper `DisposeAsync`.

## Anti-Patterns

### ❌ Network Wait for SPA Navigation → ✅ DOM Wait

```csharp
// ❌ BAD — hangs because Blazor doesn't reload pages
await page.WaitForLoadStateAsync(LoadState.NetworkIdle);
await page.ClickAsync("[data-test='nav-link']");

// ✅ GOOD — waits for the rendered element
await page.ClickAsync("[data-test='nav-link']");
await page.WaitForSelectorAsync("h1:has-text('Target Page')");
```

### ❌ Fragile CSS Selectors → ✅ Test Attributes

```csharp
// ❌ BAD — breaks when design changes
await page.ClickAsync(".mud-button-primary.submit-btn");

// ✅ GOOD — stable across UI refactoring
await page.GetByTestId("submit-button").ClickAsync();
```

### ❌ Ignoring Error Overlay → ✅ Explicit Assert

```csharp
// ❌ BAD — test passes even when Blazor throws
await page.ClickAsync("[data-test='action']");
Assert.True(await page.IsVisibleAsync("[data-test='result']"));

// ✅ GOOD — catches unhandled exceptions
await page.ClickAsync("[data-test='action']");
await page.AssertNoBlazorErrors();
Assert.True(await page.IsVisibleAsync("[data-test='result']"));
```

### ❌ Hardcoded Delays → ✅ Element Waits

```csharp
// ❌ BAD — arbitrary delay, flaky in CI
await Task.Delay(3000);
var text = await page.TextContentAsync("[data-test='result']");

// ✅ GOOD — waits until element appears
await page.Locator("[data-test='result']").WaitForAsync();
var text = await page.Locator("[data-test='result']").TextContentAsync();
```

## Quick Reference

### Selector Strategy Decision Table

| Need | Selector | Example |
|------|----------|---------|
| Accessible button | `GetByRole` | `GetByRole(AriaRole.Button, new() { Name = "Save" })` |
| Test-specific element | `GetByTestId` | `GetByTestId("user-profile")` |
| Form input by label | `GetByLabel` | `GetByLabel("Email Address")` |
| Text content | `GetByText` | `GetByText("Welcome back")` |
| CSS (last resort) | `Locator` | `Locator("#login-form")` |

### Blazor Wait Strategy Cheat Sheet

| Scenario | Method | Why |
|----------|--------|-----|
| Initial page load | `GotoAsync` + `WaitForSelectorAsync` | HTTP navigation + Blazor init |
| In-app navigation | Click + `WaitForSelectorAsync` | Client-side routing, no reload |
| Route confirmation | `WaitForURLAsync("**/path")` | URL updates before DOM |
| Element appearance | `Locator.WaitForAsync()` | Fine-grained state control |
| Blazor error check | `Locator("#blazor-error-ui").IsVisibleAsync()` | Catch silent exceptions |

### Debugging Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Test hangs | `WaitForLoadStateAsync(NetworkIdle)` | Switch to `WaitForSelectorAsync` |
| Flaky selector | CSS class changed | Use `data-test` attribute |
| Silent failure | Unhandled Blazor exception | Add `AssertNoBlazorErrors()` |
| CI-only failure | Timing difference | Add explicit element waits |
| Connection refused | Browser not installed | Run `playwright install --with-deps` |

## Resources

- [Playwright .NET Documentation](https://playwright.dev/dotnet/)
- [Blazor Testing Guidance](https://learn.microsoft.com/en-us/aspnet/core/blazor/test)
- [Playwright Locators](https://playwright.dev/dotnet/docs/locators)
- [Blazor Server SignalR](https://learn.microsoft.com/en-us/aspnet/core/blazor/fundamentals/signalr)
- [references/detailed-patterns.md](references/detailed-patterns.md) — Cookie auth, OAuth mocking, SignalR tests, screenshots, custom wait helpers
