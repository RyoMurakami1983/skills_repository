---
name: dotnet-snapshot-testing
description: >
  Approve rendered output, API surfaces, HTTP responses, and serialized objects
  using Verify snapshot testing in .NET. Captures output as human-reviewed baselines
  and detects unintended changes through diff comparison.
  Use when validating complex output where manual assertions are impractical.
metadata:
  author: RyoMurakami1983
  tags: [verify, snapshot-testing, xunit, dotnet, api-approval, email-testing, regression]
  invocable: false
---

# Snapshot Testing with Verify

Capture output and compare it against human-approved baselines. Verify generates `.received.` files on first run, developers approve them as `.verified.` files, and subsequent runs detect unintended changes through diff comparison. Targets .NET 8+ with xUnit.

**Acronyms**: API (Application Programming Interface), CI (Continuous Integration), HTML (HyperText Markup Language), MJML (Mailjet Markup Language), DI (Dependency Injection).

## When to Use This Skill

- Verifying rendered HTML email output to catch CSS and layout regressions automatically
- Approving public API surfaces to detect accidental breaking changes before release
- Testing HTTP response bodies and headers as a single verified snapshot per endpoint
- Validating serialization output format to ensure wire compatibility across versions
- Catching unintended changes in complex object graphs without writing manual assertions
- Comparing generated code or report output against approved baselines for regression

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-testcontainers` | Integration testing with real Docker infrastructure |
| `dotnet-serialization` | Serialization strategies, JSON/XML format configuration |
| `dotnet-csharp-api-design` | Public API design, versioning, breaking change prevention |

## Core Principles

1. **Human-Approved Baselines** — Every snapshot requires explicit developer approval before becoming the baseline. Why: prevents false baselines from being committed without review.
2. **Diff-Based Regression Detection** — Changes surface through diff tools, not silent assertion failures. Why: visual diffs make unintended changes immediately obvious.
3. **Scrub Dynamic Values** — Replace timestamps, GUIDs, and non-deterministic data with stable placeholders. Why: ensures snapshots produce identical results across runs and environments.
4. **One Snapshot Per Concern** — Each test verifies a single logical output. Why: pinpoints the exact source of regression when a snapshot fails.
5. **Version Control Integration** — Commit `.verified.` files and ignore `.received.` files. Why: baselines are reviewed in PRs and tracked in history.

> **Values**: 基礎と型の追求（Verify の「型」—承認ベースライン・スクラブ・差分検出—を守ることで、再現可能なリグレッション検出基盤を築く）, ニュートラルな視点（手動アサーションの偏りを排し、差分ベースの客観的な比較で品質基準を保つ）

## Workflow: Snapshot Testing with Verify

### Step 1: Install Verify and Configure ModuleInitializer

Install the Verify NuGet package for your test framework and configure project-level settings. Why: centralized configuration ensures consistent snapshot behavior across all tests.

```bash
dotnet add package Verify.Xunit
# or: dotnet add package Verify.NUnit / Verify.MSTest
```

```csharp
using System.Runtime.CompilerServices;

