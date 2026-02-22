---
name: dotnet-mjml-email-templates
description: >
  MJML マークアップ言語を使用して .NET でレスポンシブなメールテンプレートを構築する。
  Outlook、Gmail、Apple Mail で動作するクロスクライアント HTML にコンパイルする。
  テンプレートレンダラー、レイアウトパターン、コンポーザーパターン、変数置換を含む。
  Use when トランザクションメールや通知メールを主要メールクライアント全体で正しくレンダリングする必要がある場合に使用。
metadata:
  author: RyoMurakami1983
  tags: [mjml, email, templates, dotnet, responsive, outlook, gmail, transactional]
  invocable: false
---

<!-- このドキュメントは dotnet-mjml-email-templates の日本語版です。英語版: ../SKILL.md -->

# MJML Email Templates for .NET

MJML マークアップを Mjml.Net 経由で HTML にコンパイルし、レスポンシブなクロスクライアントメールテンプレートを構築する。.NET 8+ を対象とし、埋め込みリソーステンプレート、レイアウト合成、型安全なメールコンポーザーを使用する。

**略語**: MJML（Mailjet Markup Language）、HTML（HyperText Markup Language）、CSS（Cascading Style Sheets）、DI（Dependency Injection）、CI（Continuous Integration）。

## When to Use This Skill

- トランザクションメール（サインアップ招待、パスワードリセット、請求書、通知）を構築する
- Outlook、Gmail、Apple Mail で一貫してレンダリングされるレスポンシブなメールテンプレートを作成する
- .NET プロジェクトでレイアウト合成を伴う MJML テンプレートレンダリングを構築する
- 手書きのテーブルベース HTML メールを保守性の高い MJML マークアップに置き換える
- メール作成ロジックを型安全なコンポーザーでテンプレートレンダリングから分離する

## Related Skills

| Skill | Scope |
|-------|-------|
| `dotnet-snapshot-testing` | Verify を使用してレンダリングされた HTML メール出力をスナップショットテストする |
| `dotnet-extensions-dependency-injection` | テンプレートレンダラーとコンポーザーを DI コンテナに登録する |
| `dotnet-serialization` | メールメッセージ値オブジェクトのシリアライズ戦略 |

## Core Principles

1. **Layout Composition** — 共有構造（ヘッダー、フッター、スタイル）をメールごとのコンテンツからレイアウトテンプレートで分離する。理由：重複を排除し、全メールでブランドの一貫性を保証するため。
2. **Strongly-Typed Composers** — メールアドレス、人名、URL に生の文字列ではなく値オブジェクトを使用する。理由：不正データがテンプレートレンダラーに到達するのを防ぎ、API を自己文書化するため。
3. **Embedded Resource Templates** — MJML テンプレートをアセンブリの埋め込みリソースとして格納する。理由：テンプレートがアプリケーションバイナリと共にデプロイされ、環境間のファイルパス問題を解消するため。
4. **Variable Substitution** — `{{Placeholder}}` トークンを正規表現ベースの置換でランタイム値に置き換える。理由：テンプレートを静的かつテスト可能に保ちながら、動的コンテンツ注入を可能にするため。
5. **Cross-Client Compatibility** — 生の HTML を書く代わりに MJML にテーブルベースレイアウト生成を委ねる。理由：MJML がシンプルなマークアップを全メールクライアントで動作するインラインスタイル付き HTML にコンパイルするため。

> **Values**: 基礎と型の追求（MJML の「型」—レイアウト合成・変数置換・埋め込みリソース—を守ることで、再現可能なメール生成基盤を築く）, ニュートラルな視点（メールクライアント間の差異を MJML コンパイラに委ね、偏りのないレンダリング品質を保つ）

## Workflow: MJML Email Templates in .NET

### Step 1: Install Mjml.Net and Configure Embedded Resources

Mjml.Net NuGet パッケージを追加し、MJML テンプレートを埋め込みリソースとして構成する。理由：埋め込みリソースによりテンプレートがアセンブリにバンドルされ、全デプロイ環境で利用可能になるため。

```bash
dotnet add package Mjml.Net
```

`.csproj` に以下を追加:

```xml
<ItemGroup>
  <EmbeddedResource Include="Templates\**\*.mjml" />
</ItemGroup>
```

> **Values**: 基礎と型の追求（埋め込みリソースという「型」を最初に整え、環境に依存しないテンプレート配信を保証する）

### Step 2: Create the Layout Template

全メールが継承する共有レイアウト（ヘッダー、コンテンツスロット、フッター）を定義する。理由：集中レイアウトにより一貫したブランディングを保証し、テンプレートごとのボイラープレートを削減するため。

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

    <!-- コンテンツがここに注入される -->
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

MJML コンポーネントを使用してメールごとのコンテンツテンプレートを作成する。レイアウトテンプレートが自動的にラップする。理由：コンテンツテンプレートがメール固有のマークアップのみに集中し、小さく保守しやすくなるため。

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
  この招待は {{ExpirationDate}} に期限切れになります。
