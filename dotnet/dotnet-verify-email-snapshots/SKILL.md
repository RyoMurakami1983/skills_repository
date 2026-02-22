---
name: dotnet-verify-email-snapshots
description: >
  Snapshot test email templates using Verify to catch rendering regressions.
  Validates rendered HTML output matches approved baselines with MJML support.
  Use when verifying email template rendering against human-approved snapshots.
metadata:
  author: RyoMurakami1983
  tags: [verify, snapshot-testing, email-testing, mjml, xunit, dotnet, regression]
  invocable: false
---

# Snapshot Testing Email Templates with Verify

Capture rendered email HTML and compare it against human-approved baselines. Verify generates `.received.html` files on first run, developers approve them as `.verified.html` files, and subsequent runs detect unintended template changes through diff comparison. Targets .NET 8+ with xUnit and MJML templates.

**Acronyms**: HTML (HyperText Markup Language), MJML (Mailjet Markup Language), CI (Continuous Integration), DI (Dependency Injection), GUID (Globally Unique Identifier).

## When to Use This Skill

- Testing email template rendering to catch CSS and layout regressions automatically
- Validating MJML templates compile to expected HTML output across template variants
- Reviewing email template changes in code review through visual snapshot diffs
- Ensuring variable substitution renders correctly for each recipient scenario
- Verifying email composer output including subject line and metadata fields
- Catching unintended side effects when modifying shared email template partials

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-snapshot-testing` | General Verify snapshot patterns for any .NET output |
| `dotnet-serialization` | Serialization strategies, JSON/XML format configuration |
| `dotnet-testcontainers` | Integration testing with real Docker infrastructure |

## Core Principles

1. **One Test Per Template Variant** — Each email template variant gets its own snapshot test. Why: isolates regression sources so a failure points directly to the affected template.
2. **Scrub Dynamic Values Globally** — Replace timestamps, GUIDs, and tokens with stable placeholders in `ModuleInitializer`. Why: ensures snapshots produce identical results across runs and environments.
3. **Human-Approved Baselines** — Every `.verified.html` requires explicit developer review before acceptance. Why: prevents broken rendering from being silently committed as the new baseline.
4. **Diff-Based Visual Review** — Template changes surface through diff tools and browser preview, not silent assertion failures. Why: visual diffs make unintended CSS and layout changes immediately obvious.
5. **Version Control Integration** — Commit `.verified.html` files and ignore `.received.html` files. Why: baselines are reviewed in PRs and tracked in history alongside template source.

> **Values**: 基礎と型の追求（Verify の「型」—承認ベースライン・スクラブ・差分検出—を守ることで、再現可能なメールテンプレート検証基盤を築く）, ニュートラルな視点（手動目視確認の偏りを排し、スナップショット差分による客観的なレンダリング品質基準を保つ）

## Workflow: Email Template Snapshot Testing with Verify

### Step 1: Install Verify and Configure Test Fixture

Install the Verify NuGet package and create a shared test fixture for email rendering. Why: centralized fixture configuration ensures consistent rendering across all email tests.

```bash
dotnet add package Verify.Xunit
```

```csharp
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

public class EmailTestFixture : IAsyncLifetime
{
    public IServiceProvider Services { get; private set; } = null!;

    public async Task InitializeAsync()
    {
        var services = new ServiceCollection();

        services.AddSingleton<IConfiguration>(new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["SiteUrl"] = "https://example.com"
            })
            .Build());

        services.AddSingleton<IMjmlTemplateRenderer, MjmlTemplateRenderer>();

        Services = services.BuildServiceProvider();
        await Task.CompletedTask;
    }

    public Task DisposeAsync() => Task.CompletedTask;
}
```

> **Values**: 基礎と型の追求（テストフィクスチャという初期化の「型」を最初に整えることで、全メールテストの一貫性を保証する）

### Step 2: Write Basic Email Snapshot Tests

Return `Verify(html, extension: "html")` from test methods to generate snapshot files. Why: Verify captures rendered HTML and compares it against the approved baseline automatically.

```csharp
// ✅ GOOD — descriptive test name becomes the snapshot file name
[Fact]
public async Task UserSignupInvitation_RendersCorrectly()
{
    var renderer = _services.GetRequiredService<IMjmlTemplateRenderer>();

    var variables = new Dictionary<string, string>
    {
        { "PreviewText", "You've been invited to join Acme Corp" },
        { "OrganizationName", "Acme Corporation" },
        { "InviteeName", "John Doe" },
        { "InviterName", "Jane Admin" },
        { "InvitationLink", "https://example.com/invite/abc123" },
        { "ExpirationDate", "December 31, 2025" }
    };

    var html = await renderer.RenderTemplateAsync(
        "UserInvitations/UserSignupInvitation", variables);

    await Verify(html, extension: "html");
}
```

First run creates `UserSignupInvitation_RendersCorrectly.received.html`. Approve it to create `UserSignupInvitation_RendersCorrectly.verified.html`.

> **Values**: 温故知新（テストの命名規則という「過去の知恵」を、スナップショットファイル名の自動生成という新技術と結びつける）

### Step 3: Test Each Template Variant

Create dedicated tests for each email template to catch variant-specific regressions. Why: shared helper methods reduce boilerplate while keeping each variant independently verifiable.

```csharp
public class EmailTemplateSnapshotTests : IClassFixture<EmailTestFixture>
{
    private readonly IMjmlTemplateRenderer _renderer;