public static class ModuleInitializer
{
    [ModuleInitializer]
    public static void Init()
    {
        // Store verified files in a dedicated directory
        VerifyBase.UseProjectRelativeDirectory("Snapshots");
    }
}
```

> **Values**: 基礎と型の追求（ModuleInitializer という初期化の「型」を最初に整えることで、全テストの一貫性を保証する）

### Step 2: Write Basic Snapshot Tests

Return `Verify(object)` from test methods to generate snapshot files. Why: Verify serializes the object and compares it against the approved baseline automatically.

```csharp
// ✅ GOOD — descriptive test name becomes the snapshot file name
[Fact]
public Task VerifyUserDto()
{
    var user = new UserDto(
        Id: "user-123",
        Name: "John Doe",
        Email: "john@example.com",
        CreatedAt: new DateTime(2025, 1, 15));

    return Verify(user);
}
```

First run creates `VerifyUserDto.received.txt`. Approve it to create `VerifyUserDto.verified.txt`:

```json
{
  Id: user-123,
  Name: John Doe,
  Email: john@example.com,
  CreatedAt: 2025-01-15T00:00:00
}
```

Use the `extension` parameter for non-text content:

```csharp
[Fact]
public async Task VerifyRenderedEmail()
{
    var html = await _emailRenderer.RenderAsync("Welcome", new { Name = "John" });
    await Verify(html, extension: "html");
}
```

> **Values**: 温故知新（テストの命名規則という「過去の知恵」を、スナップショットファイル名の自動生成という新技術と結びつける）

### Step 3: Scrub Dynamic Values for Deterministic Snapshots

Replace non-deterministic data with stable placeholders. Why: timestamps and GUIDs change every run and cause false failures without scrubbing.

```csharp
[Fact]
public Task VerifyOrder()
{
    var order = new Order
    {
        Id = Guid.NewGuid(),        // different every run
        CreatedAt = DateTime.UtcNow, // different every run
        Total = 99.99m
    };

    return Verify(order)
        .ScrubMember("Id")
        .ScrubMember("CreatedAt");
}
```

Configure global scrubbing in `ModuleInitializer` to avoid repetition:

```csharp
[ModuleInitializer]
public static void Init()
{
    VerifierSettings.ScrubMembersWithType<DateTime>();
    VerifierSettings.ScrubMembersWithType<DateTimeOffset>();
    VerifierSettings.ScrubMembersWithType<Guid>();

    // Scrub specific patterns (tokens, session IDs)
    VerifierSettings.AddScrubber(s =>
        Regex.Replace(s, @"token=[a-zA-Z0-9]+", "token=SCRUBBED"));
}
```

> **Values**: 余白の設計（動的値をスクラブすることで、環境差異に対する余白を確保し、どの環境でも同一結果を保証する）

### Step 4: Apply to Domain-Specific Scenarios

Use Verify for email templates, API surfaces, and HTTP responses. Why: each domain benefits from visual diff review and version-controlled baselines.

**Email template verification:**

```csharp
[Fact]
public async Task UserSignupInvitation_RendersCorrectly()
{
    var renderer = _services.GetRequiredService<IMjmlTemplateRenderer>();
    var variables = new Dictionary<string, string>
    {
        { "OrganizationName", "Acme Corporation" },
        { "InviteeName", "John Doe" },
        { "InvitationLink", "https://example.com/invite/abc123" },
        { "ExpirationDate", "December 31, 2025" }
    };

    var html = await renderer.RenderTemplateAsync(
        "UserInvitations/UserSignupInvitation", variables);
    await Verify(html, extension: "html");
}
```

**Public API surface approval:**

```csharp
[Fact]
public Task ApprovePublicApi()
{
    var api = typeof(MyPublicClass).Assembly.GeneratePublicApi();
    return Verify(api);
}
```

**HTTP response verification:**

```csharp
[Fact]
public async Task GetUser_ReturnsExpectedResponse()
{
    var client = _factory.CreateClient();
    var response = await client.GetAsync("/api/users/123");

    await Verify(new
    {
        StatusCode = response.StatusCode,
        Headers = response.Headers
            .Where(h => h.Key.StartsWith("X-"))
            .ToDictionary(h => h.Key, h => h.Value.First()),
        Body = await response.Content.ReadAsStringAsync()
    });
}
```

> **Values**: 成長の複利（一つの Verify パターンを習得すれば、メール・API・HTTP の各ドメインに横展開でき、知識が複利的に増幅する）

### Step 5: Configure File Organization and CI Integration

Organize snapshot files and configure CI to fail without launching diff tools. Why: proper file organization prevents repository clutter and CI hangs.

**Recommended project structure:**

```
tests/
  MyApp.Tests/
    Snapshots/
      EmailTests/
        WelcomeEmail.verified.html
      ApiTests/
        GetUser.verified.txt
    EmailTests.cs
    ApiTests.cs
    ModuleInitializer.cs
