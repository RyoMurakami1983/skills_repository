---
name: dotnet-mjml-email-templates
description: >
  Build responsive email templates using MJML markup language in .NET.
  Compiles to cross-client HTML that works in Outlook, Gmail, and Apple Mail.
  Includes template renderer, layout patterns, composer pattern, and variable substitution.
  Use when creating transactional or notification emails that must render correctly across all major email clients.
metadata:
  author: RyoMurakami1983
  tags: [mjml, email, templates, dotnet, responsive, outlook, gmail, transactional]
  invocable: false
---

# MJML Email Templates for .NET

Build responsive, cross-client email templates using MJML markup compiled to HTML via Mjml.Net. Targets .NET 8+ with embedded resource templates, layout composition, and strongly-typed email composers.

**Acronyms**: MJML (Mailjet Markup Language), HTML (HyperText Markup Language), CSS (Cascading Style Sheets), DI (Dependency Injection), CI (Continuous Integration).

## When to Use This Skill

- Building transactional emails (signup invitations, password reset, invoices, notifications)
- Creating responsive email templates that render consistently across Outlook, Gmail, and Apple Mail
- Setting up MJML template rendering with layout composition in a .NET project
- Replacing hand-coded table-based HTML emails with maintainable MJML markup
- Separating email composition logic from template rendering with strongly-typed composers

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-snapshot-testing` | Snapshot test rendered HTML email output with Verify |
| `dotnet-extensions-dependency-injection` | Register template renderer and composers in DI container |
| `dotnet-serialization` | Serialization strategies for email message value objects |

## Core Principles

1. **Layout Composition** — Separate shared structure (header, footer, styles) from per-email content using a layout template with content injection. Why: eliminates duplication and ensures brand consistency across all emails.
2. **Strongly-Typed Composers** — Use value objects for email addresses, person names, and URLs instead of raw strings. Why: prevents invalid data from reaching the template renderer and makes APIs self-documenting.
3. **Embedded Resource Templates** — Store MJML templates as embedded resources in the assembly. Why: templates deploy with the application binary, eliminating file path issues across environments.
4. **Variable Substitution** — Replace `{{Placeholder}}` tokens with runtime values using regex-based substitution. Why: keeps templates static and testable while allowing dynamic content injection.
5. **Cross-Client Compatibility** — Let MJML handle table-based layout generation instead of writing raw HTML. Why: MJML compiles simple markup to ~200 lines of inline-styled HTML that works across all email clients.

> **Values**: 基礎と型の追求（MJML の「型」—レイアウト合成・変数置換・埋め込みリソース—を守ることで、再現可能なメール生成基盤を築く）, ニュートラルな視点（メールクライアント間の差異を MJML コンパイラに委ね、偏りのないレンダリング品質を保つ）

## Workflow: MJML Email Templates in .NET

### Step 1: Install Mjml.Net and Configure Embedded Resources

Add the Mjml.Net NuGet package and configure MJML templates as embedded resources. Why: embedded resources ensure templates are bundled with the assembly and available in all deployment environments.

```bash
dotnet add package Mjml.Net
```

In your `.csproj`:

```xml
<ItemGroup>
  <EmbeddedResource Include="Templates\**\*.mjml" />
