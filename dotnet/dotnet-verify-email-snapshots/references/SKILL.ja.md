---
name: dotnet-verify-email-snapshots
description: >
  Verify スナップショットテストを使用してメールテンプレートのレンダリングリグレッションを検出する。
  レンダリングされた HTML 出力が承認済みベースラインと一致することを検証し、MJML をサポートする。
  Use when メールテンプレートのレンダリングを人間が承認したスナップショットで検証する場合に使用。
metadata:
  author: RyoMurakami1983
  tags: [verify, snapshot-testing, email-testing, mjml, xunit, dotnet, regression]
  invocable: false
---

<!-- このドキュメントは dotnet-verify-email-snapshots の日本語版です。英語版: ../SKILL.md -->

# Snapshot Testing Email Templates with Verify

レンダリングされたメール HTML をキャプチャし、人間が承認したベースラインと比較する。Verify は初回実行時に `.received.html` ファイルを生成し、開発者がそれを `.verified.html` ファイルとして承認し、以降の実行で差分比較により意図しないテンプレート変更を検出する。.NET 8+ と xUnit、MJML テンプレートを対象とする。

**略語**: HTML（HyperText Markup Language）、MJML（Mailjet Markup Language）、CI（Continuous Integration）、DI（Dependency Injection）、GUID（Globally Unique Identifier）。

## When to Use This Skill

- メールテンプレートのレンダリングをテストし、CSS やレイアウトのリグレッションを自動検出する
- MJML テンプレートが期待通りの HTML 出力にコンパイルされることをバリアント別に検証する
- コードレビューでメールテンプレートの変更を視覚的なスナップショット差分で確認する
- 各受信者シナリオで変数置換が正しくレンダリングされることを保証する
- サブジェクトラインとメタデータフィールドを含むメールコンポーザー出力を検証する
- 共有メールテンプレートパーシャルの変更による意図しない副作用を検出する

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-snapshot-testing` | あらゆる .NET 出力に対する汎用 Verify スナップショットパターン |
| `dotnet-serialization` | シリアライズ戦略、JSON/XML フォーマット設定 |
| `dotnet-testcontainers` | Docker 実インフラを使った統合テスト |

## Core Principles

1. **One Test Per Template Variant** — 各メールテンプレートバリアントにそれぞれ専用のスナップショットテストを作成する。理由：リグレッション源を分離し、失敗時に影響を受けたテンプレートを直接特定するため。
2. **Scrub Dynamic Values Globally** — タイムスタンプ、GUID、トークンを `ModuleInitializer` で安定したプレースホルダーに置換する。理由：スナップショットが実行環境に関わらず同一結果を生成することを保証するため。
3. **Human-Approved Baselines** — すべての `.verified.html` は受け入れ前に開発者の明示的なレビューを必要とする。理由：壊れたレンダリングが新しいベースラインとしてサイレントにコミットされるのを防ぐため。
4. **Diff-Based Visual Review** — テンプレート変更は差分ツールとブラウザプレビューで表面化し、サイレントなアサーション失敗ではない。理由：視覚的な差分により意図しない CSS やレイアウトの変更が即座に明確になるため。
5. **Version Control Integration** — `.verified.html` ファイルをコミットし、`.received.html` ファイルを無視する。理由：ベースラインがテンプレートソースと共に PR でレビューされ、履歴で追跡されるため。

> **Values**: 基礎と型の追求（Verify の「型」—承認ベースライン・スクラブ・差分検出—を守ることで、再現可能なメールテンプレート検証基盤を築く）, ニュートラルな視点（手動目視確認の偏りを排し、スナップショット差分による客観的なレンダリング品質基準を保つ）

## Workflow: Email Template Snapshot Testing with Verify

### Step 1: Install Verify and Configure Test Fixture

Verify NuGet パッケージをインストールし、メールレンダリング用の共有テストフィクスチャを作成する。理由：集中化されたフィクスチャ設定により全メールテストで一貫したレンダリングを保証するため。

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

テストメソッドから `Verify(html, extension: "html")` を返してスナップショットファイルを生成する。理由：Verify がレンダリングされた HTML をキャプチャし、承認済みベースラインと自動比較するため。

```csharp
// ✅ GOOD — 記述的なテスト名がスナップショットファイル名になる
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