</mj-text>
```

> **Values**: 基礎と型の追求（コンテンツテンプレートをレイアウトから分離する「型」により、各メールの関心事を最小限に保つ）

### Step 4: Build the Template Renderer

埋め込み MJML テンプレートを読み込み、レイアウトにコンテンツを注入し、変数を置換して HTML にコンパイルするレンダラーを実装する。理由：レンダーパイプラインをインターフェースの背後にカプセル化することで、テストと DI 登録が可能になるため。

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

型安全な値オブジェクトを使用して、テンプレートレンダリングからメール作成を分離する。理由：コンポーザーが境界で型安全性を強制し、メール構築を自己文書化するため。

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

開発中にレンダリングされたメールをプレビューする管理者エンドポイントを作成する。理由：ビジュアルプレビューによりフィードバックループを短縮し、デプロイ前にレンダリングの問題を発見するため。

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

- ✅ MJML コンポーネント（`mj-section`、`mj-column`、`mj-text`）を生の HTML テーブルの代わりに使用する
- ✅ 環境間のファイルパス問題を避けるため、テンプレートを埋め込みリソースとして格納する
- ✅ 全メールで一貫したヘッダー、フッター、スタイリングのために共有レイアウトテンプレートを使用する
- ✅ コンポーザーメソッドシグネチャに型安全な値オブジェクト（`EmailAddress`、`PersonName`）を使用する
- ✅ 画像にはプロダクションの絶対 URL を使用する — 相対パスはメールクライアントで壊れる
- ✅ 管理者認証で保護された開発プレビューエンドポイントを追加する
- ✅ MJML コンパイルエラーを検証し、説明的なメッセージでスローする
- ✅ テンプレートをドメイン別（UserInvitations、PasswordReset、Billing）にサブディレクトリで整理する

## Common Pitfalls

1. **Raw HTML Tables in Templates** — MJML コンポーネントを使わずに手動でテーブルレイアウトを書く。修正：全レイアウトに `mj-section` と `mj-column` を使用する。
2. **Relative Image URLs** — メールクライアントで壊れる `/img/logo.png` を使用する。修正：`https://myapp.com/logo.png` のような絶対プロダクション URL を常に使用する。
3. **Unsanitized Variable Values** — エスケープなしでユーザー入力をテンプレートに直接注入する。修正：置換前に変数値を HTML エンコードする。
4. **Missing Error Handling on Compilation** — MJML コンパイルの `result.Errors` を無視する。修正：エラーをチェックし、説明的なメッセージでスローする。
5. **Hardcoded Site URLs** — テンプレートに環境固有の URL を埋め込む。修正：設定経由で変数として URL を渡す。

## Anti-Patterns

### ❌ Raw HTML Tables → ✅ Use MJML Components

```mjml
<!-- ❌ BAD — クライアント間で壊れる脆弱なテーブルレイアウト -->
<table><tr><td>Content</td></tr></table>

<!-- ✅ GOOD — MJML がクロスクライアントのテーブル生成を処理 -->
<mj-section>
  <mj-column>
    <mj-text>Content</mj-text>
  </mj-column>
</mj-section>
```

理由：MJML がテスト済みのインラインスタイル付きテーブル HTML にコンパイルし、全主要メールクライアントで動作するため。

### ❌ Raw String Parameters → ✅ Strongly-Typed Value Objects

```csharp
// ❌ BAD — バリデーションなし、パラメータの入れ替えが容易
Task<EmailMessage> ComposeAsync(string email, string name, string url);

// ✅ GOOD — 自己文書化、構築時にバリデーション
Task<EmailMessage> ComposeAsync(EmailAddress to, PersonName name, AbsoluteUri actionUrl);
```

理由：値オブジェクトが構築時に不変条件を強制し、パラメータ順序の間違いを防ぐため。

### ❌ Inline Styles in Templates → ✅ Use mj-attributes

```mjml
<!-- ❌ BAD — 全要素に繰り返されるインラインスタイル -->
<mj-text font-size="14px" color="#555" font-family="Arial">Text 1</mj-text>
<mj-text font-size="14px" color="#555" font-family="Arial">Text 2</mj-text>

<!-- ✅ GOOD — mj-head で集中管理されたデフォルト -->
<mj-attributes>
  <mj-text font-size="14px" color="#555555" font-family="Arial" />
</mj-attributes>
```

理由：集中属性により重複を削減し、グローバルスタイル変更を1行の編集で可能にするため。

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
| `<mj-section>` | 水平行コンテナ | `<mj-section background-color="#fff">` |
| `<mj-column>` | セクション内の垂直列 | `<mj-column width="50%">` |
| `<mj-text>` | スタイル付きテキストブロック | `<mj-text font-size="14px">Hello</mj-text>` |
| `<mj-button>` | コールトゥアクションボタン | `<mj-button href="{{Url}}">Click</mj-button>` |
| `<mj-image>` | レスポンシブ画像 | `<mj-image src="https://..." />` |
| `<mj-divider>` | 水平セパレーター | `<mj-divider border-color="#eee" />` |
| `<mj-spacer>` | 垂直スペーシング | `<mj-spacer height="20px" />` |

### Template Variable Convention

| Variable | Source | Example |
|----------|--------|---------|
| `{{SiteUrl}}` | Configuration | `https://myapp.com` |
| `{{PreviewText}}` | Composer | メールクライアントプレビューテキスト |
| `{{InviteeName}}` | Composer | 受信者の表示名 |
| `{{ActionUrl}}` | Composer | CTA ボタンのターゲット URL |
| `{{ExpirationDate}}` | Composer | フォーマット済み日付文字列 |

## Resources

- [MJML Documentation](https://documentation.mjml.io/) — 公式 MJML コンポーネントリファレンスとガイド
- [MJML Playground](https://mjml.io/try-it-live) — テンプレートプロトタイピング用ライブエディタ
- [Mjml.Net](https://github.com/ArtZab/Mjml.Net) — .NET MJML コンパイラライブラリ
- [Litmus](https://www.litmus.com/) — メールクライアントレンダリングプレビューとテスト