    public EmailTemplateSnapshotTests(EmailTestFixture fixture)
    {
        _renderer = fixture.Services.GetRequiredService<IMjmlTemplateRenderer>();
    }

    [Fact]
    public async Task WelcomeEmail_NewUser() =>
        await VerifyTemplate("Welcome/NewUser", new Dictionary<string, string>
        {
            { "UserName", "John Doe" },
            { "LoginUrl", "https://example.com/login" }
        });

    [Fact]
    public async Task PasswordReset() =>
        await VerifyTemplate("PasswordReset/PasswordReset", new Dictionary<string, string>
        {
            { "UserName", "John Doe" },
            { "ResetLink", "https://example.com/reset/abc123" },
            { "ExpirationMinutes", "30" }
        });

    [Fact]
    public async Task PaymentReceipt() =>
        await VerifyTemplate("Billing/PaymentReceipt", new Dictionary<string, string>
        {
            { "UserName", "John Doe" },
            { "Amount", "$10.00" },
            { "InvoiceNumber", "INV-2025-001" },
            { "Date", "January 15, 2025" }
        });

    private async Task VerifyTemplate(
        string templateName, Dictionary<string, string> variables)
    {
        var html = await _renderer.RenderTemplateAsync(templateName, variables);
        await Verify(html, extension: "html")
            .UseMethodName(templateName.Replace("/", "_"));
    }
}
```

> **Values**: 成長の複利（一つの VerifyTemplate ヘルパーを習得すれば、全テンプレートバリアントに横展開でき、知識が複利的に増幅する）

### Step 4: Scrub Dynamic Values for Deterministic Snapshots

Replace non-deterministic data with stable placeholders. Why: timestamps and GUIDs change every run and cause false failures without scrubbing.

```csharp
using System.Runtime.CompilerServices;
using System.Text.RegularExpressions;

public static class ModuleInitializer
{
    [ModuleInitializer]
    public static void Init()
    {
        // Store verified files in a dedicated directory
        VerifyBase.UseProjectRelativeDirectory("Snapshots");

        // Scrub dynamic values globally
        VerifierSettings.ScrubMembersWithType<DateTime>();
        VerifierSettings.ScrubMembersWithType<DateTimeOffset>();
        VerifierSettings.ScrubInlineGuids();

        // Scrub URL tokens and generated timestamps
        VerifierSettings.AddScrubber(s =>
            Regex.Replace(s, @"token=[a-zA-Z0-9]+", "token=SCRUBBED"));
    }
}
```

Per-test scrubbing for email-specific dynamic content:

```csharp
[Fact]
public async Task EmailWithTimestamp_ScrubsDynamicValues()
{
    var html = await _renderer.RenderTemplateAsync("Welcome", variables);

    await Verify(html, extension: "html")
        .ScrubLinesContaining("Generated at:")
        .ScrubInlineGuids();
}
```

> **Values**: 余白の設計（動的値をスクラブすることで、環境差異に対する余白を確保し、どの環境でも同一結果を保証する）

### Step 5: Verify Composer Output and Configure CI

Test the full email composer including subject and metadata, and configure CI integration. Why: composer-level tests catch subject line and recipient errors; CI configuration prevents diff tool hangs.

```csharp
[Fact]
public async Task SignupInvitation_ComposesCorrectEmail()
{
    var composer = _services.GetRequiredService<IUserEmailComposer>();

    var email = await composer.ComposeSignupInvitationAsync(
        recipientEmail: new EmailAddress("john@example.com"),
        recipientName: new PersonName("John Doe"),
        inviterName: new PersonName("Jane Admin"),
        organizationName: new OrganizationName("Acme Corp"),
        invitationUrl: new AbsoluteUri("https://example.com/invite/abc123"),
        expiresAt: new DateTimeOffset(2025, 12, 31, 0, 0, 0, TimeSpan.Zero));

    await Verify(new { email.To, email.Subject, email.HtmlBody });
}
```

**CI configuration — disable diff tool and fail on missing baselines:**

```csharp
[ModuleInitializer]
public static void Init()
{
    if (Environment.GetEnvironmentVariable("CI") == "true")
    {
        VerifyDiffPlex.UseDiffPlex(OutputType.Minimal);
        DiffRunner.Disabled = true;
    }

    // Fail if no baseline exists
    VerifierSettings.ThrowOnMissingVerifiedFile();
}
```

**Git configuration for snapshot files:**

```gitignore
*.received.*
```

```gitattributes
*.verified.html linguist-generated=true
*.verified.html diff=html
```

> **Values**: 継続は力（CI パイプラインでのスナップショット検証を自動化し、継続的にリグレッションを検出する仕組みを構築する）

## Good Practices

- ✅ Use descriptive test names — they become snapshot file names for easy identification
- ✅ Create one test per email template variant to isolate regression sources
- ✅ Use the `extension: "html"` parameter for rendered email output
- ✅ Scrub all dynamic values globally via `ModuleInitializer` to avoid per-test repetition
- ✅ Commit `.verified.html` files to source control and review changes in pull requests
- ✅ Use `linguist-generated=true` in `.gitattributes` to collapse snapshot diffs in PRs
- ✅ Disable diff tool launching in CI with `DiffRunner.Disabled = true`
- ✅ Open `.received.html` in a browser to preview actual email rendering

## Common Pitfalls

1. **Unscrubbed Dynamic Values** — GUIDs and timestamps cause email snapshots to fail on every run. Fix: use `ScrubInlineGuids()` and `ScrubMembersWithType<DateTime>()` in `ModuleInitializer`.
2. **Committing Received Files** — Adding `*.received.html` to source control creates noise and merge conflicts. Fix: add `*.received.*` to `.gitignore` immediately.
3. **Diff Tool Launches in CI** — Verify tries to open a diff tool, causing CI to hang indefinitely. Fix: set `DiffRunner.Disabled = true` when `CI` environment variable is detected.
4. **Generic Test Names** — Names like `Test1` produce unidentifiable snapshot files. Fix: use descriptive names like `WelcomeEmail_NewUser_RendersCorrectly`.
5. **Missing Template Variant Coverage** — Testing only one variant misses regressions in others. Fix: create separate tests for each template variant using a shared `VerifyTemplate` helper method.

## Anti-Patterns

### ❌ Auto-Accepting Without Review → ✅ Review Diffs Before Accepting

```csharp
// ❌ BAD — blindly accepting all changes without review
// verify accept --all
// This may commit broken rendering as the new baseline