</ItemGroup>
```

> **Values**: 基礎と型の追求（埋め込みリソースという「型」を最初に整え、環境に依存しないテンプレート配信を保証する）

### Step 2: Create the Layout Template

Define a shared layout with header, content slot, and footer that all emails inherit. Why: centralized layout ensures consistent branding and reduces per-template boilerplate.

```mjml
<!-- Templates/_Layout.mjml -->
<mjml>
  <mj-head>
    <mj-title>MyApp</mj-title>
    <mj-preview>{{PreviewText}}</mj-preview>
    <mj-attributes>
      <mj-all font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" />
      <mj-text font-size="14px" color="#555555" line-height="20px" />
      <mj-section padding="20px" />
    </mj-attributes>
    <mj-style inline="inline">
      a { color: #2563eb; text-decoration: none; }
      a:hover { text-decoration: underline; }
    </mj-style>
  </mj-head>
  <mj-body background-color="#f3f4f6">
    <mj-section background-color="#ffffff" padding-bottom="0">
      <mj-column>
        <mj-image src="https://myapp.com/logo.png" alt="MyApp"
          width="150px" href="{{SiteUrl}}" padding="30px 25px 20px 25px" />
      </mj-column>
    </mj-section>

    <!-- Content injected here -->
    <mj-section background-color="#ffffff" padding-top="20px" padding-bottom="40px">
      <mj-column>
        {{Content}}
      </mj-column>
    </mj-section>

    <mj-section background-color="#f9fafb" padding="20px 25px">
      <mj-column>
        <mj-text align="center" font-size="12px" color="#9ca3af">
          &copy; 2025 MyApp Inc. All rights reserved.
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
```

> **Values**: 温故知新（メールの共通構造をレイアウトテンプレートに集約し、過去のブランド資産を新しいメールに自然に継承する）

### Step 3: Create Content Templates

Write per-email content templates using MJML components. The layout template wraps them automatically. Why: content templates focus only on email-specific markup, keeping them small and maintainable.

```mjml
<!-- Templates/UserInvitations/UserSignupInvitation.mjml -->
<mj-text font-size="16px" color="#111827" font-weight="600" padding-bottom="20px">
  You've been invited to join {{OrganizationName}}
</mj-text>

<mj-text padding-bottom="15px">
  Hi {{InviteeName}},
</mj-text>

<mj-text padding-bottom="15px">
  {{InviterName}} has invited you to join <strong>{{OrganizationName}}</strong>.
</mj-text>

<mj-text padding-bottom="25px">
  Click the button below to accept your invitation:
</mj-text>

<mj-button background-color="#2563eb" color="#ffffff" font-size="16px"
  href="{{InvitationLink}}">
  Accept Invitation
</mj-button>

<mj-text padding-top="25px" font-size="13px" color="#6b7280">
  This invitation expires on {{ExpirationDate}}.
</mj-text>
```

> **Values**: 基礎と型の追求（コンテンツテンプレートをレイアウトから分離する「型」により、各メールの関心事を最小限に保つ）

### Step 4: Build the Template Renderer

Implement a renderer that loads embedded MJML templates, injects content into the layout, substitutes variables, and compiles to HTML. Why: encapsulating the render pipeline behind an interface enables testing and DI registration.

```csharp
public interface IMjmlTemplateRenderer
{
    Task<string> RenderTemplateAsync(
        string templateName,
        IReadOnlyDictionary<string, string> variables,
        CancellationToken ct = default);
}

public sealed partial class MjmlTemplateRenderer : IMjmlTemplateRenderer
{
    private readonly MjmlRenderer _mjmlRenderer = new();
    private readonly Assembly _assembly;
    private readonly string _siteUrl;

    public MjmlTemplateRenderer(IConfiguration config)
    {
        _assembly = typeof(MjmlTemplateRenderer).Assembly;
        _siteUrl = config["SiteUrl"] ?? "https://myapp.com";
    }

    public async Task<string> RenderTemplateAsync(
        string templateName,
        IReadOnlyDictionary<string, string> variables,
        CancellationToken ct = default)
    {
        var contentMjml = await LoadTemplateAsync(templateName, ct);
        var layoutMjml = await LoadTemplateAsync("_Layout", ct);
        var combinedMjml = layoutMjml.Replace("{{Content}}", contentMjml);

        var allVariables = new Dictionary<string, string> { { "SiteUrl", _siteUrl } };
        foreach (var kvp in variables)
            allVariables[kvp.Key] = kvp.Value;

        var processedMjml = SubstituteVariables(combinedMjml, allVariables);
        var result = await _mjmlRenderer.RenderAsync(processedMjml, null, ct);

        if (result.Errors.Any())
            throw new InvalidOperationException(
                $"MJML compilation failed: {string.Join(", ", result.Errors.Select(e => e.Error))}");

        return result.Html;
    }

    private async Task<string> LoadTemplateAsync(string templateName, CancellationToken ct)
    {
        var resourceName = $"MyApp.Infrastructure.Mailing.Templates.{templateName.Replace('/', '.')}.mjml";
        await using var stream = _assembly.GetManifestResourceStream(resourceName)
            ?? throw new FileNotFoundException($"Template '{templateName}' not found");
        using var reader = new StreamReader(stream);
        return await reader.ReadToEndAsync(ct);
    }

    private static string SubstituteVariables(string mjml, IReadOnlyDictionary<string, string> variables)
    {
        return VariableRegex().Replace(mjml, match =>
        {
            var name = match.Groups[1].Value;
            return variables.TryGetValue(name, out var value) ? value : match.Value;
        });
    }

    [GeneratedRegex(@"\{\{([^}]+)\}\}", RegexOptions.Compiled)]
    private static partial Regex VariableRegex();
}
```

> **Values**: 成長の複利（インターフェース抽象化により、テスト・モック・将来の実装差し替えが容易になり、チーム全体の生産性が複利的に向上する）

### Step 5: Implement the Email Composer Pattern

Separate template rendering from email composition with strongly-typed value objects. Why: composers enforce type safety at the boundary and make email construction self-documenting.

```csharp
public interface IUserEmailComposer
{
    Task<EmailMessage> ComposeSignupInvitationAsync(
        EmailAddress recipientEmail,
        PersonName recipientName,
        PersonName inviterName,
        OrganizationName organizationName,
        AbsoluteUri invitationUrl,
        DateTimeOffset expiresAt,
        CancellationToken ct = default);
}

public sealed class UserEmailComposer : IUserEmailComposer
{
    private readonly IMjmlTemplateRenderer _renderer;

    public UserEmailComposer(IMjmlTemplateRenderer renderer)
        => _renderer = renderer;

    public async Task<EmailMessage> ComposeSignupInvitationAsync(
        EmailAddress recipientEmail,
        PersonName recipientName,
        PersonName inviterName,
        OrganizationName organizationName,
        AbsoluteUri invitationUrl,
        DateTimeOffset expiresAt,
        CancellationToken ct = default)
    {
        var variables = new Dictionary<string, string>
        {
            { "PreviewText", $"You've been invited to join {organizationName.Value}" },
            { "InviteeName", recipientName.Value },
            { "InviterName", inviterName.Value },
            { "OrganizationName", organizationName.Value },
            { "InvitationLink", invitationUrl.ToString() },
            { "ExpirationDate", expiresAt.ToString("MMMM d, yyyy") }
        };

        var html = await _renderer.RenderTemplateAsync(
            "UserInvitations/UserSignupInvitation", variables, ct);

        return new EmailMessage(
            To: recipientEmail,
            Subject: $"You've been invited to join {organizationName.Value}",
            HtmlBody: html);
    }
}
```

> **Values**: 基礎と型の追求（値オブジェクトによる型安全な境界を設け、不正データがレンダラーに到達することを構造的に防ぐ）

### Step 6: Add Email Preview Endpoint

Create an admin endpoint to preview rendered emails during development. Why: visual preview shortens the feedback loop and catches rendering issues before deployment.

```csharp
app.MapGet("/admin/emails/preview/{template}", async (
    string template,
    IMjmlTemplateRenderer renderer) =>
{
    var sampleVariables = GetSampleVariables(template);
    var html = await renderer.RenderTemplateAsync(template, sampleVariables);
    return Results.Content(html, "text/html");
})
.RequireAuthorization("AdminOnly");
```

> **Values**: 継続は力（プレビューエンドポイントにより、メールテンプレートの反復改善サイクルを高速化し、継続的な品質向上を支える）

## Good Practices

- ✅ Use MJML components (`mj-section`, `mj-column`, `mj-text`) instead of raw HTML tables
- ✅ Store templates as embedded resources to avoid file path issues across environments
- ✅ Use a shared layout template for consistent header, footer, and styling across all emails
- ✅ Use strongly-typed value objects (`EmailAddress`, `PersonName`) in composer method signatures
- ✅ Use production absolute URLs for images — relative paths break in email clients
- ✅ Add a development preview endpoint gated behind admin authorization
- ✅ Validate MJML compilation errors and throw with descriptive messages
- ✅ Organize templates by domain (UserInvitations, PasswordReset, Billing) in subdirectories

## Common Pitfalls

1. **Raw HTML Tables in Templates** — Writing table-based layouts manually instead of using MJML components. Fix: use `mj-section` and `mj-column` for all layout needs.
2. **Relative Image URLs** — Using `/img/logo.png` which breaks in email clients. Fix: always use absolute production URLs like `https://myapp.com/logo.png`.
3. **Unsanitized Variable Values** — Injecting user input directly into templates without escaping. Fix: HTML-encode variable values before substitution.
4. **Missing Error Handling on Compilation** — Ignoring `result.Errors` from MJML compilation. Fix: check errors and throw with descriptive messages.
5. **Hardcoded Site URLs** — Embedding environment-specific URLs in templates. Fix: pass URLs as variables via configuration.

## Anti-Patterns

### ❌ Raw HTML Tables → ✅ Use MJML Components

```mjml
<!-- ❌ BAD — brittle table layout that breaks across clients -->
<table><tr><td>Content</td></tr></table>

<!-- ✅ GOOD — MJML handles cross-client table generation -->
<mj-section>
  <mj-column>
    <mj-text>Content</mj-text>
  </mj-column>
</mj-section>
```

Why: MJML compiles to tested, inline-styled table HTML that works across all major email clients.

### ❌ Raw String Parameters → ✅ Strongly-Typed Value Objects

```csharp
// ❌ BAD — no validation, easy to swap parameters
Task<EmailMessage> ComposeAsync(string email, string name, string url);

// ✅ GOOD — self-documenting, validated at construction
Task<EmailMessage> ComposeAsync(EmailAddress to, PersonName name, AbsoluteUri actionUrl);
```

Why: value objects enforce invariants at construction time and prevent parameter ordering mistakes.

### ❌ Inline Styles in Templates → ✅ Use mj-attributes

```mjml
<!-- ❌ BAD — repeated inline styles across every element -->
<mj-text font-size="14px" color="#555" font-family="Arial">Text 1</mj-text>
<mj-text font-size="14px" color="#555" font-family="Arial">Text 2</mj-text>

<!-- ✅ GOOD — centralized defaults in mj-head -->
<mj-attributes>
  <mj-text font-size="14px" color="#555555" font-family="Arial" />
</mj-attributes>
```

Why: centralized attributes reduce duplication and make global style changes a single-line edit.

## Quick Reference

### Project Structure

```
src/Infrastructure/MyApp.Infrastructure.Mailing/
  Templates/
    _Layout.mjml
    UserInvitations/UserSignupInvitation.mjml
    PasswordReset/PasswordReset.mjml
    Billing/PaymentReceipt.mjml
  Mjml/
    IMjmlTemplateRenderer.cs
    MjmlTemplateRenderer.cs
  Composers/
    IUserEmailComposer.cs
    UserEmailComposer.cs
```

### MJML Components Cheat Sheet

| Component | Purpose | Example |
|-----------|---------|---------|
| `<mj-section>` | Horizontal row container | `<mj-section background-color="#fff">` |
| `<mj-column>` | Vertical column within section | `<mj-column width="50%">` |
| `<mj-text>` | Text block with styling | `<mj-text font-size="14px">Hello</mj-text>` |
| `<mj-button>` | Call-to-action button | `<mj-button href="{{Url}}">Click</mj-button>` |
| `<mj-image>` | Responsive image | `<mj-image src="https://..." />` |
| `<mj-divider>` | Horizontal separator | `<mj-divider border-color="#eee" />` |
| `<mj-spacer>` | Vertical spacing | `<mj-spacer height="20px" />` |

### Template Variable Convention

| Variable | Source | Example |
|----------|--------|---------|
| `{{SiteUrl}}` | Configuration | `https://myapp.com` |
| `{{PreviewText}}` | Composer | Email client preview text |
| `{{InviteeName}}` | Composer | Recipient display name |
| `{{ActionUrl}}` | Composer | CTA button target URL |
| `{{ExpirationDate}}` | Composer | Formatted date string |

## Resources

- [MJML Documentation](https://documentation.mjml.io/) — Official MJML component reference and guides
- [MJML Playground](https://mjml.io/try-it-live) — Live editor for prototyping templates
- [Mjml.Net](https://github.com/ArtZab/Mjml.Net) — .NET MJML compiler library
- [Litmus](https://www.litmus.com/) — Email client rendering preview and testing