初回実行で `UserSignupInvitation_RendersCorrectly.received.html` が作成される。承認すると `UserSignupInvitation_RendersCorrectly.verified.html` になる。

> **Values**: 温故知新（テストの命名規則という「過去の知恵」を、スナップショットファイル名の自動生成という新技術と結びつける）

### Step 3: Test Each Template Variant

各メールテンプレートに専用テストを作成し、バリアント固有のリグレッションを検出する。理由：共有ヘルパーメソッドがボイラープレートを削減しつつ、各バリアントを独立して検証可能にするため。

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

非決定的データを安定したプレースホルダーに置換する。理由：タイムスタンプと GUID はスクラブなしでは毎回変化し、偽の失敗を引き起こすため。

```csharp
using System.Runtime.CompilerServices;
using System.Text.RegularExpressions;

public static class ModuleInitializer
{
    [ModuleInitializer]
    public static void Init()
    {
        // 検証済みファイルを専用ディレクトリに格納
        VerifyBase.UseProjectRelativeDirectory("Snapshots");

        // 動的値をグローバルにスクラブ
        VerifierSettings.ScrubMembersWithType<DateTime>();
        VerifierSettings.ScrubMembersWithType<DateTimeOffset>();
        VerifierSettings.ScrubInlineGuids();

        // URL トークンと生成タイムスタンプをスクラブ
        VerifierSettings.AddScrubber(s =>
            Regex.Replace(s, @"token=[a-zA-Z0-9]+", "token=SCRUBBED"));
    }
}
```

テストごとのメール固有動的コンテンツのスクラブ：

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

サブジェクトとメタデータを含むフルメールコンポーザーをテストし、CI 統合を設定する。理由：コンポーザーレベルのテストがサブジェクトラインと受信者のエラーを検出し、CI 設定が差分ツールのハングを防止するため。

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

**CI 設定 — 差分ツール無効化とベースライン欠損時の失敗：**

```csharp
[ModuleInitializer]
public static void Init()
{
    if (Environment.GetEnvironmentVariable("CI") == "true")
    {
        VerifyDiffPlex.UseDiffPlex(OutputType.Minimal);
        DiffRunner.Disabled = true;
    }

    // ベースラインが存在しない場合は失敗
    VerifierSettings.ThrowOnMissingVerifiedFile();
}
```

**スナップショットファイルの Git 設定：**

```gitignore
*.received.*
```

```gitattributes
*.verified.html linguist-generated=true
*.verified.html diff=html
```

> **Values**: 継続は力（CI パイプラインでのスナップショット検証を自動化し、継続的にリグレッションを検出する仕組みを構築する）

## Good Practices

- ✅ 記述的なテスト名を使用する — スナップショットファイル名として識別が容易になる
- ✅ テンプレートバリアントごとに一つのテストを作成し、リグレッション源を分離する
- ✅ レンダリングされたメール出力には `extension: "html"` パラメータを使用する
- ✅ `ModuleInitializer` でグローバルに動的値をスクラブし、テストごとの繰り返しを避ける
- ✅ `.verified.html` ファイルをソース管理にコミットし、PR で変更をレビューする
- ✅ `.gitattributes` で `linguist-generated=true` を使用して PR のスナップショット差分を折りたたむ
- ✅ CI では `DiffRunner.Disabled = true` で差分ツール起動を無効化する
- ✅ `.received.html` をブラウザで開いて実際のメールレンダリングをプレビューする

## Common Pitfalls

1. **Unscrubbed Dynamic Values** — GUID やタイムスタンプがメールスナップショットを毎回失敗させる。修正：`ModuleInitializer` で `ScrubInlineGuids()` と `ScrubMembersWithType<DateTime>()` を使用する。
2. **Committing Received Files** — `*.received.html` をソース管理に追加するとノイズとマージコンフリクトが発生する。修正：直ちに `*.received.*` を `.gitignore` に追加する。
3. **Diff Tool Launches in CI** — Verify が差分ツールを開こうとし、CI が無期限にハングする。修正：`CI` 環境変数を検出して `DiffRunner.Disabled = true` を設定する。
4. **Generic Test Names** — `Test1` のような名前は識別不可能なスナップショットファイルを生成する。修正：`WelcomeEmail_NewUser_RendersCorrectly` のような記述的な名前を使用する。
5. **Missing Template Variant Coverage** — 一つのバリアントだけテストすると他のリグレッションを見逃す。修正：共有 `VerifyTemplate` ヘルパーメソッドを使用して各テンプレートバリアントに個別テストを作成する。