```

**`.gitignore` — exclude received files:**

```gitignore
*.received.*
```

**`.gitattributes` — collapse verified files in PR diffs:**

```gitattributes
*.verified.txt linguist-generated=true
*.verified.html linguist-generated=true
```

**CI configuration in ModuleInitializer:**

```csharp
[ModuleInitializer]
public static void Init()
{
    if (Environment.GetEnvironmentVariable("CI") == "true")
    {
        // Use inline diff output instead of launching diff tool
        VerifyDiffPlex.UseDiffPlex(OutputType.Minimal);
        DiffRunner.Disabled = true;
    }
}
```

> **Values**: 継続は力（CI パイプラインでのスナップショット検証を自動化し、継続的にリグレッションを検出する仕組みを構築する）

## Good Practices

- ✅ Use descriptive test names — they become snapshot file names for easy identification
- ✅ Scrub all dynamic values globally via `ModuleInitializer` to avoid per-test repetition
- ✅ Use the `extension` parameter for HTML, JSON, and XML content for proper rendering
- ✅ Commit `.verified.*` files to source control and review changes in pull requests
- ✅ Use `linguist-generated=true` in `.gitattributes` to collapse snapshot diffs in PRs
- ✅ Disable diff tool launching in CI with `DiffRunner.Disabled = true`
- ✅ Keep one snapshot per test method to isolate regression sources
- ✅ Use `VerifyBase.UseProjectRelativeDirectory` for consistent file paths across IDEs

## Common Pitfalls

1. **Unscrubbed Dynamic Values** — GUIDs and timestamps cause snapshots to fail on every run. Fix: use `ScrubMember` or `ScrubMembersWithType<T>()` in `ModuleInitializer`.
2. **Committing Received Files** — Adding `*.received.*` to source control creates noise and merge conflicts. Fix: add `*.received.*` to `.gitignore` immediately.
3. **Diff Tool Launches in CI** — Verify tries to open a diff tool, causing CI to hang indefinitely. Fix: set `DiffRunner.Disabled = true` when `CI` environment variable is detected.
4. **Overly Broad Snapshots** — Verifying entire response objects captures irrelevant fields. Fix: project to a focused anonymous type with only the fields under test.
5. **Generic Test Names** — Names like `Test1` produce unidentifiable snapshot files. Fix: use descriptive names like `UserRegistration_WithValidData_ReturnsConfirmation`.

## Anti-Patterns

### ❌ Verifying Without Scrubbing → ✅ Scrub Dynamic Values

```csharp
// ❌ BAD — fails every run because Id and CreatedAt change
var order = new Order { Id = Guid.NewGuid(), CreatedAt = DateTime.UtcNow };
await Verify(order);

// ✅ GOOD — dynamic values replaced with stable placeholders
await Verify(order).ScrubMember("Id").ScrubMember("CreatedAt");
```

Why: unscrubbed dynamic values make snapshots non-deterministic and produce false failures.

### ❌ Snapshot for Simple Values → ✅ Use Direct Assertions

```csharp
// ❌ BAD — snapshot overhead for a simple value check
await Verify(result.Count);

// ✅ GOOD — direct assertion is clearer and faster
Assert.Equal(5, result.Count);
```

Why: snapshots add file management overhead that is only justified for complex structure verification.

### ❌ Monolithic Snapshots → ✅ Focused Projections

```csharp
// ❌ BAD — captures entire response including irrelevant headers
await Verify(response);

// ✅ GOOD — focuses on the fields that matter
await Verify(new { response.StatusCode, Body = await response.Content.ReadAsStringAsync() });
```

Why: monolithic snapshots break on any change, making it hard to identify the actual regression.

## Quick Reference

### Snapshot Testing Decision Table

| Scenario | Use Snapshot? | Why |
|----------|--------------|-----|
| Rendered HTML emails | ✅ Yes | Catches visual and layout regressions |
| Public API surfaces | ✅ Yes | Prevents accidental breaking changes |
| Serialization output | ✅ Yes | Validates wire format compatibility |
| Complex object graphs | ✅ Yes | Easier than dozens of manual assertions |
| Simple value checks | ❌ No | Use `Assert.Equal` directly |
| Business logic results | ❌ No | Use explicit assertions for clarity |
| Performance metrics | ❌ No | Use benchmarks instead |

### Verify API Cheat Sheet

| Method | Purpose | Example |
|--------|---------|---------|
| `Verify(object)` | Snapshot any serializable object | `return Verify(dto);` |
| `Verify(string, extension)` | Snapshot with file type | `await Verify(html, extension: "html");` |
| `.ScrubMember("Name")` | Replace specific field | `Verify(obj).ScrubMember("Id");` |
| `ScrubMembersWithType<T>()` | Scrub all fields of type | `VerifierSettings.ScrubMembersWithType<Guid>();` |
| `AddScrubber(Action)` | Custom regex scrubbing | `VerifierSettings.AddScrubber(...)` |
| `DiffRunner.Disabled` | Disable diff tool in CI | `DiffRunner.Disabled = true;` |

### File Naming Convention

| Input | Output File |
|-------|-------------|
| `[Fact] VerifyUserDto()` | `VerifyUserDto.verified.txt` |
| `Verify(html, extension: "html")` | `MethodName.verified.html` |
| Parameterized test | `MethodName_ParameterValue.verified.txt` |

## Resources

- [Verify GitHub](https://github.com/VerifyTests/Verify) — Main repository and documentation
- [Verify.Xunit](https://github.com/VerifyTests/Verify.Xunit) — xUnit integration package
- [PublicApiGenerator](https://github.com/PublicApiGenerator/PublicApiGenerator) — API surface approval
- [Verify.DiffPlex](https://github.com/VerifyTests/Verify.DiffPlex) — Inline diff for CI environments