// ✅ GOOD — review each change in diff tool or browser
// verify review
// Open .received.html in browser to verify rendering
```

Why: auto-accepting bypasses the human review that is the foundation of snapshot testing quality.

### ❌ Testing Only Happy Path → ✅ Cover Each Template Variant

```csharp
// ❌ BAD — only testing one email template
[Fact] public Task WelcomeEmail_Renders() => VerifyTemplate("Welcome");

// ✅ GOOD — testing each variant independently
[Fact] public Task WelcomeEmail_NewUser() => VerifyTemplate("Welcome/NewUser");
[Fact] public Task WelcomeEmail_InvitedUser() => VerifyTemplate("Welcome/InvitedUser");
[Fact] public Task PasswordReset() => VerifyTemplate("PasswordReset");
```

Why: each template variant can regress independently; full coverage catches all rendering issues.

### ❌ Monolithic Email Snapshots → ✅ Focused Projections

```csharp
// ❌ BAD — captures entire composer result with irrelevant metadata
await Verify(emailResult);

// ✅ GOOD — focuses on the fields that matter for email verification
await Verify(new { emailResult.Subject, emailResult.HtmlBody });
```

Why: monolithic snapshots break on any field change, making it hard to identify the actual rendering regression.

## Quick Reference

### Email Snapshot Testing Decision Table

| Scenario | Use Snapshot? | Why |
|----------|--------------|-----|
| Rendered HTML email templates | ✅ Yes | Catches visual and layout regressions |
| Email subject line composition | ✅ Yes | Detects unintended subject changes |
| Variable substitution output | ✅ Yes | Validates dynamic content rendering |
| Email recipient address logic | ❌ No | Use `Assert.Equal` directly |
| SMTP delivery success | ❌ No | Use integration tests with Mailpit |

### Verify API for Email Testing

| Method | Purpose | Example |
|--------|---------|---------|
| `Verify(html, extension: "html")` | Snapshot rendered email | `await Verify(html, extension: "html");` |
| `.UseMethodName(name)` | Override snapshot file name | `.UseMethodName("Welcome_NewUser");` |
| `.ScrubLinesContaining(text)` | Remove dynamic lines | `.ScrubLinesContaining("Generated at:");` |
| `.ScrubInlineGuids()` | Replace GUIDs in URLs | `.ScrubInlineGuids();` |
| `DiffRunner.Disabled` | Disable diff tool in CI | `DiffRunner.Disabled = true;` |

### Review Workflow

| Step | Command | Purpose |
|------|---------|---------|
| Run tests | `dotnet test` | Detect snapshot changes |
| Review diffs | `verify review` | Open diff tool for comparison |
| Preview in browser | Open `.received.html` | Visual rendering check |
| Accept changes | `verify accept` | Approve new baseline |
| Commit baselines | `git add *.verified.html` | Track in version control |

## Resources

- [Verify GitHub](https://github.com/VerifyTests/Verify) — Main repository and documentation
- [Verify.Xunit](https://github.com/VerifyTests/Verify.Xunit) — xUnit integration package
- [DiffEngine](https://github.com/VerifyTests/DiffEngine) — Diff tool configuration
- [Verify.DiffPlex](https://github.com/VerifyTests/Verify.DiffPlex) — Inline diff for CI environments