## Anti-Patterns

### ❌ Auto-Accepting Without Review → ✅ Review Diffs Before Accepting

```csharp
// ❌ BAD — レビューなしで全変更を盲目的に受け入れ
// verify accept --all
// 壊れたレンダリングが新しいベースラインとしてコミットされる可能性

// ✅ GOOD — 差分ツールまたはブラウザで各変更をレビュー
// verify review
// .received.html をブラウザで開いてレンダリングを検証
```

理由：自動受け入れはスナップショットテスト品質の基盤である人間のレビューをバイパスする。

### ❌ Testing Only Happy Path → ✅ Cover Each Template Variant

```csharp
// ❌ BAD — 一つのメールテンプレートだけテスト
[Fact] public Task WelcomeEmail_Renders() => VerifyTemplate("Welcome");

// ✅ GOOD — 各バリアントを独立してテスト
[Fact] public Task WelcomeEmail_NewUser() => VerifyTemplate("Welcome/NewUser");
[Fact] public Task WelcomeEmail_InvitedUser() => VerifyTemplate("Welcome/InvitedUser");
[Fact] public Task PasswordReset() => VerifyTemplate("PasswordReset");
```

理由：各テンプレートバリアントは独立してリグレッションし得る。完全なカバレッジがすべてのレンダリング問題を検出する。

### ❌ Monolithic Email Snapshots → ✅ Focused Projections

```csharp
// ❌ BAD — 無関係なメタデータを含むコンポーザー結果全体をキャプチャ
await Verify(emailResult);

// ✅ GOOD — メール検証に重要なフィールドにフォーカス
await Verify(new { emailResult.Subject, emailResult.HtmlBody });
```

理由：モノリシックなスナップショットはあらゆるフィールド変更で壊れ、実際のレンダリングリグレッション特定を困難にする。

## Quick Reference

### Email Snapshot Testing Decision Table

| Scenario | Use Snapshot? | Why |
|----------|--------------|-----|
| Rendered HTML email templates | ✅ Yes | 視覚・レイアウトのリグレッションを検出 |
| Email subject line composition | ✅ Yes | 意図しないサブジェクト変更を検出 |
| Variable substitution output | ✅ Yes | 動的コンテンツのレンダリングを検証 |
| Email recipient address logic | ❌ No | `Assert.Equal` を直接使用 |
| SMTP delivery success | ❌ No | Mailpit を使った統合テストを使用 |

### Verify API for Email Testing

| Method | Purpose | Example |
|--------|---------|---------|
| `Verify(html, extension: "html")` | レンダリングされたメールのスナップショット | `await Verify(html, extension: "html");` |
| `.UseMethodName(name)` | スナップショットファイル名のオーバーライド | `.UseMethodName("Welcome_NewUser");` |
| `.ScrubLinesContaining(text)` | 動的行の除去 | `.ScrubLinesContaining("Generated at:");` |
| `.ScrubInlineGuids()` | URL 内の GUID を置換 | `.ScrubInlineGuids();` |
| `DiffRunner.Disabled` | CI で差分ツール無効化 | `DiffRunner.Disabled = true;` |

### Review Workflow

| Step | Command | Purpose |
|------|---------|---------|
| テスト実行 | `dotnet test` | スナップショット変更を検出 |
| 差分レビュー | `verify review` | 差分ツールで比較 |
| ブラウザプレビュー | `.received.html` を開く | 視覚的レンダリング確認 |
| 変更の受け入れ | `verify accept` | 新しいベースラインを承認 |
| ベースラインのコミット | `git add *.verified.html` | バージョン管理で追跡 |

## Resources

- [Verify GitHub](https://github.com/VerifyTests/Verify) — メインリポジトリとドキュメント
- [Verify.Xunit](https://github.com/VerifyTests/Verify.Xunit) — xUnit 統合パッケージ
- [DiffEngine](https://github.com/VerifyTests/DiffEngine) — 差分ツール設定
- [Verify.DiffPlex](https://github.com/VerifyTests/Verify.DiffPlex) — CI 環境向けインライン差分
